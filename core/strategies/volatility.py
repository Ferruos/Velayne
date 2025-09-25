from .base import StrategyBase

class VolatilityStrategy(StrategyBase):
    name = "Volatility"
    param_space = ["window", "threshold"]

    def generate_signal(self, market_data):
        prices = market_data["close"]
        window = int(self.params.get("window", 14))
        threshold = float(self.params.get("threshold", 0.025))
        import numpy as np
        returns = np.diff(prices[-window:]) / prices[-window:-1]
        vol = np.std(returns)
        if vol > threshold:
            return {"action": "buy"}
        elif vol < threshold / 2:
            return {"action": "sell"}
        return {"action": "hold"}