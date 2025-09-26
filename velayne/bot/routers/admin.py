from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from velayne.bot.keyboards import admin_kb
from velayne.infra.config import is_sandbox_mode, toggle_sandbox_mode, reload_components
from velayne.core.ml import train_meta_model, load_golden_dataset
from velayne.infra.db import list_users, export_logs_zip  # реализуй
from velayne.infra.security import admin_only  # фильтр/декоратор

router = Router(name="admin")

@router.message(Command("admin"))
@admin_only
async def admin_menu(m: Message):
    await m.answer("Админ-панель:", reply_markup=admin_kb(is_sandbox_mode()))

@router.callback_query(F.data=="toggle_mode")
@admin_only
async def toggle(c: CallbackQuery):
    new_mode = await toggle_sandbox_mode()
    await c.message.answer("Режим переключён: " + ("🧪 SANDBOX" if new_mode else "🔴 LIVE"))
    await reload_components()
    await c.answer()

@router.callback_query(F.data=="train_now")
@admin_only
async def train_now(c: CallbackQuery):
    res = await train_meta_model(async_mode=True)  # добавь async враппер
    await c.message.answer(f"🧠 Обучение завершено: acc={res['acc']:.3f}")
    await c.answer()

@router.callback_query(F.data=="dataset_info")
@admin_only
async def dsinfo(c: CallbackQuery):
    ds = await load_golden_dataset()
    await c.message.answer(f"Dataset: bars={len(ds)} | колонки: {list(ds.columns)[:8]}...")
    await c.answer()

@router.callback_query(F.data=="users_list")
@admin_only
async def users_list_cb(c: CallbackQuery):
    items = await list_users(limit=50)
    if not items:
        await c.message.answer("Пользователей не найдено.")
    else:
        text = "👥 Пользователи:\n" + "\n".join([f"• {u['tg_id']} | sub: {u['sub_until']}" for u in items])
        await c.message.answer(text)
    await c.answer()

@router.callback_query(F.data=="export_logs")
@admin_only
async def export_logs_cb(c: CallbackQuery):
    path = await export_logs_zip()
    from aiogram.types import FSInputFile
    await c.message.answer_document(FSInputFile(path), caption="Логи")
    await c.answer()