from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from velayne.infra.config import settings
from velayne.bot.routers.user import router as user_router
from velayne.bot.routers.admin import router as admin_router

bot = Bot(
    token=settings.TG_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)

dp = Dispatcher()
dp.include_router(user_router)
dp.include_router(admin_router)

# ... далее запуск polling в стандартной точке входа ...