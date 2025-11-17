from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки retriever микросервиса из .env файла"""

    # Qdrant настройки
    qdrant_host: str = "8b725c10-321f-428c-8fc8-00160f7dff00.eu-central-1-0.aws.cloud.qdrant.io"
    qdrant_port: int = 6333
    qdrant_api_key: str | None = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.-UBQoLGrgkXii0DuFq-4EWTiBNAme7CHdgFPIryHj94"
    qdrant_collection_name: str = "documents"
    qdrant_timeout: int = 60

    # Retriever настройки
    prefetch_ratio: float = 1.0
    top_k: int = 20
    top_n: int = 10

    # Query reformulation настройки
    enable_query_reformulation: bool = True
    query_reformulation_llm_provider: str = "qwen"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Создаем экземпляр настроек
settings = Settings()
