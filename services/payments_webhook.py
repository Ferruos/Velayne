"""
Webhook для ЮKassa (FastAPI).
Укажи этот URL в личном кабинете ЮKassa для получения статуса платежа.
"""
from fastapi import FastAPI, Request
from services.subscription import renew_subscription
from storage.repositories import UserRepo, SubscriptionRepo

app = FastAPI()

@app.post("/yookassa/webhook")
async def yookassa_webhook(request: Request):
    data = await request.json()
    # ЮKassa отправляет структуру, где payment.succeeded — подтверждение оплаты
    if data.get("event") == "payment.succeeded":
        payment = data["object"]
        description = payment.get("description", "")
        user_id = parse_user_id_from_description(description)  # Сделай функцию разбора
        plan = parse_plan_from_description(description)        # Сделай функцию разбора
        if user_id and plan:
            user = UserRepo.get(user_id)
            renew_subscription(user, SubscriptionRepo, plan)
            # Можно уведомить пользователя в Telegram
    return {"ok": True}