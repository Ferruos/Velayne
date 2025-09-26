from aiogram import Router, F
from aiogram.types import Message
from velayne.infra.config import settings
from velayne.bot.texts_ru import WELCOME, HELP
from velayne.bot.ui import main_reply_menu

router = Router(name="user")

@router.message(F.text == "/start")
async def start_handler(msg: Message):
    is_admin = str(msg.from_user.id) == str(settings.ADMIN_ID)
    await msg.answer(
        WELCOME,
        reply_markup=main_reply_menu(is_admin)
    )

@router.message(F.text == "/help")
async def help_handler(msg: Message):
    is_admin = str(msg.from_user.id) == str(settings.ADMIN_ID)
    await msg.answer(
        HELP,
        reply_markup=main_reply_menu(is_admin)
    )

@router.message(F.text == "ℹ️ Справка")
async def help_btn(msg: Message):
    is_admin = str(msg.from_user.id) == str(settings.ADMIN_ID)
    await msg.answer(
        HELP,
        reply_markup=main_reply_menu(is_admin)
    )

@router.message(F.text == "🧪 Режим: Sandbox")
@router.message(F.text == "🧪 Режим: Live")
async def mode_status(msg: Message):
    mode = settings.SERVICE_MODE
    await msg.answer(f"🧪 Текущий режим: <b>{mode}</b>")

@router.message(F.text == "⚙️ Настройки")
async def settings_btn(msg: Message):
    await msg.answer("⚙️ Раздел настроек (скоро будет доступен).")

@router.message(F.text == "📊 Портфель")
async def portfolio_btn(msg: Message):
    await msg.answer("📊 Раздел портфеля (статистика и сделки — скоро).")

@router.message(F.text == "🧾 Подписка")
async def subs_btn(msg: Message):
    await msg.answer("🧾 Статус подписки и оплата — скоро.")

@router.message()
async def fallback(msg: Message):
    await msg.answer("Команда не распознана. Нажмите /help или используйте меню.")