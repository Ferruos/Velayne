"""
Ачивки: best month, never lost, first trade, etc.
"""
ACHIEVEMENTS = {}

def grant_achievement(user_id, name, desc):
    if user_id not in ACHIEVEMENTS:
        ACHIEVEMENTS[user_id] = []
    ACHIEVEMENTS[user_id].append({"name": name, "desc": desc})
    print(f"Ачивка '{name}' выдана пользователю {user_id}")