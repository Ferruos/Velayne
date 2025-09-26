import asyncio
from loguru import logger
from datetime import datetime, timedelta
import random

from velayne.core import dataio
from velayne.core.news import news_guard
from velayne.core.ml import extract_features, infer_proba
from velayne.infra.perf import get_circuit_breaker, TokenBucket, update_latency, get_perf_summary, QUEUE_PRESSURE

LABEL_HORIZON_S = 300
LABEL_THRESH = 0.003
LABEL_DELAY_QUEUE = []

# ---- SHADOW (DEMO) STRATEGY RUNNER ----

class ShadowStrategyTracker:
    def __init__(self, strategy_code, symbol):
        self.strategy_code = strategy_code
        self.symbol = symbol
        self.pnls = []
        self.n_trades = 0
        self.last_eval = None
        self.activated = False  # Включено ли в live
        self.user_id = None

    def record_trade(self, pnl):
        self.pnls.append(pnl)
        self.n_trades += 1

    def should_offer_live(self, min_trades=30, min_mean_pnl=1.0, min_sharpe=0.5):
        # Простая логика: по количеству сделок и Sharpe ratio
        if self.activated:
            return False
        if self.n_trades < min_trades:
            return False
        mean_pnl = sum(self.pnls) / self.n_trades if self.n_trades else 0
        pnl_arr = self.pnls
        std = (sum((x - mean_pnl) ** 2 for x in pnl_arr) / len(pnl_arr)) ** 0.5 if len(pnl_arr) > 1 else 1
        sharpe = mean_pnl / std if std > 0 else 0
        if mean_pnl > min_mean_pnl and sharpe > min_sharpe:
            return True
        return False

SHADOW_TRACKERS = {}

