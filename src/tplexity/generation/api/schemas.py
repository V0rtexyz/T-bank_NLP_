"""Pydantic схемы для generation API"""

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Схема для запроса генерации ответа"""

    query: str = Field(..., description="Вопрос пользователя")
    top_k: int | None = Field(
        default=None,
        ge=1,
        le=20,
        description="Количество релевантных документов для использования в контексте (если не указано, используется значение из config)",
    )
    use_rerank: bool | None = Field(
        default=None,
        description="Использовать ли reranking при поиске документов (если не указано, используется значение из config)",
    )
    temperature: float | None = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Температура для генерации (если не указано, используется значение из config)",
    )
    max_tokens: int | None = Field(
        default=None,
        ge=1,
        le=4000,
        description="Максимальное количество токенов в ответе (если не указано, используется значение из config)",
    )


class SourceInfo(BaseModel):
    """Схема для информации об источнике"""

    doc_id: str = Field(..., description="ID документа")
    metadata: dict | None = Field(default=None, description="Метаданные документа")


class GenerateResponse(BaseModel):
    """Схема для ответа генерации"""

    answer: str = Field(..., description="Сгенерированный ответ")
    sources: list[SourceInfo] = Field(default_factory=list, description="Список источников (doc_ids и метаданные)")
    query: str = Field(..., description="Исходный запрос пользователя")
