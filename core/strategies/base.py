"""
Базовый класс для атомарных стратегий.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class StrategyBase(ABC):
    name: str = "BaseStrategy"

    def __init__(self, params: Dict[str, Any]):
        self.params = params

    @abstractmethod
    def generate_signal(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерирует торговый сигнал на основе рыночных данных."""
        pass