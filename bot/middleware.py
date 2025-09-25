"""
Middleware: проверка активной подписки, лимитов, terms_of_use.
"""
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types
from services.subscription import is_subscription_active, get_plan
from storage.repositories import SubscriptionRepo, UserRepo

class SubscriptionMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        user = UserRepo.get(message.from_user.id)
        if not user:
            UserRepo.create(message.from_user.id)
            await message.answer("Привет! Для работы необходимо согласиться с условиями /start")
            return

        sub = SubscriptionRepo.get(user["id"])
        if not is_subscription_active(sub):
            await message.answer("У вас нет активной подписки! Используйте /pay")
            return