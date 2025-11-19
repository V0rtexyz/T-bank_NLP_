from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки generation микросервиса из .env файла"""

    # LLM настройки
    llm_provider: str = "deepseek"

    # Retriever API настройки
    retriever_api_url: str = "http://localhost:8010"
    retriever_api_timeout: float = 60.0

    # Redis настройки
    redis_host: str = "redis"
    redis_port: int = 6379  # Внутри Docker сети Redis слушает на стандартном порту 6379
    redis_db: int = 0
    redis_password: str | None = None
    session_ttl: int = 86400  # 24 часа в секундах
    max_history_messages: int = 10  # Максимум 10 сообщений (5 пар запрос-ответ)

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Создаем экземпляр настроек
settings = Settings()
