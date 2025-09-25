"""
Пример атомарной стратегии: EMA crossover.
"""
from .base import StrategyBase

class EMAStrategy(StrategyBase):
    name = "EMA"
    # Теперь optimizer будет искать fast и slow в указанном диапазоне
    param_space = ["fast", "slow"]

    def generate_signal(self, market_data):
        prices = market_data["close"]
        fast = int(self.params.get("fast", 12))
        slow = int(self.params.get("slow", 26))
        if len(prices) < max(fast, slow):
            # недостаточно данных для расчёта — держим
            return {"action": "hold"}
        ema_fast = sum(prices[-fast:]) / fast
        ema_slow = sum(prices[-slow:]) / slow

        if ema_fast > ema_slow:
            return {"action": "buy"}
        elif ema_fast < ema_slow:
            return {"action": "sell"}
        return {"action": "hold"}
