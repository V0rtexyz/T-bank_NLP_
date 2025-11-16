"""Pydantic схемы для generation API"""

from typing import Literal

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
    llm_provider: Literal["qwen", "yandexgpt", "chatgpt", "gemini"] | None = Field(
        default=None,
        description="Провайдер LLM для использования (если не указано, используется значение из config)",
    )
    session_id: str | None = Field(
        default=None,
        description="Идентификатор сессии для сохранения истории диалога (если не указано, история не сохраняется)",
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


class ClearSessionRequest(BaseModel):
    """Схема для запроса очистки истории сессии"""

    session_id: str = Field(..., description="Идентификатор сессии для очистки")


class ClearSessionResponse(BaseModel):
    """Схема для ответа очистки истории сессии"""

    success: bool = Field(..., description="Успешность операции")
    message: str = Field(..., description="Сообщение о результате")
