from datetime import datetime

# Стандартные ачивки
ACHIEVEMENTS = [
    {"code": "first_trade", "name": "Первая сделка", "desc": "Совершите первую сделку"},
    {"code": "first_profit", "name": "Первая прибыль", "desc": "Закройте сделку с прибылью"},
    {"code": "fifty_trades", "name": "50 сделок", "desc": "Совершите 50 сделок"},
    {"code": "long_streak", "name": "Серия успеха", "desc": "5 сделок подряд с профитом"},
    {"code": "risk_change", "name": "Смена риска", "desc": "Измените risk-mode"},
]

# Тайные ачивки (easter eggs)
SECRET_ACHIEVEMENTS = [
    {"code": "hidden_diver", "name": "🕵️ Hidden Diver", "desc": "Что-то особенное..."},
    {"code": "risk_tamer", "name": "🎲 Risk Tamer", "desc": "Вы приручили риск!"},
    {"code": "fast_fingers", "name": "⚡ Fast Fingers", "desc": "Очень быстрое действие..."},
    {"code": "night_owl", "name": "🌙 Night Owl", "desc": "Торговали глубокой ночью"},
    {"code": "zen_master", "name": "🧘 Zen Master", "desc": "Идеальный баланс"},
]

def get_user_achievements(user):
    # user.achievements — set
    unlocked = set(getattr(user, "achievements", []))
    standard = [a for a in ACHIEVEMENTS if a["code"] in unlocked]
    secrets = [a for a in SECRET_ACHIEVEMENTS if a["code"] in unlocked]
    return standard + secrets

def update_on_fill(user_id, fill, meta: dict):
    # Раскрытие секретных ачивок (пример логики)
    unlocked = []
    # Тайная: Hidden Diver — если pnl < -100 за одну сделку
    if fill.get("pnl", 0) < -100:
        unlocked.append("hidden_diver")
    # Тайная: Risk Tamer — если risk_mode в meta = 'turbo' и прибыль > 50
    if meta.get("risk_mode") == "turbo" and fill.get("pnl", 0) > 50:
        unlocked.append("risk_tamer")
    # Тайная: Fast Fingers — если latency_ms < 20
    if fill.get("meta", {}).get("latency_ms", 1000) < 20:
        unlocked.append("fast_fingers")
    # Тайная: Night Owl — если сделка в 2–4 ночи UTC
    hour = fill.get("dt", datetime.utcnow()).hour
    if 2 <= hour < 4:
        unlocked.append("night_owl")
    # Тайная: Zen Master — баланс ровно 10000
    if abs(meta.get("balance", 0) - 10000) < 1e-4:
        unlocked.append("zen_master")
    return unlocked

def update_on_day_close(user_id, pnl_day):
    pass  # stub for daily close aсhievements