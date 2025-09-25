from aiogram import types
from services.payments import create_yookassa_payment

@dp.message_handler(commands=["pay"])
async def pay(m: types.Message):
    # В реальности: спросить тариф, offer_confirmed и т.п.
    plan = "Basic"
    amount = 499
    return_url = "https://t.me/YourBot?start=paid"   # ВСТАВЬ СВОЮ ССЫЛКУ
    url = create_yookassa_payment(amount, f"Подписка Velayne {plan}", return_url)
    await m.answer(
        f"Для активации тарифа {plan}, оплатите по ссылке:\n{url}\n\nПосле оплаты подписка активируется автоматически (или напишите /status)."
    )