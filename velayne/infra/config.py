import os
from pathlib import Path
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"

class Settings(BaseSettings):
    TG_TOKEN: str = ""
    ADMIN_ID: Optional[int] = None
    DB_URL: str = f"sqlite+aiosqlite:///{str(ROOT / 'data' / 'velayne.db')}"
    EXCHANGE_TESTNET: Optional[bool] = None
    SERVICE_MODE: str = "sandbox"
    LOG_DIR: str = str(ROOT / "logs")
    DATA_DIR: str = str(ROOT / "data")
    YOOKASSA_SHOP_ID: Optional[str] = ""
    YOOKASSA_SECRET_KEY: Optional[str] = ""
    # ... more as needed

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache(maxsize=1)
def get_settings():
    return Settings()

settings = get_settings()

def is_sandbox_mode() -> bool:
    return getattr(settings, "SERVICE_MODE", "sandbox").strip().lower() == "sandbox"

def _update_env_var(key, value):
    env_path = ENV_PATH
    lines = []
    found = False
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith(f"{key}="):
                    lines.append(f"{key}={value}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"{key}={value}\n")
    tmp = str(env_path) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.writelines(lines)
    os.replace(tmp, env_path)

def toggle_sandbox_mode():
    """
    Переключает SERVICE_MODE в .env и обновляет settings.
    Возвращает новое значение (True если sandbox, False если live).
    """
    new_mode = "live" if is_sandbox_mode() else "sandbox"
    _update_env_var("SERVICE_MODE", new_mode)
    global settings
    settings = get_settings.cache_clear() or get_settings()
    return is_sandbox_mode()

def reload_components():
    # Имитация рестарта компонентов
    import logging
    logging.info("[СЕРВИС] Рестарт компонентов инициирован (имитация).")