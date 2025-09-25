from .base import StrategyBase

class BreakoutStrategy(StrategyBase):
    name = "Breakout"
    param_space = ["window"]

    def generate_signal(self, market_data):
        prices = market_data["close"]
        window = int(self.params.get("window", 20))
        high = max(prices[-window:])
        low = min(prices[-window:])
        last = prices[-1]
        if last >= high:
            return {"action": "buy"}
        elif last <= low:
            return {"action": "sell"}
        return {"action": "hold"}