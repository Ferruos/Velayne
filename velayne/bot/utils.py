import logging
import asyncio
import os
from datetime import datetime
from aiogram.exceptions import RetryAfter, TelegramAPIError
from aiogram.types import InputFile

LOG_PATH = os.path.join("logs", "msg_safely.log")

async def send_text_safely(bot, chat_id, text, filename_prefix="report"):
    """
    Sends text to Telegram as a message (≤4096 chars per block) or as document if >100KB.
    Handles RetryAfter, logs message meta.
    """
    os.makedirs("logs", exist_ok=True)
    try:
        # If text is very large ( >100KB ) send as document
        encoded = text.encode("utf-8")
        if len(encoded) > 100_000:
            fname = f"logs/{filename_prefix}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.txt"
            with open(fname, "w", encoding="utf-8") as f:
                f.write(text)
            msg = await bot.send_document(chat_id, InputFile(fname), caption=f"{filename_prefix}.txt")
            _log_msg(chat_id, "document", msg.message_id, fname)
            return [msg]
        # Else send as multiple messages in blocks of 4096
        msgs = []
        blocks = [text[i:i+4096] for i in range(0, len(text), 4096)]
        for block in blocks:
            while True:
                try:
                    msg = await bot.send_message(chat_id, block)
                    _log_msg(chat_id, "message", msg.message_id, f"len={len(block)}")
                    msgs.append(msg)
                    break
                except RetryAfter as e:
                    logging.warning(f"[send_text_safely] RetryAfter {e.timeout} sec")
                    await asyncio.sleep(e.timeout + 1)
                except TelegramAPIError as e:
                    logging.error(f"[send_text_safely] TelegramAPIError: {e}")
                    break
        return msgs
    except Exception as e:
        logging.error(f"[send_text_safely] Exception: {e}")
        return []

def _log_msg(chat_id, kind, msg_id, meta):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            ts = datetime.utcnow().isoformat()
            f.write(f"{ts} chat_id={chat_id} kind={kind} msg_id={msg_id} meta={meta}\n")
    except Exception as e:
        logging.warning(f"[send_text_safely] log file error: {e}")