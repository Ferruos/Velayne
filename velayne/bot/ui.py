from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from velayne.infra.config import settings

def main_reply_menu(is_admin: bool) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="📊 Портфель"), KeyboardButton(text="⚙️ Настройки")],
        [KeyboardButton(text=f"🧪 Режим: {'Sandbox' if settings.SERVICE_MODE == 'sandbox' else 'Live'}"),
         KeyboardButton(text="🧾 Подписка")],
        [KeyboardButton(text="ℹ️ Справка")],
    ]
    if is_admin:
        rows.insert(2, [KeyboardButton(text="⚡ Диагностика")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

def back_inline_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu:main")]
    ])

def admin_diag_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("Проверить БД", callback_data="diag:db"),
            InlineKeyboardButton("Сервисы", callback_data="diag:svc"),
        ],
        [
            InlineKeyboardButton("Последние логи", callback_data="diag:logs"),
            InlineKeyboardButton("Пинг биржи", callback_data="diag:ping"),
        ],
        [
            InlineKeyboardButton("Проверка оннх модели", callback_data="diag:onnx"),
            InlineKeyboardButton("⬅️ Назад", callback_data="menu:main"),
        ]
    ])

def settings_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("Частота отчётов", callback_data="settings:freq"),
            InlineKeyboardButton("Уведомления", callback_data="settings:notify"),
        ],
        [
            InlineKeyboardButton("Стратегия по умолчанию", callback_data="settings:strategy"),
            InlineKeyboardButton("Язык", callback_data="settings:lang"),
        ],
        [
            InlineKeyboardButton("⬅️ Назад", callback_data="menu:main")
        ]
    ])

def subscription_inline(is_active: bool = False):
    if is_active:
        rows = [
            [InlineKeyboardButton("Продлить", callback_data="subs:pay")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="menu:main")]
        ]
    else:
        rows = [
            [InlineKeyboardButton("Оплатить", callback_data="subs:pay")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="menu:main")]
        ]
    return InlineKeyboardMarkup(inline_keyboard=rows)

def mode_switch_inline(is_admin: bool):
    if is_admin:
        rows = [
            [InlineKeyboardButton("🧪 Sandbox", callback_data="mode:sandbox"),
             InlineKeyboardButton("💹 Live", callback_data="mode:live")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="menu:main")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=rows)
    return back_inline_menu()

def data_provider_inline(last_bar_ts: str = ""):
    rows = [
        [InlineKeyboardButton("Докачать сейчас", callback_data="data:fetch"),
         InlineKeyboardButton("Показать последнюю свечу", callback_data="data:last")],
        [InlineKeyboardButton("Источник", callback_data="data:src")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="menu:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)

__all__ = [
    "main_reply_menu",
    "back_inline_menu",
    "admin_diag_inline",
    "settings_inline",
    "subscription_inline",
    "mode_switch_inline",
    "data_provider_inline"
]