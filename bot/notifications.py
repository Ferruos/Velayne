from aiogram import Bot

async def notify_trade(bot: Bot, chat_id, trade):
    await bot.send_message(chat_id, f"Сделка: {trade}")

async def notify_drawdown(bot: Bot, chat_id, dd):
    await bot.send_message(chat_id, f"Просадка: {dd}%")

async def notify_plan_limit(bot: Bot, chat_id, limit):
    await bot.send_message(chat_id, f"Превышен лимит плана: {limit}")

async def notify_payment(bot: Bot, chat_id):
    await bot.send_message(chat_id, "Подписка успешно продлена!")