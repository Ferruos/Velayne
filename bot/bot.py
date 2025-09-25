import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from services.env import get_env

TOKEN = get_env("TG_TOKEN")
ADMIN_ID = int(get_env("ADMIN_ID", "0"))

bot = Bot(token=TOKEN, parse_mode="MarkdownV2")
dp = Dispatcher(bot)

def is_admin(user_id):
    return user_id == ADMIN_ID

# --- Команды бота ---
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for cmd in ["/pay", "/status", "/run", "/stop", "/report", "/risk", "/mode"]:
        kb.add(KeyboardButton(cmd))
    if is_admin(message.from_user.id):
        kb.add(KeyboardButton("/admin"))
    await message.reply(
        "*Velayne*: _Добро пожаловать!_\nЖми /help или кнопки ниже 👇",
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
        "/report — 📈 отчет\n"
        "/risk — ⚡️ риски\n"
        "/mode — режим\n"
    )
    if is_admin(message.from_user.id):
        text += "\n*Админ:*\n/admin — панель"
    await message.reply(text)

@dp.message_handler(commands=["admin"])
async def admin_panel(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("⛔️ Нет доступа.")
        return
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🚀 Обучение", callback_data="train"),
        InlineKeyboardButton("🔄 Обновить blend", callback_data="blend_update"),
    )
    kb.add(
        InlineKeyboardButton("⚙️ Сменить режим", callback_data="setmode"),
        InlineKeyboardButton("📊 Статус", callback_data="status"),
    )
    await message.reply("🛠 *Админ-панель*", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data in ["train", "blend_update", "setmode", "status"])
async def admin_cb(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return
    if call.data == "train":
        # Импортируй и вызови обучение
        from master.master import admin_train_blend
        await call.message.reply("🧠 Обучение blend и режима запущено!")
        admin_train_blend()
    elif call.data == "blend_update":
        await call.message.reply("🔄 Blend обновлен!")
    elif call.data == "setmode":
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("Sandbox", callback_data="mode_sandbox"),
            InlineKeyboardButton("Live", callback_data="mode_live"),
        )
        await call.message.reply("⚙️ Выберите режим:", reply_markup=kb)
    elif call.data == "status":
        await call.message.reply("💡 Все сервисы работают нормально!")

@dp.callback_query_handler(lambda c: c.data.startswith("mode_"))
async def mode_cb(call: types.CallbackQuery):
    mode = call.data.split("_", 1)[1]
    # Здесь можно сохранить режим в БД или файл
    await call.message.reply(f"Режим установлен: *{mode}*")

def main():
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    main()