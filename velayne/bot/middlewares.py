import time
import re
from aiogram import BaseMiddleware
from aiogram.types import Update
from aiogram.exceptions import TelegramBadRequest
from loguru import logger
from velayne.infra.db import get_global_mode, get_or_create_user, get_user_active_subscription
from velayne.infra.config import settings

SENSITIVE_PATTERNS = [
    re.compile(r"(?i)(api[_\-]?key|secret|passphrase)[\'\"]?\s*[:=]\s*[\'\"]?([A-Za-z0-9\-_]{12,})[\'\"]?"),
    re.compile(r"[A-Za-z0-9]{32,}"),  # long hex/base64 strings
]

def redact_secrets(text: str) -> str:
    out = text
    for pat in SENSITIVE_PATTERNS:
        out = pat.sub(lambda m: m.group(0)[:6] + "******REDACTED******", out)
    return out

class RedactionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # redact sensitive in logs
        upd = event.model_dump() if hasattr(event, "model_dump") else str(event)
        redacted = redact_secrets(str(upd))
        logger.info(f"Update: {redacted[:512]}")
        return await handler(event, data)

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit=20, per_seconds=30):
        self.limit = limit
        self.per_seconds = per_seconds
        self.user_times = {}

    async def __call__(self, handler, event, data):
        user_id = None
        if hasattr(event, "from_user") and event.from_user:
            user_id = event.from_user.id
        elif hasattr(event, "message") and event.message and hasattr(event.message, "from_user"):
            user_id = event.message.from_user.id
        max_limit = self.limit
        if user_id and str(user_id) == str(getattr(settings, "ADMIN_ID", "0")):
            max_limit *= 10
        if user_id:
            now = time.time()
            times = self.user_times.get(user_id, [])
            times = [t for t in times if now - t < self.per_seconds]
            if len(times) >= max_limit:
                if len(times) == max_limit:
                    logger.warning(f"RateLimit: user {user_id} spamming, throttled.")
                    try:
                        await event.answer("Помедленнее 🙏", show_alert=True)
                    except Exception:
                        pass
                return
            times.append(now)
            self.user_times[user_id] = times
        return await handler(event, data)

class ExecTimeMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        t0 = time.monotonic()
        result = await handler(event, data)
        dt = (time.monotonic() - t0) * 1000
        from velayne.infra.perf import update_latency, flush_perf_log
        label = type(event).__name__
        update_latency(f"bot_{label}", dt)
        if int(time.time()) % 10 == 0:
            flush_perf_log()
        return result

class RBACMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Allow/deny by user.role
        user_id = None
        role = "user"
        if hasattr(event, "from_user") and event.from_user:
            user_id = event.from_user.id
        elif hasattr(event, "message") and event.message and hasattr(event.message, "from_user"):
            user_id = event.message.from_user.id
        if user_id:
            from velayne.infra.db import SessionLocal, User
            session = SessionLocal()
            dbu = session.query(User).filter_by(tg_id=user_id).first()
            if dbu and dbu.role:
                role = dbu.role
        cb_data = getattr(event, "data", None)
        if cb_data:
            if "admin:pay" in cb_data and role != "admin":  # payments only for admin
                await event.answer("Нет доступа (только для admin).", show_alert=True)
                return
            if "admin:moderate" in cb_data and role not in ("editor", "admin"):
                await event.answer("Нет доступа (только для editor/admin).", show_alert=True)
                return
        return await handler(event, data)

class SubscriptionStubMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = None
        if hasattr(event, "from_user") and event.from_user:
            user_id = event.from_user.id
        elif hasattr(event, "message") and event.message and hasattr(event.message, "from_user"):
            user_id = event.message.from_user.id
        mode = await get_global_mode()
        if mode == "live":
            user = await get_or_create_user(user_id)
            active_sub = await get_user_active_subscription(user.id)
            if not active_sub:
                try:
                    await event.answer("🛡 Для доступа в LIVE-режиме нужна активная подписка. Оформить можно через /pay", show_alert=True)
                except TelegramBadRequest:
                    pass
                return
        return await handler(event, data)