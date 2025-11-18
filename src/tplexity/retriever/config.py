from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки retriever микросервиса из .env файла"""

    # Qdrant настройки
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str | None = "your qdrant api key here"
    qdrant_collection_name: str = "documents"
    qdrant_timeout: int = 60
    qdrant_connect_timeout: int = 10
    qdrant_read_timeout: int = 30
    qdrant_write_timeout: int = 30

    # Connection pooling настройки
    qdrant_pool_connections: int = 10
    qdrant_pool_maxsize: int = 20
    qdrant_max_keepalive_connections: int = 5
    qdrant_keepalive_expiry: float = 5.0

    # Retry настройки
    qdrant_max_retries: int = 3
    qdrant_retry_initial_delay: float = 1.0
    qdrant_retry_max_delay: float = 60.0
    qdrant_retry_exponential_base: float = 2.0
    qdrant_retry_jitter: bool = True

    # Retriever настройки
    prefetch_ratio: float = 1.0
    top_k: int = 20
    top_n: int = 10

    # Query reformulation настройки
    enable_query_reformulation: bool = True
    query_reformulation_llm_provider: str = "qwen"

    # Reranker настройки
    enable_reranker: bool = False

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Создаем экземпляр настроек
settings = Settings()
