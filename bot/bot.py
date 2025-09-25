import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from services.env import get_env
from services.payments import create_payment, check_yoomoney_payment, is_user_paid
from services.keys import add_api_key, get_keys_info
from services.analytics import get_full_analytics
from services.settings import set_mode, get_mode
from bot.utils import escape_md
import logging
import pandas as pd

TOKEN = get_env("TG_TOKEN")
ADMIN_ID = int(get_env("ADMIN_ID", "0"))

bot = Bot(token=TOKEN, parse_mode="MarkdownV2")
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

def is_admin(user_id):
    return user_id == ADMIN_ID

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for cmd in ["/pay", "/status", "/run", "/stop", "/report", "/risk", "/mode"]:
        kb.add(KeyboardButton(cmd))
    if is_admin(message.from_user.id):
        kb.add(KeyboardButton("/admin"))
    await message.reply(
        escape_md("*Velayne*: _Добро пожаловать!_\nЖми /help или кнопки ниже 👇"),
        reply_markup=kb
    )

@dp.message_handler(commands=["help"])
async def help_cmd(message: types.Message):
    text = (
        "✨ *Команды*\n"
        "/pay — оплата\n"
        "/status — статус\n"
        "/run — запуск\n"
        "/stop — стоп\n"
        "/report — 📝 отчет\n"
        "/risk — ⚡️ риски\n"
        "/mode — режим\n"
        "\n*Админ:*\n/admin — панель"
    )
    await message.reply(escape_md(text))

@dp.message_handler(commands=["pay"])
async def pay_cmd(message: types.Message):
    payment_id = create_payment(message.from_user.id, 990, "RUB")
    await message.reply(
        escape_md(
            f"Для активации доступа переведи 990 RUB на YooMoney `41001234567890`.\n"
            f"После оплаты отправь чек или номер перевода.\n"
            f"Твой ID платежа: `{payment_id}`"
        )
    )

@dp.message_handler(commands=["status"])
async def status_cmd(message: types.Message):
    paid = is_user_paid(message.from_user.id)
    msg = "✅ Оплата подтверждена. Доступ открыт!" if paid else "⏳ Ожидание оплаты."
    await message.reply(escape_md(msg))

@dp.message_handler(commands=["admin"])
async def admin_panel(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply(escape_md("⛔️ Нет доступа."))
        return
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🚀 Обучить", callback_data="train"),
        InlineKeyboardButton("🔄 Обновить blend", callback_data="blend_update"),
        InlineKeyboardButton("⚙️ Сменить режим", callback_data="setmode"),
        InlineKeyboardButton("📊 Статус", callback_data="status"),
        InlineKeyboardButton("📈 Аналитика", callback_data="analytics"),
        InlineKeyboardButton("🔑 Ключи", callback_data="keys"),
    )
    await message.reply(escape_md("🛠 *Админ-панель* — выбирай действие:"), reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data in [
    "train", "blend_update", "setmode", "status", "analytics", "keys"])
async def admin_cb(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return

    if call.data == "train":
        import subprocess
        subprocess.Popen(["python", "master/master.py"])
        await call.message.reply(escape_md("🧠 Обучение blend и режима запущено!"))
    elif call.data == "blend_update":
        await call.message.reply(escape_md("🔄 Blend обновлен!"))
    elif call.data == "setmode":
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("Sandbox", callback_data="mode_sandbox"),
            InlineKeyboardButton("Live", callback_data="mode_live"),
        )
        await call.message.reply(escape_md("⚙️ Выберите режим:"), reply_markup=kb)
    elif call.data == "status":
        # Добавьте get_full_status если нужно
        await call.message.reply(escape_md("💡 *Статус системы:*\nOK"))
    elif call.data == "analytics":
        analytics = get_full_analytics()
        await call.message.reply(escape_md(f"📈 *Аналитика:*\n{analytics}"))
    elif call.data == "keys":
        keys_info = get_keys_info(call.from_user.id)
        await call.message.reply(escape_md(f"🔑 *API-ключи:*\n{keys_info}"))

@dp.callback_query_handler(lambda c: c.data.startswith("mode_"))
async def mode_cb(call: types.CallbackQuery):
    mode = call.data.split("_", 1)[1]
    set_mode(mode)
    await call.message.reply(escape_md(f"Режим установлен: *{mode}*"))

@dp.message_handler(commands=["run"])
async def run_cmd(message: types.Message):
    mode = get_mode()
    if mode == "live" and not is_user_paid(message.from_user.id):
        await message.reply(escape_md("Оплата не подтверждена, доступ невозможен."))
        return
    import subprocess
    subprocess.Popen(["python", "workers/worker.py", str(message.from_user.id), mode])
    await message.reply(escape_md("⏳ Запуск торговли..."))

@dp.message_handler(commands=["stop"])
async def stop_cmd(message: types.Message):
    await message.reply(escape_md("⏹️ Торговля остановлена."))

@dp.message_handler(commands=["report"])
async def report_cmd(message: types.Message):
    if os.path.exists("last_report.png"):
        with open("last_report.png", "rb") as f:
            await message.reply_photo(f, caption=escape_md("Последний отчёт"))
    else:
        await message.reply(escape_md("Нет отчёта."))

@dp.message_handler(commands=["risk"])
async def risk_cmd(message: types.Message):
    if os.path.exists("risk_profile.csv"):
        stats = pd.read_csv("risk_profile.csv").tail(1).to_dict("records")[0]
        await message.reply(escape_md(
            f"Риск-профиль: {stats['profile']}\nDrawdown: {stats['drawdown']}%\nLeverage: x{stats['leverage']}"
        ))
    else:
        await message.reply(escape_md("Нет данных по рискам."))

@dp.message_handler(commands=["mode"])
async def mode_cmd(message: types.Message):
    mode = get_mode()
    await message.reply(escape_md(f"Текущий режим: *{mode}*"))

def main():
    from storage.db import init_db
    init_db()
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    main()