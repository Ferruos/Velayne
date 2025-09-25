import os
import time
from dotenv import load_dotenv
from core.blend.blend_manager import BlendManager
from core.portfolio import PortfolioManager
from core.execution import Executor
from services.exchange import ExchangeAdapter
from services.logging import get_logger

# Параметры риск‑плана — можете скорректировать под себя
class Plan:
    max_order_size = 0.05    # максимально 5% депозита на один ордер
    max_balance = 100        # условный баланс (для stop_loss и trailing)
    max_open_positions = 1   # не более одной позиции одновременно

logger = get_logger("worker")

def main():
    load_dotenv()
    # Инициализируем биржу
    name = os.getenv("EXCHANGE_NAME", "bybit").lower()
    api_key = os.getenv("EXCHANGE_API_KEY", "")
    api_secret = os.getenv("EXCHANGE_API_SECRET", "")
    is_live = os.getenv("EXCHANGE_IS_LIVE", "false").lower() in ("true", "1", "yes")
    exchange = ExchangeAdapter(name=name, api_key=api_key, api_secret=api_secret, testnet=not is_live)

    blend_manager = BlendManager()
    plan = Plan()
    portfolio = PortfolioManager(blend_manager, plan)
    executor = Executor(exchange, portfolio)

    symbol = os.getenv("SYMBOL", "BTC/USDT")
    timeframe = os.getenv("TIMEFRAME", "1h")
    limit = int(os.getenv("HIST_LIMIT", "60"))

    logger.info("Воркер: слушаю blend и торгую на песочнице…")
    while True:
        try:
            market_data = exchange.get_historical_data(symbol, timeframe=timeframe, limit=limit)
            order = portfolio.aggregate_signals("demo_user", market_data)
            logger.info(f"Сигнал: {order}")
            # Отправляем ордер сразу через Executor
            executor.execute_order(symbol, order)
            time.sleep(5)  # пауза между запросами
        except Exception as e:
            logger.error(f"Ошибка воркера: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
