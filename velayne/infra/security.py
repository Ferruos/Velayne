from aiogram import types
from velayne.infra.config import settings

def admin_only(handler):
    async def wrapper(event, *args, **kwargs):
        user_id = getattr(event.from_user, "id", None)
        if str(user_id) != str(settings.ADMIN_ID):
            if hasattr(event, "answer"):
                await event.answer("⛔ Только для администратора", show_alert=True)
            return
        return await handler(event, *args, **kwargs)
    return wrapper