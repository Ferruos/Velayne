from aiogram import Bot, Dispatcher
from velayne.infra.config import settings
from velayne.infra.logger import setup_logging, logger
from .middlewares import LoggingMiddleware, SubscriptionStubMiddleware, RateLimitMiddleware, ExecTimeMiddleware
from . import user, admin

async def start_bot():
    setup_logging()
    if not settings.TG_TOKEN or not settings.TG_TOKEN.strip():
        logger.warning("TG_TOKEN не задан. Бот не будет запущен.")
        return
    logger.info("Запуск Telegram-бота...")
    bot = Bot(token=settings.TG_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(RateLimitMiddleware(limit=20, per_seconds=30))
    dp.message.middleware(ExecTimeMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.callback_query.middleware(ExecTimeMiddleware())
    dp.message.middleware(SubscriptionStubMiddleware())
    dp.callback_query.middleware(SubscriptionStubMiddleware())

    dp.include_router(user.router)
    dp.include_router(admin.router)

    await dp.start_polling(bot)