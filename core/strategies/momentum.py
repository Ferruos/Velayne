from .base import StrategyBase

class MomentumStrategy(StrategyBase):
    name = "Momentum"
    param_space = ["lookback", "threshold"]

    def generate_signal(self, market_data):
        prices = market_data["close"]
        lookback = int(self.params.get("lookback", 10))
        threshold = float(self.params.get("threshold", 0.01))
        change = (prices[-1] - prices[-lookback]) / prices[-lookback]
        if change > threshold:
            return {"action": "buy"}
        elif change < -threshold:
            return {"action": "sell"}
        return {"action": "hold"}