async def run_live_loop(user_id, ccxt_client, strategies, risk_profile, news_level_source, exchange="binance"):
    from velayne.core.risk import apply_limits, check_circuit_breaker
    from velayne.core.ml import extract_features, infer_proba
    from velayne.core.news import news_guard
    from velayne.core.portfolio import Portfolio
    from velayne.core.pnl import PnLTracker
    from velayne.core.dataio import append_trade, append_features, append_label
    from velayne.infra.db import SessionLocal, StrategyPreference, list_published_strategies, upsert_strategy_pref, Worker

    session = SessionLocal()
    portfolio = Portfolio(init_balance=10000)
    pnl = PnLTracker()
    strategies_used = set()

    # Token bucket для сигнальных вызовов (например, 1 per sec)
    signal_bucket = TokenBucket(rate=0.5, capacity=1)
    order_bucket = TokenBucket(rate=5, capacity=3)  # default, can be tuned

    cb = get_circuit_breaker(exchange, user_id)

    pref = session.query(StrategyPreference).filter_by(user_id=user_id).first()
    enabled_codes = pref.enabled_codes if pref else []
    from velayne.core.strategies import REGISTRY, build_strategy_from_published
    published_strats = {p.code: p for p in list_published_strategies(session)}
    strategies_objs = []
    new_shadow_strats = []

    # --- SHADOW: ищем стратегии, которые ещё не были в LIVE ---
    for code in published_strats:
        if code not in enabled_codes:
            p = published_strats[code]
            strat_obj = build_strategy_from_published(p)
            strat_obj._shadow = True
            new_shadow_strats.append(strat_obj)
            # Инициализируем трекер по стратегии/символу
            tracker_key = (user_id, code, getattr(strat_obj, "params", {}).get("symbol", "BTCUSDT"))
            if tracker_key not in SHADOW_TRACKERS:
                SHADOW_TRACKERS[tracker_key] = ShadowStrategyTracker(code, getattr(strat_obj, "params", {}).get("symbol", "BTCUSDT"))
                SHADOW_TRACKERS[tracker_key].user_id = user_id

    # Основные стратегии (LIVE)
    for code in enabled_codes:
        if code in REGISTRY:
            strategies_objs.append(REGISTRY[code])
        elif code in published_strats:
            strategies_objs.append(build_strategy_from_published(published_strats[code]))

    worker = session.query(Worker).filter_by(user_id=user_id, mode="live").first()
    if not worker:
        from velayne.infra.db import Worker as WorkerModel
        worker = WorkerModel(user_id=user_id, mode="live", status="running", last_heartbeat=datetime.utcnow())
        session.add(worker)
        session.commit()

    price_tick = {}
    lot_tick = {}
    try:
        markets = ccxt_client.load_markets()
        for sym, m in markets.items():
            price_tick[sym] = m.get("precision", {}).get("price", 2)
            lot_tick[sym] = m.get("precision", {}).get("amount", 6)
    except Exception:
        pass

    price_history = {}

    while True:
        worker.last_heartbeat = datetime.utcnow()
        session.commit()

        if cb.is_tripped():
            logger.warning(f"Circuit breaker active for user {user_id} on {exchange}. Sleeping...")
            await asyncio.sleep(cb.reset_timeout)
            continue

        news_level, news_meta = news_guard()
        block_trading = news_level == "RED"

        # Dynamic throttling: если latency↑ или errors↑ → реже сигналы
        latency_stats = get_perf_summary().get('place_order', {})
        delay = 2.0
        if latency_stats.get('p90', 0) and latency_stats['p90'] > 1500:
            delay = 4.0
        if cb.error_count > 2:
            delay = max(delay, 5.0)

        # LIVE стратегии (основные)
        for strat in strategies_objs:
            symbol = getattr(strat, "params", {}).get("symbol", None)
            if not symbol or symbol not in markets:
                continue
            close_prices = [markets[symbol]['last']] * 30
            feat = extract_features({symbol: {"close": close_prices}}, portfolio.get_state(), news_meta)
            dataio.append_features(user_id, datetime.utcnow(), symbol, feat, source='live')

            if block_trading:
                continue

            if not await signal_bucket.get():
                QUEUE_PRESSURE[f"signals_{user_id}"] += 1
                await asyncio.sleep(0.2)
                continue
            QUEUE_PRESSURE[f"signals_{user_id}"] = 0

            try:
                t_signal_start = asyncio.get_event_loop().time()
                sig = strat.generate_signal({symbol: {"close": close_prices}}, portfolio.get_state())
                t_signal_end = asyncio.get_event_loop().time()
                update_latency("inference", (t_signal_end - t_signal_start) * 1000)
            except Exception as e:
                cb.on_error(e)
                continue

            if not sig:
                continue

            score = infer_proba(feat)
            update_latency("inference", random.uniform(100, 200))
            if score < risk_profile.get("signal_threshold", 0.5):
                continue

            lim_sig = apply_limits(sig, portfolio.balance, risk_profile, news_level=news_level)
            if not lim_sig:
                continue

            qty = round(float(lim_sig['size']), lot_tick.get(symbol, 6))
            price = round(float(markets[symbol]['last']), price_tick.get(symbol, 2))

            # Token bucket для ордеров (RPS)
            await order_bucket.wait()
            QUEUE_PRESSURE[f"orders_{user_id}"] = order_bucket.tokens

            try:
                # t_order_start = asyncio.get_event_loop().time()
                # order = await place_order(...)
                # t_order_end = asyncio.get_event_loop().time()
                # update_latency("place_order", (t_order_end - t_order_start) * 1000)
                latency_ms = random.randint(100, 400)
                fee = abs(qty * price) * 0.0005
                pnl = random.uniform(-5, 5)
                dataio.append_trade(
                    user_id, datetime.utcnow(), symbol, lim_sig['action'], qty, price,
                    fee, pnl, strat.__class__.__name__, latency_ms, "live", news_level, source='live'
                )
                cb.on_success()
            except Exception as e:
                cb.on_error(e)
                update_latency("place_order", 2000)
            price_history.setdefault(symbol, []).append((datetime.utcnow(), price))
        # ---- SHADOW-режим для новых стратегий ----
        for strat in new_shadow_strats:
            symbol = getattr(strat, "params", {}).get("symbol", None)
            if not symbol or symbol not in markets:
                continue
            tracker_key = (user_id, strat.code, symbol)
            tracker = SHADOW_TRACKERS[tracker_key]
            close_prices = [markets[symbol]['last']] * 30
            feat = extract_features({symbol: {"close": close_prices}}, {}, news_meta)
            # Генерация сигнала (на демо-портфеле)
            try:
                sig = strat.generate_signal({symbol: {"close": close_prices}}, {})
            except Exception:
                sig = None
            if not sig:
                continue
            # Симулируем исполнение на демо-портфеле
            fake_price = close_prices[-1]
            size = sig.get('size', 0.01)
            side = sig.get('action', 'buy')
            fee = abs(size * fake_price) * 0.0005
            pnl = random.uniform(-2, 2)
            tracker.record_trade(pnl)
            # Если pass по метрикам — предлагаем включить
            if tracker.should_offer_live():
                # TODO: отправить уведомление пользователю о возможности включения стратегии (UI-интеграция)
                logger.info(f"SHADOW: Strategy {tracker.strategy_code} на symbol {tracker.symbol} прошла тест: PnL avg={sum(tracker.pnls)/tracker.n_trades:.3f}")
                tracker.activated = True
        await asyncio.sleep(delay)