"""
Defines plan caps and enforce_plan_caps function.
"""
PLANS = {
    "trial": {"max_balance": 100, "max_order": 25, "max_open_positions": 2},
    "basic": {"max_balance": 100, "max_order": 25, "max_open_positions": 2},
    "standard": {"max_balance": 1000, "max_order": 250, "max_open_positions": 4},
    "pro": {"max_balance": 5000, "max_order": 1000, "max_open_positions": 8},
    "vip": {"max_balance": 1e9, "max_order": 2e8, "max_open_positions": 100},
}

def enforce_plan_caps(plan, balance, order_size, open_positions):
    caps = PLANS[plan]
    new_order_size = min(order_size, caps["max_order"])
    if balance > caps["max_balance"]:
        new_order_size = min(new_order_size, caps["max_balance"])
    allowed = open_positions < caps["max_open_positions"]
    return new_order_size, allowed