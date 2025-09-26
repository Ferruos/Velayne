from datetime import datetime
import pytz
from velayne.infra.i18n import tr

def _format_dt(dt: datetime, tz: str = "UTC", lang: str = "en") -> str:
    try:
        tzinfo = pytz.timezone(tz)
        dt = dt.replace(tzinfo=pytz.UTC).astimezone(tzinfo)
    except Exception:
        pass
    fmt = "%d.%m.%Y %H:%M" if lang == "ru" else "%Y-%m-%d %H:%M"
    return dt.strftime(fmt)

def show_portfolio_summary(summary: dict, tz: str = "UTC", lang: str = "en") -> str:
    txt = "<b>" + tr("portfolio_user", lang) + "</b>\n"
    for kind, acc in summary.items():
        if kind.startswith("total"):
            continue
        label = "DEMO" if kind == "demo" else "LIVE"
        txt += f"<b>{label}:</b> {tr('balance', lang)}: {acc['balance']:.2f} | {tr('trades', lang)}: {acc['n_trades']} | {tr('created', lang)}: {_format_dt(acc['created_at'], tz, lang)}\n"
    txt += f"<b>{tr('total_balance', lang)}:</b> {summary.get('total_balance', 0):.2f}\n"
    return txt

def preset_profiles_message(lang: str = "en") -> str:
    txt = "<b>" + tr("ready_profiles", lang) + "</b>:\n\n"
    txt += "🟢 <b>" + tr("profile_conservative", lang) + "</b>: " + tr("desc_conservative", lang) + "\n"
    txt += "🟡 <b>" + tr("profile_balanced", lang) + "</b>: " + tr("desc_balanced", lang) + "\n"
    txt += "🔴 <b>" + tr("profile_aggressive", lang) + "</b>: " + tr("desc_aggressive", lang) + "\n\n"
    txt += tr("choose_style", lang)
    return txt

def admin_model_metrics_message(meta: dict, lang: str = "en") -> str:
    if not meta:
        return tr("no_training_data", lang)
    txt = f"*{tr('model_overall', lang)}:*\n"
    txt += f"- {tr('version', lang)}: {meta.get('version','?')}\n"
    txt += f"- {tr('date', lang)}: {meta.get('updated','?')}\n"
    txt += f"- AUC: {meta.get('auc',0):.3f}\n"
    txt += f"- {tr('accuracy', lang)}: {meta.get('accuracy',0):.3f}\n"
    txt += f"- F1: {meta.get('f1',0):.3f}\n"
    txt += f"- {tr('threshold', lang)}: {meta.get('best_thresh',0.5):.2f}\n"
    txt += f"- N = {meta.get('sample_count', '?')}\n"
    if "sources" in meta and meta["sources"]:
        txt += f"\n*{tr('by_sources', lang)}:*\n"
        txt += "| " + tr('source', lang) + " | AUC | Acc | F1 | N |\n"
        txt += "|----------|-----|-----|----|---|\n"
        for src, m in meta["sources"].items():
            txt += f"| {src} | {m['auc']:.3f} | {m['accuracy']:.3f} | {m['f1']:.3f} | {m['count']} |\n"
    return f"```\n{txt}```"

def dashboard_message(url: str, lang: str = "en") -> str:
    return tr("dashboard_hint", lang, url=url)

def mode_switch_message(new_mode: str, lang: str = "en") -> str:
    if new_mode == "live":
        return tr("mode_live", lang)
    elif new_mode == "sandbox":
        return tr("mode_sandbox", lang)
    else:
        return tr("mode_switched", lang, mode=new_mode)