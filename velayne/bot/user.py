from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from velayne.infra.db import get_or_create_user, upsert_strategy_pref
from velayne.infra.config import settings
from .ui import mode_switch_message, preset_profiles_message, dashboard_message
from velayne.infra.i18n import tr, available_langs
import pytz

router = Router()

@router.message(Command("tz"))
async def tz_cmd(msg: Message):
    user = await get_or_create_user(msg.from_user.id)
    tz_list = pytz.all_timezones
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(tz, callback_data=f"tz:{tz}")] for tz in tz_list[:20]])
    await msg.answer(tr("select_tz", getattr(user, "lang", "en")), reply_markup=kb)

@router.callback_query(F.data.regexp(r"tz:.+"))
async def tz_set_cb(cb: CallbackQuery):
    tz = cb.data.split(":", 1)[1]
    user = await get_or_create_user(cb.from_user.id)
    # Сохраняем TZ в Setting/user
    await cb.answer(tr("tz_set", getattr(user, "lang", "en")).format(tz=tz))
    await cb.message.answer(tr("tz_reports", getattr(user, "lang", "en")).format(tz=tz))

@router.message(Command("lang"))
async def lang_cmd(msg: Message):
    user = await get_or_create_user(msg.from_user.id)
    langs = available_langs()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(lang.upper(), callback_data=f"lang:{lang}")] for lang in langs])
    await msg.answer("Choose language / Выберите язык:", reply_markup=kb)

@router.callback_query(F.data.regexp(r"lang:.+"))
async def lang_set_cb(cb: CallbackQuery):
    lang = cb.data.split(":",1)[1]
    user = await get_or_create_user(cb.from_user.id)
    # сохранить lang в Setting/user
    await cb.answer(f"Language set: {lang.upper()}")
    await cb.message.answer(tr("welcome", lang))

# --- Preset profiles ---

PRESET_PROFILES = {
    "conservative": {
        "label": "🟢 " + tr("profile_conservative", "ru"),
        "desc": tr("desc_conservative", "ru"),
        "strategies": ["ema_crossover", "mean_reversion"],
        "risk_profile": {"risk_cap_fraction": 0.01, "circuit_dd": 0.1}
    },
    "balanced": {
        "label": "🟡 " + tr("profile_balanced", "ru"),
        "desc": tr("desc_balanced", "ru"),
        "strategies": ["ema_crossover", "mean_reversion", "breakout", "momentum"],
        "risk_profile": {"risk_cap_fraction": 0.03, "circuit_dd": 0.15}
    },
    "aggressive": {
        "label": "🔴 " + tr("profile_aggressive", "ru"),
        "desc": tr("desc_aggressive", "ru"),
        "strategies": ["ema_crossover", "mean_reversion", "breakout", "momentum", "grid", "scalping", "arbitrage", "event_based"],
        "risk_profile": {"risk_cap_fraction": 0.07, "circuit_dd": 0.25}
    },
}

@router.message(Command("preset"))
async def preset_cmd(msg: Message):
    user = await get_or_create_user(msg.from_user.id)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f"{d['label']}", callback_data=f"preset:{k}")] for k, d in PRESET_PROFILES.items()
    ])
    await msg.answer(preset_profiles_message(getattr(user, "lang", "en")), reply_markup=kb)

@router.callback_query(F.data.regexp(r"preset:(\w+)"))
async def preset_apply_cb(cb: CallbackQuery):
    code = cb.data.split(":")[1]
    user = await get_or_create_user(cb.from_user.id)
    profile = PRESET_PROFILES.get(code)
    if not profile:
        await cb.answer(tr("profile_not_found", getattr(user, "lang", "en")), show_alert=True)
        return
    upsert_strategy_pref(
        session=user.session,
        user_id=user.id,
        enabled_codes=profile["strategies"],
        last_recommended={"risk_profile": profile["risk_profile"]}
    )
    await cb.answer(tr("profile_applied", getattr(user, "lang", "en")).format(profile=profile['label']), show_alert=True)
    await cb.message.answer(
        f"✅ {tr('profile_applied', getattr(user, 'lang', 'en')).format(profile=profile['label'])}\n"
        f"{tr('strategies', getattr(user, 'lang', 'en'))}: {', '.join(profile['strategies'])}\n"
        f"{tr('risk_params', getattr(user, 'lang', 'en'))}: {profile['risk_profile']}"
    )

@router.message(Command("dashboard"))
async def dashboard_cmd(msg: Message):
    user = await get_or_create_user(msg.from_user.id)
    url = "http://127.0.0.1:8686"
    await msg.answer(dashboard_message(url, getattr(user, "lang", "en")))