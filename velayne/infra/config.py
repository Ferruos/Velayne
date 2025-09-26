from pydantic_settings import BaseSettings
from enum import Enum

class Role(str, Enum):
    user = "user"
    editor = "editor"
    admin = "admin"

class Settings(BaseSettings):
    TG_TOKEN: str = ""
    ADMIN_ID: int = 0
    DB_URL: str = "sqlite+aiosqlite:///data/velayne.db"
    ENCRYPTION_KEY: str = ""
    LOG_DIR: str = "logs"
    DATA_DIR: str = "data"
    YOOKASSA_SHOP_ID: str = ""
    YOOKASSA_SECRET: str = ""
    LOG_RETENTION_DAYS: int = 14
    DATA_RETENTION_DAYS: int = 30
    NEWS_CACHE_RETENTION_DAYS: int = 14
    MODELS_KEEP_LAST: int = 5
    DISK_SOFT_LIMIT_GB: float = 5
    EXCHANGE_TESTNET: bool = True
    DEFAULT_TZ: str = "UTC"
    ORDER_QUEUE_MAX_PARALLEL: int = 3
    ORDER_QUEUE_MAX_PER_SEC: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()