from .base import StrategyBase

class MarketMakingStrategy(StrategyBase):
    name = "MarketMaking"
    param_space = ["spread"]

    def generate_signal(self, market_data):
        # Лёгкий маркет-мейкинг: всегда лимитки buy и sell вокруг цены
        # Для демо возвращаем оба направления (реализация зависит от ядра)
        spread = float(self.params.get("spread", 0.001))
        last = market_data["close"][-1]
        return {"action": "both", "buy_price": last * (1 - spread), "sell_price": last * (1 + spread)}