import uuid
from datetime import datetime, timedelta

# Эмуляция YooKassa-интерфейса (заглушка)
class YooKassaEmulator:
    _payments = {}

    @classmethod
    def create_payment(cls, user_id, plan_id, amount, currency='RUB'):
        external_id = str(uuid.uuid4())
        payment_url = f"https://pay.mock/yookassa/{external_id}"
        cls._payments[external_id] = {
            "user_id": user_id,
            "plan_id": plan_id,
            "amount": amount,
            "currency": currency,
            "status": "pending",
            "created_at": datetime.utcnow(),
        }
        return payment_url, external_id

    @classmethod
    def handle_webhook(cls, payload):
        ext_id = payload.get("external_id")
        status = payload.get("status")
        if ext_id in cls._payments:
            cls._payments[ext_id]["status"] = status
            return True
        return False

    @classmethod
    def mark_paid(cls, external_id):
        if ext_id := external_id in cls._payments:
            cls._payments[external_id]["status"] = "success"
            return True
        return False

    @classmethod
    def get_payment(cls, external_id):
        return cls._payments.get(external_id)

def create_payment(user_id, plan_id, amount, currency='RUB'):
    return YooKassaEmulator.create_payment(user_id, plan_id, amount, currency)

def handle_webhook(payload):
    return YooKassaEmulator.handle_webhook(payload)

def mark_payment_paid(external_id):
    return YooKassaEmulator.mark_paid(external_id)