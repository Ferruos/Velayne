"""
Маркетплейс стратегий: добавление, выбор, рейтинг, отзывы.
"""
STRATEGY_DB = {}

def add_strategy(user_id, name, code, params=None, desc=""):
    sid = f"{name}_{user_id}_{len(STRATEGY_DB)}"
    STRATEGY_DB[sid] = {
        "owner": user_id, "name": name, "code": code,
        "params": params or {}, "desc": desc, "rating": [], "enabled": True
    }
    return sid

def get_strategies():
    return [s for s in STRATEGY_DB.values() if s["enabled"]]

def rate_strategy(sid, user_id, score):
    STRATEGY_DB[sid]["rating"].append((user_id, score))