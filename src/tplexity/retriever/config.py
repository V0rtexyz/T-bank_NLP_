from pydantic import BaseModel, Field


class RetrieverSettings(BaseModel):
    """Настройки для retriever микросервиса"""

    # Qdrant настройки
    qdrant_host: str = Field(default="localhost", description="Хост Qdrant сервера")
    qdrant_port: int = Field(default=6333, ge=1, le=65535, description="Порт Qdrant сервера")
    qdrant_api_key: str | None = Field(default=None, description="API ключ для Qdrant")
    qdrant_collection_name: str = Field(default="documents", description="Имя коллекции в Qdrant")
    qdrant_timeout: int = Field(default=30, ge=1, description="Таймаут подключения к Qdrant в секундах")

    # Retriever настройки
    prefetch_ratio: float = Field(
        default=1.0, ge=1.0, le=10.0, description="Во сколько раз документов для prefetch больше по сравнению с top_k"
    )
    top_k: int = Field(default=20, ge=1, le=1000, description="Количество документов до реранка")
    top_n: int = Field(default=10, ge=1, le=500, description="Количество документов после реранка (возвращаемые)")
