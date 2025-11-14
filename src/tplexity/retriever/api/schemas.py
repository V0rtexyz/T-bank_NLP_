"""Pydantic схемы для retriever API"""

from pydantic import BaseModel, Field


class DocumentRequest(BaseModel):
    """Схема для добавления документа"""

    text: str = Field(..., description="Текст документа")
    metadata: dict | None = Field(default=None, description="Метаданные документа")


class DocumentsRequest(BaseModel):
    """Схема для добавления нескольких документов"""

    documents: list[DocumentRequest] = Field(..., description="Список документов для добавления")


class SearchRequest(BaseModel):
    """Схема для поискового запроса"""

    query: str = Field(..., description="Поисковый запрос")
    top_k: int = Field(default=10, ge=1, le=200, description="Количество документов до реранка")
    top_n: int = Field(default=10, ge=1, le=100, description="Количество документов после реранка (возвращаемые)")
    use_rerank: bool = Field(default=True, description="Использовать ли reranking")


class SearchResult(BaseModel):
    """Схема для результата поиска"""

    doc_id: str = Field(..., description="ID документа")
    score: float = Field(..., description="Релевантность документа")
    text: str = Field(..., description="Текст документа")
    metadata: dict | None = Field(default=None, description="Метаданные документа")


class SearchResponse(BaseModel):
    """Схема для ответа поиска"""

    results: list[SearchResult] = Field(..., description="Список результатов поиска")
    total: int = Field(..., description="Общее количество результатов")


class DeleteDocumentsRequest(BaseModel):
    """Схема для удаления документов"""

    doc_ids: list[str] = Field(..., description="Список ID документов для удаления")


class MessageResponse(BaseModel):
    """Схема для сообщений об успешных операциях"""

    message: str = Field(..., description="Сообщение")
    success: bool = Field(default=True, description="Успешность операции")
