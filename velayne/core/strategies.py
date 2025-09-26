import yaml
import operator
import time
from typing import Any, Dict, List, Optional

# === Индикаторы (safe, без сторонних библиотек) ===

def ema(series, period):
    alpha = 2 / (period + 1)
    ema_val = series[0]
    for price in series[1:]:
        ema_val = alpha * price + (1 - alpha) * ema_val
    return ema_val

def sma(series, period):
    if len(series) < period:
        return sum(series) / len(series)
    return sum(series[-period:]) / period

def rsi(series, period):
    if len(series) < period + 1:
        return 50
    gains = [max(0, series[i] - series[i-1]) for i in range(1, len(series))]
    losses = [max(0, series[i-1] - series[i]) for i in range(1, len(series))]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def atr(high, low, close, period):
    trs = []
    for i in range(1, len(close)):
        tr = max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))
        trs.append(tr)
    if not trs:
        return 1.0
    if len(trs) < period:
        return sum(trs) / len(trs)
    return sum(trs[-period:]) / period

def highest(series, n):
    return max(series[-n:]) if len(series) >= n else max(series)

def lowest(series, n):
    return min(series[-n:]) if len(series) >= n else min(series)

def ret(series, n):
    if len(series) < n + 1:
        return 0.0
    return (series[-1] - series[-1-n]) / series[-1-n]

# === StrategyBase ===

class StrategyBase:
    def __init__(self, code, name, params=None):
        self.code = code
        self.name = name
        self.params = params or {}

    def configure(self, **kwargs):
        self.params.update(kwargs)

    def generate_signal(self, market: Dict, portfolio: Dict) -> Optional[Dict]:
        raise NotImplementedError

    def on_fill(self, fill: Dict):
        pass

# === Реализации ===

class EmaCrossoverStrategy(StrategyBase):
    def __init__(self, symbol, short=12, long=26):
        super().__init__("ema_crossover", "EMA Crossover", {"short": short, "long": long, "symbol": symbol})
        self.last_signal = None

    def generate_signal(self, market, portfolio):
        symbol = self.params["symbol"]
        data = market[symbol]
        closes = data.get("close", [])
        if len(closes) < max(self.params["short"], self.params["long"]) + 1:
            return None
        ema_short = ema(closes, self.params["short"])
        ema_long = ema(closes, self.params["long"])
        prev_ema_short = ema(closes[:-1], self.params["short"])
        prev_ema_long = ema(closes[:-1], self.params["long"])
        if prev_ema_short < prev_ema_long and ema_short > ema_long:
            self.last_signal = "buy"
            return {"action": "buy", "symbol": symbol, "size": 0.01}
        if prev_ema_short > prev_ema_long and ema_short < ema_long:
            self.last_signal = "sell"
            return {"action": "sell", "symbol": symbol, "size": 0.01}
        return None

class MeanReversionStrategy(StrategyBase):
    def __init__(self, symbol, period=20, threshold=2):
        super().__init__("mean_reversion", "Mean Reversion", {"period": period, "threshold": threshold, "symbol": symbol})

    def generate_signal(self, market, portfolio):
        symbol = self.params["symbol"]
        data = market[symbol]
        closes = data.get("close", [])
        if len(closes) < self.params["period"]:
            return None
        mean = sma(closes, self.params["period"])
        std = (sum((x - mean) ** 2 for x in closes[-self.params["period"]:]) / self.params["period"]) ** 0.5
        z = (closes[-1] - mean) / std if std > 0 else 0
        if z > self.params["threshold"]:
            return {"action": "sell", "symbol": symbol, "size": 0.01}
        if z < -self.params["threshold"]:
            return {"action": "buy", "symbol": symbol, "size": 0.01}
        return None

class BreakoutStrategy(StrategyBase):
    def __init__(self, symbol, period=20):
        super().__init__("breakout", "Breakout", {"period": period, "symbol": symbol})

    def generate_signal(self, market, portfolio):
        symbol = self.params["symbol"]
        data = market[symbol]
        closes = data.get("close", [])
        if len(closes) < self.params["period"] + 1:
            return None
        high = max(closes[-self.params["period"]-1:-1])
        low = min(closes[-self.params["period"]-1:-1])
        if closes[-1] > high:
            return {"action": "buy", "symbol": symbol, "size": 0.01}
        if closes[-1] < low:
            return {"action": "sell", "symbol": symbol, "size": 0.01}
        return None

