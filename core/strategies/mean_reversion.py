from .base import StrategyBase

class MeanReversionStrategy(StrategyBase):
    name = "MeanReversion"
    param_space = ["window", "threshold"]

    def generate_signal(self, market_data):
        prices = market_data["close"]
        window = int(self.params.get("window", 10))
        threshold = float(self.params.get("threshold", 0.02))
        mean = sum(prices[-window:]) / window
        last = prices[-1]
        deviation = (last - mean) / mean
        if deviation < -threshold:
            return {"action": "buy"}
        elif deviation > threshold:
            return {"action": "sell"}
        else:
            return {"action": "hold"}