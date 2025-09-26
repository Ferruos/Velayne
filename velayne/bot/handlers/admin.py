import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from velayne.infra.config import settings
from velayne.infra.db import (
    set_global_mode,
    get_global_mode,
    get_users_count,
    get_or_create_user,
    get_user_active_subscription,
    SessionLocal,
    User,
    Subscription
)
from velayne.core.ml import train_meta_model, load_golden_dataset

router = Router(name="admin")

admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="⚙️ Режим: Sandbox/Live", callback_data="switch_mode"),
        InlineKeyboardButton(text="🧠 Обучить модель", callback_data="train_model"),
    ],
    [
        InlineKeyboardButton(text="📊 Dataset info", callback_data="dataset_info"),
        InlineKeyboardButton(text="📑 Пользователи", callback_data="users_list"),
    ],
])

@router.callback_query(F.data == "switch_mode")
async def switch_mode(call: CallbackQuery):
    if not settings.ADMIN_ID or str(call.from_user.id) != str(settings.ADMIN_ID):
        await call.answer("⛔ Только для администратора", show_alert=True)
        return
    # Переключение режима
    mode = get_global_mode()
    new_mode = "live" if mode == "sandbox" else "sandbox"
    set_global_mode(new_mode)
    await call.message.answer(f"Режим теперь: {new_mode.upper()}", reply_markup=admin_menu)
    await call.bot.send_message(settings.ADMIN_ID, f"[РЕЖИМ] Админ переключил режим на {new_mode.upper()}.")
    logging.info(f"[ADMIN] Режим переключён на {new_mode}")

@router.callback_query(F.data == "train_model")
async def admin_train_model(call: CallbackQuery):
    try:
        df = load_golden_dataset()
        meta = train_meta_model(df)
        text = (
            f"Обучение завершено!\n"
            f"Точность: {meta['acc']:.3f}\n"
            f"Признаки: {', '.join(meta['features'])}"
        )
        await call.message.answer(text, reply_markup=admin_menu)
        await call.bot.send_message(settings.ADMIN_ID, f"[ОБУЧЕНИЕ] Модель обучена, acc={meta['acc']:.3f}")
        logging.info(f"[ADMIN] Обучена модель (acc={meta['acc']:.3f})")
    except Exception as e:
        logging.error(f"[ADMIN] Ошибка обучения: {e}")
        await call.message.answer("Ошибка обучения.", reply_markup=admin_menu)

@router.callback_query(F.data == "dataset_info")
async def dataset_info(call: CallbackQuery):
    try:
        df = load_golden_dataset()
        text = f"📊 Датаcет: {len(df)} баров, признаки: {', '.join(df.columns)}"
        await call.message.answer(text, reply_markup=admin_menu)
    except Exception as e:
        logging.error(f"[ADMIN] Ошибка dataset_info: {e}")
        await call.message.answer("Ошибка данных.", reply_markup=admin_menu)

@router.callback_query(F.data == "users_list")
async def users_list(call: CallbackQuery):
    try:
        # Вывести список пользователей и подписок
        with SessionLocal() as session:
            users = session.query(User).all()
            subs = {s.user_id: s for s in session.query(Subscription).all()}
        lines = ["<b>Пользователи:</b>"]
        for u in users:
            sub = subs.get(u.id)
            sub_info = f"{sub.status} до {sub.expires_at.strftime('%d.%m.%Y')}" if sub else "нет подписки"
            lines.append(f"{u.tg_id} ({u.role}): {sub_info}")
        await call.message.answer("\n".join(lines), reply_markup=admin_menu)
    except Exception as e:
        logging.error(f"[ADMIN] Ошибка вывода пользователей: {e}")
        await call.message.answer("Ошибка пользователей.", reply_markup=admin_menu)