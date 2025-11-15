from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Настройки Telegram Bot микросервиса из .env файла"""

    # Telegram Bot настройки
    bot_token: str = Field(default="")
    
    @field_validator('bot_token', mode='before')
    @classmethod
    def parse_bot_token(cls, v):
        # Если передана пустая строка или None, используем дефолтное значение
        if v == '' or v is None:
            return ""
        return v

    # Generation API настройки
    generation_api_url: str = "http://localhost:8002"
    generation_api_timeout: float = 60.0

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Создаем экземпляр настроек
settings = Settings()
