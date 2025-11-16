from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

# Импортируем настройки из llm_client для получения списка доступных моделей
try:
    from tplexity.llm_client.config import settings as llm_settings
except ImportError:
    # Fallback если импорт не удался
    llm_settings = None


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
    generation_api_url: str = "http://localhost:8012"
    generation_api_timeout: float = 60.0

    @property
    def available_models(self) -> list[str]:
        """Получает список доступных моделей из llm_client настроек"""
        if llm_settings and hasattr(llm_settings, 'available_models'):
            return llm_settings.available_models
        # Fallback если llm_settings недоступен
        return ["qwen"]

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Создаем экземпляр настроек
settings = Settings()
