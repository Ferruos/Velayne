import random
from datetime import datetime

def market_tick(symbols):
    """Симулирует рыночные данные по символам"""
    # Для каждого symbol: генерируем OHLC + spread
    market = {}
    for sym in symbols:
        base = 100 + random.uniform(-5, 5)
        close = [base + random.gauss(0, 1) for _ in range(60)]
        high = [c + random.uniform(0, 2) for c in close]
        low = [c - random.uniform(0, 2) for c in close]
        spread = random.uniform(0.01, 0.2)
        market[sym] = {
            "close": close,
            "high": high,
            "low": low,
            "spread": spread,
            "atr": sum([h - l for h, l in zip(high, low)]) / len(high),
            "rsi": random.uniform(30, 70),
            "ema_short": sum(close[-8:]) / 8,
            "ema_long": sum(close[-21:]) / 21,
            "returns": [close[i] - close[i - 1] for i in range(1, len(close))],
        }
    return market

def exec_order(order, market):
    """
    Симулирует исполнение ордера с учетом комиссии, спреда, влияния и проскальзывания.
    order: dict{symbol, side, size}
    market: dict
    """
    symbol = order['symbol']
    side = order['action']  # 'buy' or 'sell'
    size = order['size']
    mkt = market[symbol]

    # Текущая цена bid/ask
    mid = mkt['close'][-1]
    spread = mkt['spread']
    # Реалистичный bid/ask:
    ask = mid + spread / 2
    bid = mid - spread / 2

    # Проскальзывание: зависит от размера
    slippage = abs(size) * random.uniform(0.01, 0.08)  # до 0.08% на крупный объем

    # Рыночное влияние: если size большой, увеличиваем slippage и комиссию
    impact = abs(size) * 0.05

    if side == 'buy':
        exec_price = ask + slippage + impact
    else:
        exec_price = bid - slippage - impact

    # Комиссия (0.05% стандарт, но больше при большом объеме)
    commission_rate = 0.0005 + 0.0002 * min(5, abs(size) / 0.1)
    fee = abs(size * exec_price) * commission_rate

    fill = {
        "dt": datetime.utcnow(),
        "symbol": symbol,
        "side": side,
        "price": exec_price,
        "size": size,
        "fee": fee,
        "meta": {
            "slippage": slippage,
            "impact": impact,
            "commission_rate": commission_rate,
            "spread": spread,
        }
    }
    return fill