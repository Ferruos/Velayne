from .base import StrategyBase

class ScalpStrategy(StrategyBase):
    name = "Scalp"
    param_space = ["window"]

    def generate_signal(self, market_data):
        prices = market_data["close"]
        window = int(self.params.get("window", 5))
        # Scalp: открываемся на каждом небольшом отклонении от последнего среднего
        avg = sum(prices[-window:]) / window
        if prices[-1] < avg * 0.998:
            return {"action": "buy"}
        elif prices[-1] > avg * 1.002:
            return {"action": "sell"}
        return {"action": "hold"}