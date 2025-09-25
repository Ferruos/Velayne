import os
from dotenv import load_dotenv
from core.blend.blend_manager import BlendManager
from ml.blend_optimizer import optimize_blend
from core.strategies import STRATEGY_CLASSES
from services.logging import get_logger

logger = get_logger("master")

def get_historical_data():
    return [{"close": [100 + i + j for i in range(30)]} for j in range(5)]

def main():
    load_dotenv()
    blend_manager = BlendManager()  # Без redis_url
    historical_data = get_historical_data()
    try:
        result = optimize_blend(historical_data, STRATEGY_CLASSES, n_trials=4)
        blend = {
            "version": None,
            "components": result["components"],
            "metrics": result["metrics"],
            "regime": "trend"
        }
        blend_manager.publish_blend(blend)
        logger.info(f"Blend published: {blend}")
    except Exception as e:
        logger.error(f"Ошибка master/main: {e}")

if __name__ == "__main__":
    main()