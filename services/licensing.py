"""
Лицензирование: фиксация и проверка лицензии пользователя.
"""
from datetime import datetime, timedelta

LICENSES = {}

def grant_license(user_id, plan, days):
    LICENSES[user_id] = {"plan": plan, "expires_at": datetime.now() + timedelta(days=days)}

def check_license(user_id):
    lic = LICENSES.get(user_id)
    if lic and lic["expires_at"] > datetime.now():
        return True
    return False