class GridStrategy(StrategyBase):
    def __init__(self, symbol, grid_size=0.005, base_size=0.01):
        super().__init__("grid", "Grid", {"grid_size": grid_size, "base_size": base_size, "symbol": symbol})
        self.reference = None

    def generate_signal(self, market, portfolio):
        symbol = self.params["symbol"]
        data = market[symbol]
        closes = data.get("close", [])
        if not closes:
            return None
        price = closes[-1]
        if self.reference is None:
            self.reference = price
        diff = (price - self.reference) / self.reference
        if diff > self.params["grid_size"]:
            self.reference = price
            return {"action": "sell", "symbol": symbol, "size": self.params["base_size"]}
        if diff < -self.params["grid_size"]:
            self.reference = price
            return {"action": "buy", "symbol": symbol, "size": self.params["base_size"]}
        return None

class MomentumStrategy(StrategyBase):
    def __init__(self, symbol, period=14):
        super().__init__("momentum", "Momentum", {"period": period, "symbol": symbol})

    def generate_signal(self, market, portfolio):
        symbol = self.params["symbol"]
        data = market[symbol]
        closes = data.get("close", [])
        if len(closes) < self.params["period"] + 1:
            return None
        momentum = closes[-1] - closes[-1 - self.params["period"]]
        if momentum > 0:
            return {"action": "buy", "symbol": symbol, "size": 0.01}
        elif momentum < 0:
            return {"action": "sell", "symbol": symbol, "size": 0.01}
        return None

class ScalpingStrategy(StrategyBase):
    def __init__(self, symbol):
        super().__init__("scalping", "Scalping", {"symbol": symbol})

    def generate_signal(self, market, portfolio):
        symbol = self.params["symbol"]
        data = market[symbol]
        spread = data.get("spread", 0.1)
        if spread < 0.05:
            return {"action": "buy", "symbol": symbol, "size": 0.01}
        elif spread > 0.2:
            return {"action": "sell", "symbol": symbol, "size": 0.01}
        return None

class ArbitrageStrategy(StrategyBase):
    def __init__(self, symbol, ref_price=100):
        super().__init__("arbitrage", "Arbitrage", {"symbol": symbol, "ref_price": ref_price})

    def generate_signal(self, market, portfolio):
        symbol = self.params["symbol"]
        data = market[symbol]
        price = data.get("close", [self.params["ref_price"]])[-1]
        if price > self.params["ref_price"] * 1.01:
            return {"action": "sell", "symbol": symbol, "size": 0.01}
        elif price < self.params["ref_price"] * 0.99:
            return {"action": "buy", "symbol": symbol, "size": 0.01}
        return None

# --- Event-based strategy: реагирует на NLP-теги новостей ---
class EventBasedStrategy(StrategyBase):
    def __init__(self, symbol, event_tags = ("listing","partnership"), hard_stop_atr=3):
        super().__init__("event_based", "EventBased", {"symbol": symbol, "event_tags": event_tags, "hard_stop_atr": hard_stop_atr})
        self.active_event = None

    def generate_signal(self, market, portfolio, news_meta=None):
        # news_meta: dict с тегами из News Guard (например, {'tags': {'listing': 1}})
        event_tags = self.params.get("event_tags", [])
        found_tags = []
        if news_meta and "tags" in news_meta:
            tags = news_meta["tags"]
            for t in event_tags:
                if t in tags:
                    found_tags.append(t)
        if not found_tags:
            return None
        symbol = self.params["symbol"]
        data = market[symbol]
        closes = data.get("close", [])
        atr_val = data.get('atr', 1.0)
        size = 0.02
        stop_loss = atr_val * self.params.get("hard_stop_atr", 3)
        # Можно реализовать направление входа по типу события, но базово — всегда BUY
        return {
            "action": "buy",
            "symbol": symbol,
            "size": size,
            "sl": stop_loss,
            "meta": {"event_tags": found_tags}
        }

# === REGISTRY and plan ===

REGISTRY = {
    "ema_crossover": EmaCrossoverStrategy,
    "mean_reversion": MeanReversionStrategy,
    "breakout": BreakoutStrategy,
    "grid": GridStrategy,
    "momentum": MomentumStrategy,
    "scalping": ScalpingStrategy,
    "arbitrage": ArbitrageStrategy,
    "event_based": EventBasedStrategy,
}

