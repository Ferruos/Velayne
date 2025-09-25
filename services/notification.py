"""
Unified notification sender for Telegram via aiogram.
"""
import os
import asyncio
from aiogram import Bot

TOKEN = os.getenv("TG_TOKEN", "PASTE_YOUR_TOKEN_HERE")
bot = Bot(token=TOKEN)

async def send_notify(chat_id, text):
    await bot.send_message(chat_id, text)

def notify(chat_id, text):
    try:
        asyncio.run(send_notify(chat_id, text))
    except RuntimeError:
        # For nested event loops (when inside aiogram bot already)
        pass