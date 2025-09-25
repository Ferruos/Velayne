"""
Интеграция ЮKassa для подписок.
ВАЖНО:
- Зарегистрируйся в ЮKassa, получи shop_id и secret_key.
- Введи их в .env либо прямо сюда.
- Для Telegram-бота можно использовать ссылку на redirect-платёж или встроенный invoice (если поддерживается).
"""

import uuid
from yookassa import Payment

# ВСТАВЬ СВОИ ДАННЫЕ СЮДА
YOOKASSA_SHOP_ID = "ВСТАВЬ_СВОЙ_SHOP_ID"
YOOKASSA_SECRET_KEY = "ВСТАВЬ_СВОЙ_SECRET_KEY"  # Никому не показывай!

def create_yookassa_payment(amount, description, return_url):
    """
    Создаёт платёж в ЮKassa и возвращает ссылку.
    """
    payment = Payment.create({
        "amount": {"value": str(amount), "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": return_url},
        "capture": True,
        "description": description,
    }, uuid.uuid4())
    return payment.confirmation.confirmation_url

# В боте: после выбора тарифа и подтверждения оферты
# url = create_yookassa_payment(499, "Подписка Velayne Basic", "https://t.me/YourBot?start=paid")
# bot.send_message(chat_id, f"Оплатите по ссылке: {url}")