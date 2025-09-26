import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, BotCommandScopeDefault, Message, CallbackQuery
from velayne.infra.config import get_settings, is_sandbox_mode, toggle_sandbox_mode, reload_components
from velayne.bot.keyboards import main_menu, profile_menu, admin_menu, news_nav_menu
from velayne.infra.db import (
    get_last_trades,
    get_live_stats,
    get_user_sub_status,
    get_or_create_user,
    award_achievement,
    get_user_achievements,
    list_users
)
from velayne.core.ml import simulate_strategy_on_data, load_golden_dataset
from velayne.core.news import get_latest_news
settings = get_settings()

async def start_bot():
    TG_TOKEN = settings.TG_TOKEN
    if not TG_TOKEN:
        logging.warning("[БОТ] TG_TOKEN не задан. Бот не будет запущен.")
        return None

    bot = Bot(
        TG_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    async def heartbeat():
        while True:
            logging.info("[БОТ] бот жив")
            await asyncio.sleep(30)

    # Главное меню
    @dp.message(F.text == "/start")
    async def cmd_start(msg: Message):
        is_admin = str(msg.from_user.id) == str(settings.ADMIN_ID)
        await msg.answer("👋 Добро пожаловать в Velayne!", reply_markup=main_menu(is_admin))

    # Кнопка "Профиль"
    @dp.callback_query(F.data == "profile_menu")
    async def cb_profile(call: CallbackQuery):
        user = await get_or_create_user(call.from_user.id)
        st = await get_user_sub_status(call.from_user.id)
        achs = await get_user_achievements(user.id)
        achv_text = "🏆 Ачивки:\n" + ("Нет" if not achs else "\n".join(f"• {a}" for a in achs))
        sub_text = f"💳 Подписка: {'активна до ' + st['until'].strftime('%d.%m.%Y') if st['active'] else 'нет'}"
        await call.message.edit_text(
            f"👤 Ваш профиль\n{sub_text}\n{achv_text}",
            reply_markup=profile_menu()
        )
        await call.answer("Профиль", show_alert=False)

    # Кнопка "Ачивки"
    @dp.callback_query(F.data == "achievements_menu")
    async def cb_achievements(call: CallbackQuery):
        user = await get_or_create_user(call.from_user.id)
        achs = await get_user_achievements(user.id)
        text = "🏆 Ваши ачивки:\n" + ("Пока нет." if not achs else "\n".join(f"• {a}" for a in achs))
        await call.message.edit_text(text, reply_markup=profile_menu())
        await call.answer("Ачивки", show_alert=False)

    # Кнопка "Торговля"
    @dp.callback_query(F.data == "trade_menu")
    async def cb_trade(call: CallbackQuery):
        trades = await get_last_trades(5)
        stats = await get_live_stats()
        text = f"📊 <b>Последние сделки:</b>\n"
        for t in trades:
            text += f"{t['ts']} | {t['symbol']} | {t['side']} @ {t['price']:.2f} x {t['amount']:.6f}\n"
        text += f"\n<b>Статистика:</b>\nPnL: {stats['pnl_abs']:.2f} ({stats['pnl_pct']:.2f}%)\nSharpe: {stats['sharpe']:.2f}\nMaxDD: {stats['maxdd']:.2f}%"
        await call.message.edit_text(text, reply_markup=main_menu(str(call.from_user.id) == str(settings.ADMIN_ID)))
        await call.answer("Торговля", show_alert=False)
        # Achievement: первый trade
        user = await get_or_create_user(call.from_user.id)
        if trades and await get_user_achievements(user.id) == []:
            await award_achievement(user.id, "Первый трейд")

    # Кнопка "Обучение"
    @dp.callback_query(F.data == "ml_menu")
    async def cb_ml(call: CallbackQuery):
        await call.answer("Обучение", show_alert=False)
        df = load_golden_dataset()
        sim = simulate_strategy_on_data(df)
        text = f"🤖 Модель обучена!\nSharpe: {sim['sharpe']:.2f}\n"
        await call.message.edit_text(text, reply_markup=main_menu(str(call.from_user.id) == str(settings.ADMIN_ID)))

    # Кнопка "Новости"
    news_index = {}

    @dp.callback_query(F.data == "news_menu")
    async def cb_news(call: CallbackQuery):
        news = await get_latest_news(5)
        if not news:
            await call.message.edit_text("Нет новостей.", reply_markup=news_nav_menu())
            await call.answer("Нет новостей", show_alert=False)
            return
        news_index[call.from_user.id] = 0
        n = news[0]
        txt = f"<b>{n['title']}</b>\n{n['dt']}\n{n['link']}"
        await call.message.edit_text(txt, reply_markup=news_nav_menu())
        await call.answer("Новости", show_alert=False)

    @dp.callback_query(F.data.in_(["news_next", "news_prev"]))
    async def cb_news_nav(call: CallbackQuery):
        news = await get_latest_news(5)
        idx = news_index.get(call.from_user.id, 0)
        if call.data == "news_next":
            idx = min(idx+1, len(news)-1)
        else:
            idx = max(idx-1, 0)
        news_index[call.from_user.id] = idx
        n = news[idx]
        txt = f"<b>{n['title']}</b>\n{n['dt']}\n{n['link']}"
        await call.message.edit_text(txt, reply_markup=news_nav_menu())
        await call.answer("", show_alert=False)

    # Кнопка "Подписка"
    @dp.callback_query(F.data == "sub_menu")
    async def cb_sub(call: CallbackQuery):
        st = await get_user_sub_status(call.from_user.id)
        text = f"💳 Подписка: {'активна до ' + st['until'].strftime('%d.%m.%Y') if st['active'] else 'нет'}"
        await call.message.edit_text(text, reply_markup=profile_menu())
        await call.answer("Подписка", show_alert=False)

    # Настройки
    @dp.callback_query(F.data == "settings_menu")
    async def cb_settings(call: CallbackQuery):
        await call.message.edit_text("🛠 Раздел в разработке.", reply_markup=main_menu(str(call.from_user.id) == str(settings.ADMIN_ID)))
        await call.answer("Настройки", show_alert=False)

    # Админ меню
    @dp.callback_query(F.data == "admin_menu")
    async def cb_admin(call: CallbackQuery):
        await call.message.edit_text("👑 Админ-панель", reply_markup=admin_menu())
        await call.answer("Админ-панель", show_alert=False)

    @dp.callback_query(F.data == "admin_restart")
    async def cb_admin_restart(call: CallbackQuery):
        reload_components()
        await call.message.edit_text("Компоненты перезапущены.", reply_markup=admin_menu())
        await call.answer("Перезапуск", show_alert=False)

    @dp.callback_query(F.data == "admin_toggle_mode")
    async def cb_admin_toggle(call: CallbackQuery):
        new_mode = toggle_sandbox_mode()
        await call.message.edit_text(f"Режим сервисов: {'Sandbox' if new_mode else 'Live'}", reply_markup=admin_menu())
        await call.answer("Режим изменён", show_alert=False)

    @dp.callback_query(F.data == "admin_user_stats")
    async def cb_admin_stats(call: CallbackQuery):
        users = await list_users(10)
        text = "Пользователи:\n" + "\n".join(f"{u['tg_id']}: {u['sub_until']}" for u in users)
        await call.message.edit_text(text, reply_markup=admin_menu())
        await call.answer("Статистика пользователей", show_alert=False)

    # Назад
    @dp.callback_query(F.data == "main_menu")
    async def cb_main_menu(call: CallbackQuery):
        is_admin = str(call.from_user.id) == str(settings.ADMIN_ID)
        await call.message.edit_text("Главное меню", reply_markup=main_menu(is_admin))
        await call.answer("Главное меню", show_alert=False)

    # Назад из профиля
    @dp.callback_query(F.data == "profile_menu")
    async def cb_profile_menu(call: CallbackQuery):
        is_admin = str(call.from_user.id) == str(settings.ADMIN_ID)
        await call.message.edit_text("Главное меню", reply_markup=main_menu(is_admin))
        await call.answer("Главное меню", show_alert=False)

    # Heartbeat task
    asyncio.create_task(heartbeat())

    await bot.set_my_commands([
        BotCommand(command="start", description="Запуск"),
        BotCommand(command="help",  description="Справка"),
    ], scope=BotCommandScopeDefault())

    logging.info("[БОТ] Меню и команды установлены")
    me = await bot.get_me()
    logging.info(f"[БОТ] Онлайн как @{me.username} (id={me.id})")

    try:
        await dp.start_polling(bot, allowed_updates=None)
    except Exception as e:
        logging.error(f"[БОТ] Polling аварийно завершён: {e}")
        raise