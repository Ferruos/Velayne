import os
import uuid
from datetime import datetime, timedelta
import aiohttp
from velayne.infra.config import get_settings
from velayne.infra.db import upsert_subscription
from velayne.services.event_bus import publish, SubEvent

YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID", "") or getattr(get_settings(), "YOOKASSA_SHOP_ID", "")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY", "") or getattr(get_settings(), "YOOKASSA_SECRET_KEY", "")

API_URL = "https://api.yookassa.ru/v3/payments"

async def create_payment(user_id: int, plan_id: str, amount: float, days: int = 30, currency: str = "RUB") -> str:
    # Простейший запрос к ЮKassa API для создания платежа (без webhooks)
    payment_id = str(uuid.uuid4())
    payload = {
        "amount": {
            "value": f"{amount:.2f}",
            "currency": currency
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/your_velayne_bot"
        },
        "capture": True,
        "description": f"Подписка Velayne {plan_id} для {user_id}",
            "metadata": {
                "user_id": str(user_id),
                "plan_id": plan_id,
                "days": days,
                "payment_id": payment_id
        }
    }
    headers = {
        "Content-Type": "application/json",
    }
    auth = aiohttp.BasicAuth(YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)
    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.post(API_URL, json=payload, headers=headers) as resp:
            data = await resp.json()
            url = data.get("confirmation", {}).get("confirmation_url")
            ext_id = data.get("id", payment_id)
            return url, ext_id

async def confirm_payment_and_extend(user_id: int, ext_id: str, plan: str, amount: float, days: int = 30):
    # Продлеваем подписку, пишем в БД, публикуем событие, уведомляем
    until = datetime.utcnow() + timedelta(days=days)
    await upsert_subscription(user_id, plan, "active", days, "yookassa", ext_id)
    await publish(SubEvent(
        user_id=user_id,
        action="paid",
        until=until,
        amount=amount
    ))
    return until

async def get_payment_status(ext_id: str) -> dict:
    # Простейший прямой запрос к ЮKassa API (можно заменить на webhook)
    url = f"{API_URL}/{ext_id}"
    headers = {"Content-Type": "application/json"}
    auth = aiohttp.BasicAuth(YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)
    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.get(url, headers=headers) as resp:
            return await resp.json()

# Обработчик /payment_status
async def payment_status_handler(msg, ext_id):
    data = await get_payment_status(ext_id)
    status = data.get("status")
    if status == "succeeded":
        await msg.answer("✅ Платёж успешно подтверждён! Спасибо.")
    elif status == "pending":
        await msg.answer("⏳ Платёж ожидает подтверждения. Проверьте позже.")
    else:
        await msg.answer("❌ Платёж не найден или отменён.")