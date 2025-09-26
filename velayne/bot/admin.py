import logging
import asyncio
import platform
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputFile
from velayne.infra.config import settings
from velayne.infra.db import get_users_count, get_global_mode
from velayne.bot.ui import main_reply_menu, admin_diag_inline, back_inline_menu
from velayne.bot.texts_ru import DIAG_START, DIAG_DONE, ONLY_ADMIN, ERROR_GENERIC
import os
import pathlib
import sys
import traceback

router = Router(name="admin")

_start_time = datetime.utcnow()

async def send_text_safely(bot, chat_id, text, filename_prefix="diag"):
    blocks = [text[i:i+4096] for i in range(0, len(text), 4096)]
    if len(text.encode("utf-8")) > 100_000:
        fname = f"logs/{filename_prefix}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(text)
        await bot.send_document(chat_id, InputFile(fname), caption=f"{filename_prefix}.txt")
        return
    for block in blocks:
        await bot.send_message(chat_id, block)

async def gather_diag():
    try:
        result = []
        result.append(f"Диагностика на {datetime.utcnow().strftime('%d.%m.%Y %H:%M')} UTC")
        result.append(f"Python: {sys.version.split()[0]}, ОС: {platform.platform()}")
        env_path = pathlib.Path(settings.model_config.get('env_file', '.env'))
        result.append(f".env: {env_path} найден={env_path.exists()}")
        active = ["sandbox=ON", "scheduler=ON", f"bot={'ON' if settings.TG_TOKEN else 'OFF'}"]
        result.append(f"Компоненты: {', '.join(active)}")
        log_path = pathlib.Path(settings.LOG_DIR) / "velayne.log"
        if log_path.exists():
            sz = log_path.stat().st_size
            mtime = datetime.utcfromtimestamp(log_path.stat().st_mtime)
            result.append(f"Лог: {log_path} размер={sz} байт, обновлён={mtime.strftime('%d.%m.%Y %H:%M')}")
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()[-20:]
                result.append("Последние строки лога:\n" + "".join(lines))
        else:
            result.append(f"Лог: {log_path} не найден")
        try:
            mode = await asyncio.wait_for(get_global_mode(), timeout=5)
        except Exception as e:
            mode = f"ошибка: {e}"
        try:
            users = await asyncio.wait_for(get_users_count(), timeout=5)
        except Exception as e:
            users = f"ошибка: {e}"
        result.append(f"БД: режим={mode}, пользователей={users}")
        uptime = str(datetime.utcnow() - _start_time).split(".")[0]
        result.append(f"Uptime: {uptime}")
        return "\n".join(result)
    except Exception as e:
        return f"❗Ошибка диагностики: {e}"

@router.message(F.text == "⚡ Диагностика")
async def diag_entry(msg: Message):
    if not settings.ADMIN_ID or str(msg.from_user.id) != str(settings.ADMIN_ID):
        await msg.answer(ONLY_ADMIN, reply_markup=back_inline_menu())
        return
    await msg.answer("⚡ Диагностика", reply_markup=admin_diag_inline())

@router.callback_query(F.data == "diag:db")
async def diag_db(call: CallbackQuery):
    if not settings.ADMIN_ID or str(call.from_user.id) != str(settings.ADMIN_ID):
        await call.answer(ONLY_ADMIN, show_alert=True)
        await call.message.edit_text(ONLY_ADMIN, reply_markup=back_inline_menu())
        return
    sent = await call.message.edit_text(DIAG_START, reply_markup=back_inline_menu())
    async def run_diag():
        try:
            report = await asyncio.wait_for(gather_diag(), timeout=30)
            await send_text_safely(call.bot, call.message.chat.id, report)
            await call.message.answer(DIAG_DONE, reply_markup=admin_diag_inline())
        except Exception as e:
            logging.error(f"[ADMIN] diag_db fail: {e}")
            await call.message.answer(ERROR_GENERIC, reply_markup=back_inline_menu())
    asyncio.create_task(run_diag())