"""
Примитивные in-memory/mock репозитории для тестов.
"""
from datetime import datetime, timedelta

USERS = {}
SUBS = {}
BLENDS = {}
SESSIONS = {}

class UserRepo:
    @staticmethod
    def get(tg_id):
        return USERS.get(tg_id)

    @staticmethod
    def create(tg_id):
        USERS[tg_id] = {"id": tg_id, "tg_id": tg_id, "terms_accepted": False, "created_at": datetime.now()}
        return USERS[tg_id]

class SubscriptionRepo:
    @staticmethod
    def get(user_id):
        return SUBS.get(user_id)

    @staticmethod
    def update_or_create(user_id, plan, expires_at, status):
        SUBS[user_id] = {"user_id": user_id, "plan": plan, "expires_at": expires_at, "status": status}
        return SUBS[user_id]