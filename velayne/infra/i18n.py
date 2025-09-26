from typing import Dict

_LANGS = ['en', 'ru']
_DEFAULT = 'en'

_TRANSLATIONS = {
    "en": {
        "welcome": "Welcome to Velayne!",
        "select_tz": "Please select your timezone:",
        "profile_applied": "Profile '{profile}' has been applied!",
        "dashboard_hint": "To open the dashboard locally: {url}\nOr via SSH tunnel:\nssh -L 8686:localhost:8686 user@server",
        "export_ready": "Your data export is ready: {path}",
    },
    "ru": {
        "welcome": "Добро пожаловать в Velayne!",
        "select_tz": "Пожалуйста, выберите ваш часовой пояс:",
        "profile_applied": "Профиль '{profile}' применён!",
        "dashboard_hint": "Откройте дашборд локально: {url}\nИли через SSH туннель:\nssh -L 8686:localhost:8686 user@server",
        "export_ready": "Ваш экспорт данных готов: {path}",
    },
    # place for more languages
}

def tr(key: str, lang: str = None, **kwargs) -> str:
    lang = lang or _DEFAULT
    d = _TRANSLATIONS.get(lang, _TRANSLATIONS[_DEFAULT])
    val = d.get(key, key)
    return val.format(**kwargs)

def available_langs() -> Dict[str, str]:
    return {k: k.upper() for k in _TRANSLATIONS}