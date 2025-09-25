"""
Мок-логика оплаты через Telegram (можно заменить на реальные платежи).
"""
async def process_payment(user_id, plan_name):
    # Всегда успешная оплата для теста
    return True