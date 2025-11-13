from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""

    # Qdrant настройки
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str | None = None
    qdrant_collection_name: str = "documents"
    qdrant_timeout: int = 30

    # Embeddings настройки
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # BM25 настройки
    bm25_k1: float = 1.5
    bm25_b: float = 0.75

    # RRF настройки
    rrf_k: int = 60

    # Rerank настройки
    rerank_model_name: str | None = None
    rerank_top_k: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


settings = Settings()
