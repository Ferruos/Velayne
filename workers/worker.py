import time
from dotenv import load_dotenv
from core.blend.blend_manager import BlendManager
from services.logging import get_logger
from core.portfolio import PortfolioManager

class Plan:
    max_order_size = 0.05
    max_balance = 100
    max_open_positions = 1

def get_market_data():
    import random
    base = 100
    return {"close": [base + random.uniform(-2, 2) for _ in range(30)]}

logger = get_logger("worker")

def main():
    load_dotenv()
    blend_manager = BlendManager()
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