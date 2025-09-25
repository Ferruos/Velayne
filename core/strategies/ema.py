"""
Пример атомарной стратегии: EMA crossover.
"""
from .base import StrategyBase

class EMAStrategy(StrategyBase):
    name = "EMA"

    def generate_signal(self, market_data):
        prices = market_data["close"]
        fast = self.params.get("fast", 12)
        slow = self.params.get("slow", 26)
        ema_fast = sum(prices[-fast:]) / fast
        ema_slow = sum(prices[-slow:]) / slow

        if ema_fast > ema_slow:
            return {"action": "buy"}
        elif ema_fast < ema_slow:
            return {"action": "sell"}
        else:
            return {"action": "hold"}