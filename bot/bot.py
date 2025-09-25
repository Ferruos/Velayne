import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8291187695:AAFpr46bqQ4cJg_JVfPDoQxQkMM09mzDKTg"
ADMIN_ID = 760374544

def escape_md(text: str) -> str:
    for c in r"\_*[]()~`>#+-=|{}.!":
        text = text.replace(c, '\\' + c)
    return text

bot = Bot(token=TOKEN, parse_mode="MarkdownV2")
dp = Dispatcher(bot)

def is_admin(user_id):
    return user_id == ADMIN_ID

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("/sandbox_run"), KeyboardButton("/sandbox_stop"))
    kb.add(KeyboardButton("/blend_status"), KeyboardButton("/train_blend"))
    kb.add(KeyboardButton("/analytics"), KeyboardButton("/mode"))
    if is_admin(message.from_user.id):
        kb.add(KeyboardButton("/admin"))
    await message.reply(
        escape_md("*Velayne*: _Добро пожаловать!_\\nЖми кнопки снизу 👇"),
        reply_markup=kb
    )

@dp.message_handler(commands=["admin"])
async def admin_panel(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply(escape_md("⛔️ Нет доступа."))
        return
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("▶️ Sandbox Run", callback_data="sandbox_run"),
        InlineKeyboardButton("⏹️ Sandbox Stop", callback_data="sandbox_stop"),
        InlineKeyboardButton("🧠 Обучить Blend", callback_data="train_blend"),
        InlineKeyboardButton("📈 Аналитика", callback_data="analytics"),
    )
    kb.add(InlineKeyboardButton("⚙️ Режим", callback_data="mode"))
    await message.reply(
        escape_md("🛠 *Админ-панель* — выбери действие:"),
        reply_markup=kb
    )

@dp.callback_query_handler(lambda c: c.data in ["sandbox_run", "sandbox_stop", "train_blend", "analytics", "mode"])
async def admin_cb(call: types.CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Нет доступа", show_alert=True)
        return

    if call.data == "sandbox_run":
        # Имитация запуска sandbox-воркера. Здесь реальный запуск если нужно:
        # import subprocess; subprocess.Popen(["python", "workers/worker.py", str(call.from_user.id), "sandbox"])
        await call.message.reply(escape_md("▶️ Sandbox-воркер запущен!"))
    elif call.data == "sandbox_stop":
        await call.message.reply(escape_md("⏹️ Sandbox-воркер остановлен (или останови вручную)."))
    elif call.data == "train_blend":
        # Имитация запуска обучения blend. Здесь реальный запуск если нужно:
        # import subprocess; subprocess.Popen(["python", "master/master.py"])
        await call.message.reply(escape_md("🧠 Обучение Blend запущено!"))
    elif call.data == "analytics":
        await call.message.reply(escape_md("📈 Аналитика: Здесь будет реальная аналитика blend/торговли."))
    elif call.data == "mode":
        await call.message.reply(escape_md("⚙️ Сейчас всегда sandbox режим."))

@dp.message_handler(commands=["sandbox_run"])
async def sandbox_run_cmd(message: types.Message):
    await message.reply(escape_md("▶️ Sandbox-воркер запущен!"))

@dp.message_handler(commands=["sandbox_stop"])
async def sandbox_stop_cmd(message: types.Message):
    await message.reply(escape_md("⏹️ Sandbox-воркер остановлен (или останови вручную)."))

@dp.message_handler(commands=["train_blend"])
async def train_blend_cmd(message: types.Message):
    await message.reply(escape_md("🧠 Обучение Blend запущено!"))

@dp.message_handler(commands=["blend_status"])
async def blend_status_cmd(message: types.Message):
    await message.reply(escape_md("📈 Blend аналитика: Здесь будет реальная blend-аналитика."))

@dp.message_handler(commands=["analytics"])
async def analytics_cmd(message: types.Message):
    await message.reply(escape_md("📈 Аналитика: Здесь будет реальная аналитика торговли."))

@dp.message_handler(commands=["mode"])
async def mode_cmd(message: types.Message):
    await message.reply(escape_md("⚙️ Сейчас всегда sandbox режим."))

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)