"""Роутеры для generation микросервиса"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from tplexity.generation.api.dependencies import get_generation
from tplexity.generation.api.schemas import GenerateRequest, GenerateResponse, SourceInfo
from tplexity.generation.generation_service import GenerationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generation", tags=["generation"])


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    generation: GenerationService = Depends(get_generation),
) -> GenerateResponse:
    """
    Генерация ответа с использованием RAG (Retrieval-Augmented Generation)

    Процесс:
    1. Поиск релевантных документов через retriever
    2. Формирование промпта с контекстом
    3. Генерация ответа через LLM

    Args:
        request: Запрос с вопросом пользователя и параметрами
        generation: Экземпляр GenerationService

    Returns:
        GenerateResponse: Сгенерированный ответ с источниками
    """
    try:
        answer, doc_ids, metadatas = await generation.generate(
            query=request.query,
            top_k=request.top_k,
            use_rerank=request.use_rerank,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            llm_provider=request.llm_provider,
        )

        # Формируем список источников (всегда включаем)
        sources = []
        for doc_id, metadata in zip(doc_ids, metadatas, strict=False):
            sources.append(SourceInfo(doc_id=doc_id, metadata=metadata))

        logger.info(f"✅ [generation.api] Ответ успешно сгенерирован для запроса: {request.query[:50]}...")
        return GenerateResponse(
            answer=answer,
            sources=sources,
            query=request.query,
        )
    except ValueError as e:
        logger.error(f"❌ [generation.api] Ошибка валидации: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"❌ [generation.api] Ошибка при генерации ответа: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при генерации ответа: {str(e)}",
        ) from e
