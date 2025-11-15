from typing import Literal
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки generation микросервиса из .env файла"""

    # LLM настройки
    llm_provider: Literal["qwen", "yandexgpt", "chatgpt", "gemini"] = "chatgpt"

    # Retriever API настройки
    retriever_api_url: str = "http://localhost:8000"
    retriever_api_timeout: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Создаем экземпляр настроек
settings = Settings()
