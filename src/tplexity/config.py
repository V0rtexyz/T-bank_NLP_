from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""

    # Qdrant настройки
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str | None = None
    qdrant_collection_name: str = "documents"
    qdrant_timeout: int = 30

    # Retrieval настройки
    prefetch_ratio: float = 1.0  # Во сколько раз больше результатов для prefetch
    top_k: int = 10  # Количество результатов для гибридного поиска
    top_n: int = 10  # Количество результатов для reranking

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


settings = Settings()
