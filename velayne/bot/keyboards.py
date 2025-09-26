from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu(is_admin: bool = False):
    kb = [
        [InlineKeyboardButton("📊 Торговля", callback_data="trade_menu"),
         InlineKeyboardButton("🤖 Обучение", callback_data="ml_menu")],
        [InlineKeyboardButton("📰 Новости", callback_data="news_menu"),
         InlineKeyboardButton("👤 Профиль", callback_data="profile_menu")],
        [InlineKeyboardButton("🛠 Настройки", callback_data="settings_menu")],
    ]
    if is_admin:
        kb.append([InlineKeyboardButton("👑 Админ", callback_data="admin_menu")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def profile_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("💳 Подписка", callback_data="sub_menu")],
        [InlineKeyboardButton("🏆 Ачивки", callback_data="achievements_menu")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
    ])

def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Перезапуск компонентов", callback_data="admin_restart")],
        [InlineKeyboardButton("Вкл/Выкл sandbox/live", callback_data="admin_toggle_mode")],
        [InlineKeyboardButton("Пользовательская статистика", callback_data="admin_user_stats")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
    ])

def news_nav_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("⬅️ Предыдущая", callback_data="news_prev"),
         InlineKeyboardButton("Следующая ➡️", callback_data="news_next")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
    ])