def enabled_for_plan(plan):
    if plan == "pro":
        return list(REGISTRY.keys())
    elif plan == "basic":
        return ["ema_crossover", "mean_reversion", "breakout", "momentum"]
    else:
        return ["ema_crossover", "mean_reversion"]

SAFE_OPS = {
    "AND": all,
    "OR": any,
    "NOT": lambda args: not args[0],
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}

SAFE_FUNCS = {
    "EMA": ema,
    "SMA": sma,
    "RSI": rsi,
    "ATR": atr,
    "HIGH": highest,
    "LOW": lowest,
    "RET": ret,
    "CROSSOVER": lambda a, b: a > b,  # simplified
}

def _eval_expr(expr, ctx, depth=0, depth_limit=5, start_time=None, time_limit=0.2):
    if depth > depth_limit:
        raise Exception("DSL: depth limit exceeded")
    if start_time and (time.time() - start_time > time_limit):
        raise Exception("DSL: time limit exceeded")
    if isinstance(expr, (int, float)):
        return expr
    if isinstance(expr, str):
        if expr in ctx:
            return ctx[expr]
        try:
            return float(expr)
        except Exception:
            return expr
    if isinstance(expr, list):
        return [_eval_expr(e, ctx, depth+1, depth_limit, start_time, time_limit) for e in expr]
    if isinstance(expr, dict):
        for k, v in expr.items():
            keyu = k.upper()
            if keyu in SAFE_OPS:
                args = [_eval_expr(arg, ctx, depth+1, depth_limit, start_time, time_limit) for arg in v]
                return SAFE_OPS[keyu](args)
            elif keyu in SAFE_FUNCS:
                if isinstance(v, list):
                    args = [_eval_expr(arg, ctx, depth+1, depth_limit, start_time, time_limit) for arg in v]
                    return SAFE_FUNCS[keyu](*args)
                elif isinstance(v, dict):
                    args = []
                    kwargs = {}
                    for ak, av in v.items():
                        if ak == "series":
                            args.append(_eval_expr(av, ctx, depth+1, depth_limit, start_time, time_limit))
                        else:
                            kwargs[ak] = _eval_expr(av, ctx, depth+1, depth_limit, start_time, time_limit)
                    return SAFE_FUNCS[keyu](*(args or [ctx.get("close", [])]), **kwargs)
                else:
                    return SAFE_FUNCS[keyu](v)
            else:
                raise Exception(f"DSL: unknown func/op {k}")
    raise Exception("DSL: invalid expr")

class DSLStrategy(StrategyBase):
    def __init__(self, code, name, dsl_text, dsl_dict):
        super().__init__(code, name)
        self.dsl_text = dsl_text
        self.dsl = dsl_dict
        self._parsed = None

    def _parse_if(self, expr):
        if isinstance(expr, list):
            return [self._parse_if(e) for e in expr]
        if isinstance(expr, dict):
            out = {}
            for k, v in expr.items():
                out[k] = self._parse_if(v)
            return out
        return expr

    def generate_signal(self, market, portfolio):
        symbol = list(market.keys())[0]
        ctx = dict(
            close=market[symbol].get("close", []),
            high=market[symbol].get("high", []),
            low=market[symbol].get("low", []),
        )
        expr = self.dsl.get("if")
        start = time.time()
        try:
            if isinstance(expr, str):
                return None
            parsed_if = self._parse_if(expr)
            cond = _eval_expr(parsed_if, ctx, depth=0, depth_limit=5, start_time=start, time_limit=0.2)
            if cond:
                then = self.dsl.get("then")
                if isinstance(then, str):
                    parts = then.split()
                    action = parts[0].lower()
                    size = 0.01
                    for p in parts[1:]:
                        if p.startswith("size="):
                            size = float(p.split("=")[-1])
                    return {"action": action, "symbol": symbol, "size": size}
                elif isinstance(then, dict):
                    d = dict(then)
                    d.setdefault("symbol", symbol)
                    return d
        except Exception as ex:
            return None
        return None

def parse_strategy_dsl(dsl_text: str) -> StrategyBase:
    d = yaml.safe_load(dsl_text)
    name = d.get("name", "CustomDSL")
    code = d.get("code", name.lower().replace(" ", "_"))
    return DSLStrategy(code, name, dsl_text, d)

def build_strategy_from_published(p) -> StrategyBase:
    return parse_strategy_dsl(p.dsl_text)