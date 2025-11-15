from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Настройки retriever микросервиса из .env файла"""

    # Qdrant настройки
    qdrant_host: str = ""
    qdrant_port: int = 6333
    qdrant_api_key: str | None = ""
    qdrant_collection_name: str = "documents"
    qdrant_timeout: int = 30

    # Retriever настройки
    prefetch_ratio: float = 1.0
    top_k: int = 20
    top_n: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Создаем экземпляр настроек
settings = Settings()
