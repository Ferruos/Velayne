"""
Main entry point for training and publishing blends.

Этот скрипт загружает исторические данные через ExchangeAdapter,
оптимизирует веса и параметры стратегий при помощи Optuna,
и публикует результат через BlendManager. Все настройки берутся из .env.
"""

import os
import sys
from typing import List, Dict, Any

# Загружаем .env; если python-dotenv не установлен, определяем заглушку
default_env_loaded = False
try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    def load_dotenv(*args, **kwargs):
        return None
else:
    default_env_loaded = True

# Добавляем корень проекта в sys.path, чтобы модули 'core' импортировались корректно
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from core.blend.blend_manager import BlendManager
from ml.blend_optimizer import optimize_blend
from core.strategies import STRATEGY_CLASSES
from services.logging import get_logger
from services.exchange import ExchangeAdapter

logger = get_logger("master")


def get_historical_data(symbol: str = "BTC/USDT", timeframe: str = "1h",
                        limit: int = 500) -> List[Dict[str, Any]]:
    """
    Загружает исторические свечи через ExchangeAdapter.
    Биржа, ключи и режим тест/лайв берутся из .env:
      EXCHANGE_NAME, EXCHANGE_API_KEY, EXCHANGE_API_SECRET, EXCHANGE_IS_LIVE.

    :param symbol: Тикер, например 'BTC/USDT'
    :param timeframe: Интервал свечей, например '1h'
    :param limit: Количество свечей
    :return: список с одним словарём {'close': [prices...]}
    """
    name = os.getenv("EXCHANGE_NAME", "bybit").lower()
    api_key = os.getenv("EXCHANGE_API_KEY", "")
    api_secret = os.getenv("EXCHANGE_API_SECRET", "")
    is_live = os.getenv("EXCHANGE_IS_LIVE", "false").lower() in ("true", "1", "yes")
    adapter = ExchangeAdapter(name=name, api_key=api_key, api_secret=api_secret, testnet=not is_live)
    data = adapter.get_historical_data(symbol=symbol, timeframe=timeframe, limit=limit)
    return [data]


def main() -> None:
    """
    Загружает .env, тянет данные, оптимизирует бленд и публикует его.
    """
    # Загружаем переменные окружения из .env
    load_dotenv()
    blend_manager = BlendManager()
    historical_data = get_historical_data()
    try:
        # 100 попыток, чтобы по-настоящему обучиться на реальных данных
        result = optimize_blend(historical_data, STRATEGY_CLASSES, n_trials=100)
        blend = {
            "version": None,
            "components": result["components"],
            "metrics": result["metrics"],
            "regime": "trend",
        }
        blend_manager.publish_blend(blend)
        logger.info(f"Blend published: {blend}")
    except Exception as e:
        logger.error(f"Ошибка master/main: {e}")


if __name__ == "__main__":
    main()
