import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from services.logging import get_logger

load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logger = get_logger("tg")

# Импортируем все хендлеры (оферта, pay, demo, стратегии, etc)
from bot.handlers import register_handlers
from bot.handlers_payment import *
from bot.handlers_strategies import *
from bot.handlers_demo import *

register_handlers(dp)

@dp.errors_handler()
async def handle_errors(update, exception):
    logger.error(f"Telegram bot error: {exception}")
    return True

if __name__ == "__main__":
    logger.info("Запуск Telegram-бота...")
    executor.start_polling(dp, skip_updates=True)