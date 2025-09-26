import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from velayne.infra.config import settings
from velayne.infra.db import (
    get_or_create_user,
    get_user_active_subscription,
)
from velayne.core.ml import simulate_strategy_on_data, load_golden_dataset
from velayne.bot.texts_ru import SUBSCRIPTION_STATUS, ERROR_GENERIC
from velayne.bot.news_cache import news_cache  # Предполагается, что news_cache реализован

router = Router(name="user")

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📊 Моя подписка", callback_data="sub_status")],
    [InlineKeyboardButton(text="📰 Новости", callback_data="news")],
    [InlineKeyboardButton(text="📈 Статистика", callback_data="stats")],
])

@router.message(F.text == "/start")
async def start_handler(msg: Message):
    is_admin = str(msg.from_user.id) == str(settings.ADMIN_ID)
    await msg.answer(
        "👋 Добро пожаловать!\nВыберите действие:",
        reply_markup=main_menu
    )

@router.callback_query(F.data == "sub_status")
async def sub_status(call: CallbackQuery):
    try:
        user = get_or_create_user(call.from_user.id)
        sub = get_user_active_subscription(user.id)
        if sub:
            await call.message.answer(
                f"Ваша подписка активна до {sub.expires_at.strftime('%d.%m.%Y %H:%M')}",
                reply_markup=main_menu
            )
        else:
            await call.message.answer("Нет активной подписки.", reply_markup=main_menu)
    except Exception as e:
        logging.error(f"[USER] Ошибка подписки: {e}")
        await call.message.answer(ERROR_GENERIC, reply_markup=main_menu)

@router.callback_query(F.data == "news")
async def news(call: CallbackQuery):
    try:
        news_list = news_cache.get_latest(5)  # news_cache должен реализовывать get_latest
        if not news_list:
            await call.message.answer("Нет свежих новостей.", reply_markup=main_menu)
            return
        text = "📰 <b>Новости:</b>\n"
        for n in news_list:
            text += f"• <b>{n['title']}</b>\n{n['link']}\n"
        await call.message.answer(text, reply_markup=main_menu)
        # Дублирование новости админу
        await call.bot.send_message(settings.ADMIN_ID, f"[НОВОСТИ] Пользователь {call.from_user.id} запросил новости.")
    except Exception as e:
        logging.error(f"[USER] Ошибка новостей: {e}")
        await call.message.answer(ERROR_GENERIC, reply_markup=main_menu)

@router.callback_query(F.data == "stats")
async def stats(call: CallbackQuery):
    try:
        df = load_golden_dataset()
        sim = simulate_strategy_on_data(df)
        text = (
            f"📈 <b>Ваша статистика:</b>\n"
            f"PnL: {sim['net_pnl']:.2f}\n"
            f"Сделок: {sim['trades']}\n"
            f"Sharpe: {sim['sharpe']:.2f}\n"
        )
        await call.message.answer(text, reply_markup=main_menu)
        # Дублирование события админу
        await call.bot.send_message(settings.ADMIN_ID, f"[СТАТИСТИКА] Пользователь {call.from_user.id} запросил статистику.")
    except Exception as e:
        logging.error(f"[USER] Ошибка статистики: {e}")
        await call.message.answer(ERROR_GENERIC, reply_markup=main_menu)