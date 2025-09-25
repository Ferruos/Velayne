"""
Сервис управления подписками и лимитами пользователей.
"""
from datetime import datetime, timedelta

PLANS = {
    "Trial": {"price": 1, "period": 2, "max_balance": 100, "max_order_size": 10, "max_open_positions": 1},
    "Basic": {"price": 499, "period": 30, "max_balance": 100, "max_order_size": 10, "max_open_positions": 1},
    "Standard": {"price": 1490, "period": 30, "max_balance": 1000, "max_order_size": 50, "max_open_positions": 3},
    "Pro": {"price": 4900, "period": 30, "max_balance": 5000, "max_order_size": 100, "max_open_positions": 10},
    "VIP": {"price": 9900, "period": 30, "max_balance": None, "max_order_size": None, "max_open_positions": None},
}

def get_plan(plan):
    return PLANS[plan]

def is_subscription_active(sub):
    return sub and sub.expires_at > datetime.now() and sub.status == "active"

def renew_subscription(user, sub_repo, plan_name):
    plan = get_plan(plan_name)
    until = datetime.now() + timedelta(days=plan["period"])
    sub_repo.update_or_create(user.id, plan=plan_name, expires_at=until, status="active")
    return until