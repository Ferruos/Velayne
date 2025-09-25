import os
import time
from dotenv import load_dotenv
from core.blend.blend_manager import BlendManager
from core.portfolio import PortfolioManager
from services.logging import get_logger

logger = get_logger("worker")

class Plan:
    max_order_size = 0.05
    max_balance = 100
    max_open_positions = 1

def get_market_data():
    import random
    base = 100
    return {"close": [base + random.uniform(-2, 2) for _ in range(30)]}

def main():
    load_dotenv()
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    blend_manager = BlendManager(redis_url)
    plan = Plan()
    portfolio = PortfolioManager(blend_manager, plan)
    logger.info("Воркер: ожидаю blend и эмулирую торговлю...")
    while True:
        try:
            market_data = get_market_data()
            order = portfolio.aggregate_signals("demo_user", market_data)
            logger.info(f"Эмуляция ордера: {order}")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Ошибка воркера: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()