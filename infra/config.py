"""Configuration management using pydantic-settings."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/velayne.db",
        description="Database connection URL"
    )
    
    # Encryption
    encryption_key: str = Field(
        default="",
        description="Fernet encryption key for sensitive data"
    )
    
    # Application Settings
    app_name: str = Field(default="Velayne", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Directory Paths
    logs_dir: Path = Field(default=Path("./logs"), description="Logs directory")
    data_dir: Path = Field(default=Path("./data"), description="Data directory")
    models_dir: Path = Field(default=Path("./models"), description="Models directory")
    
    # Optional Telegram Bot
    telegram_bot_token: Optional[str] = Field(
        default=None,
        description="Telegram bot token"
    )
    
    # Optional Payment Provider
    yookassa_shop_id: Optional[str] = Field(
        default=None,
        description="YooKassa shop ID"
    )
    yookassa_secret_key: Optional[str] = Field(
        default=None,
        description="YooKassa secret key"
    )
    
    def __init__(self, **kwargs):
        """Initialize settings and ensure paths are Path objects."""
        super().__init__(**kwargs)
        # Convert string paths to Path objects if needed
        if isinstance(self.logs_dir, str):
            self.logs_dir = Path(self.logs_dir)
        if isinstance(self.data_dir, str):
            self.data_dir = Path(self.data_dir)
        if isinstance(self.models_dir, str):
            self.models_dir = Path(self.models_dir)


# Global settings instance
settings = Settings()