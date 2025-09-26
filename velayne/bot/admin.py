from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from velayne.infra.config import settings
from velayne.infra.db import get_users_count, get_global_mode, set_global_mode
from velayne.infra import health
from velayne.infra import retention
from .ui import (
    admin_panel,
    diagnostics_message,
    self_heal_result,
    admin_model_metrics_message,
    admin_strategy_mix_message,
    retention_summary_message,
    retention_policy_message,
    selftest_message,
)
from pathlib import Path
import json
import asyncio

router = Router()

def is_admin(msg_or_cb):
    user_id = None
    if hasattr(msg_or_cb, "from_user"):
        user_id = msg_or_cb.from_user.id
    elif hasattr(msg_or_cb, "message") and msg_or_cb.message and hasattr(msg_or_cb.message, "from_user"):
        user_id = msg_or_cb.message.from_user.id
    return int(user_id) == settings.ADMIN_ID

@router.message(Command("admin"))
async def admin_cmd(msg: Message):
    if not is_admin(msg):
        await msg.answer("❌ Нет доступа.")
        return
    users_count = await get_users_count()
    mode = await get_global_mode()
    text, kb = admin_panel(mode, users_count)
    await msg.answer(text, reply_markup=kb)

# ML train now with source/weights controls
@router.callback_query(F.data.startswith("admin:train_ml"))
async def admin_train_ml_cb(cb: CallbackQuery):
    if not is_admin(cb):
        await cb.answer("Нет доступа.", show_alert=True)
        return
    # admin:train_ml:sandbox:1.0:live:0.5  (пример)
    args = cb.data.split(":")[2:]
    sources = []
    weights = {}
    if not args:
        sources = ["sandbox", "live"]
        weights = {"sandbox": 0.5, "live": 1.0}
    else:
        for i in range(0, len(args), 2):
            if i+1 < len(args):
                sources.append(args[i])
                weights[args[i]] = float(args[i+1])
    from velayne.core.ml import train_from_logs
    meta = train_from_logs(sources=sources, weights=weights)
    if meta:
        await cb.answer("Обучение завершено.")
        await cb.message.answer(admin_model_metrics_message(meta), parse_mode="MarkdownV2")
    else:
        await cb.answer("Недостаточно данных для обучения.", show_alert=True)

# Кнопки для источников и весов
@router.callback_query(F.data == "admin:train_ml_controls")
async def admin_train_ml_controls_cb(cb: CallbackQuery):
    if not is_admin(cb):
        await cb.answer("Нет доступа.", show_alert=True)
        return
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("Sandbox 0.5", callback_data="admin:train_ml:sandbox:0.5"),
                InlineKeyboardButton("Live 1.0", callback_data="admin:train_ml:live:1.0"),
                InlineKeyboardButton("Both (default)", callback_data="admin:train_ml:sandbox:0.5:live:1.0"),
            ]
        ]
    )
    await cb.answer()
    await cb.message.answer("Выберите источники и веса для обучения:", reply_markup=kb)

# Show recommendations
@router.callback_query(F.data == "admin:mix_strat")
async def admin_mix_strat_cb(cb: CallbackQuery):
    if not is_admin(cb):
        await cb.answer("Нет доступа.", show_alert=True)
        return
    p = Path("data/models/strategy_mix.json")
    if not p.exists():
        await cb.message.answer("Нет рекомендаций.")
        return
    with open(p, "r", encoding="utf-8") as f:
        mix = json.load(f)
    await cb.message.answer(admin_strategy_mix_message(mix), parse_mode="MarkdownV2")

# Остальные admin callbacks не менялись