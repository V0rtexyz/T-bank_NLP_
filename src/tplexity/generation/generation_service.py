import logging
from typing import Literal

import httpx

from tplexity.generation.config import settings
from tplexity.llm_client import get_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Ты - полезный AI-ассистент. Отвечай на вопросы пользователя на основе предоставленного контекста.
Если в контексте нет информации для ответа, честно скажи об этом.
"""


class RetrieverClient:
    """Клиент для взаимодействия с Retriever API"""

    def __init__(self, base_url: str, timeout: float = 30.0):
        """
        Инициализация клиента

        Args:
            base_url: Базовый URL Retriever API (например, http://localhost:8000)
            timeout: Таймаут запросов в секундах
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        logger.info(f"🔄 [retriever_client] Инициализирован клиент для {self.base_url}")

    async def search(
        self, query: str, top_k: int | None = None, top_n: int | None = None, use_rerank: bool = True
    ) -> list[tuple[str, float, str, dict | None]]:
        """
        Поиск релевантных документов

        Args:
            query: Поисковый запрос
            top_k: Количество документов до реранка
            top_n: Количество документов после реранка
            use_rerank: Использовать ли reranking

        Returns:
            list[tuple[str, float, str, dict | None]]: Список кортежей (doc_id, score, text, metadata)
        """
        payload = {
            "query": query,
            "use_rerank": use_rerank,
        }

        if top_k is not None:
            payload["top_k"] = top_k
        if top_n is not None:
            payload["top_n"] = top_n

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/retriever/search", json=payload)
                response.raise_for_status()

                data = response.json()
                results = data.get("results", [])

                # Преобразуем в формат (doc_id, score, text, metadata)
                return [(r["doc_id"], r["score"], r["text"], r.get("metadata")) for r in results]

        except httpx.TimeoutException:
            logger.error(f"⏱️ [retriever_client] Таймаут при запросе к Retriever API")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ [retriever_client] HTTP ошибка от Retriever API: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ [retriever_client] Ошибка при запросе к Retriever API: {e}")
            raise


class GenerationService:
    """Сервис для генерации ответов с использованием RAG (Retrieval-Augmented Generation)

    Процесс:
    1. Получает запрос пользователя
    2. Использует RetrieverService для поиска релевантных документов
    3. Формирует промпт с контекстом
    4. Генерирует ответ через LLM
    """

    def __init__(
        self,
        llm_provider: Literal["qwen", "yandexgpt", "chatgpt", "gemini"] | None = None,
        retriever_url: str | None = None,
    ):
        """
        Инициализация сервиса генерации

        Args:
            llm_provider (Literal["qwen", "yandexgpt", "chatgpt", "gemini"] | None): Провайдер LLM
            retriever_url (str | None): URL Retriever API (если None, берется из config)
        """
        logger.info("🔄 [generation_service] Инициализация сервиса генерации")

        # Инициализируем клиент для Retriever API
        retriever_url = retriever_url or settings.retriever_api_url
        self.retriever_client = RetrieverClient(retriever_url, timeout=settings.retriever_api_timeout)

        # Выбираем провайдер LLM
        self.llm_provider = llm_provider or settings.llm_provider
        self.llm_client = get_llm(self.llm_provider)

        logger.info(f"✅ [generation_service] Сервис генерации инициализирован: provider={self.llm_provider}")

    def _build_prompt(self, query: str, context_documents: list[tuple[str, float, str, dict | None]]) -> str:
        """
        Формирует промпт с контекстом для LLM

        Args:
            query: Запрос пользователя
            context_documents: Список кортежей (doc_id, score, text, metadata)

        Returns:
            str: Сформированный промпт
        """
        # Формируем контекст из документов
        context_parts = []
        for idx, (doc_id, score, text, _metadata) in enumerate(context_documents, 1):
            context_parts.append(f"[Документ {idx} (ID: {doc_id}, релевантность: {score:.3f})]\n{text}")

        context = "\n\n".join(context_parts)

        # Формируем финальный промпт
        prompt = f"""Контекст:
{context}

Вопрос пользователя: {query}

Ответь на вопрос пользователя на основе предоставленного контекста. Если в контексте нет информации для ответа, честно скажи об этом."""

        return prompt

    async def _call_llm(
        self, messages: list[dict[str, str]], temperature: float | None = None, max_tokens: int | None = None
    ) -> str:
        """
        Вызов LLM через LLMClient

        Args:
            messages: Список сообщений в формате OpenAI
            temperature: Температура генерации (если None, используется из settings.llm)
            max_tokens: Максимальное количество токенов (если None, используется из settings.llm)

        Returns:
            str: Сгенерированный ответ
        """
        logger.debug("🔄 [generation_service] Отправка запроса к LLM")
        return await self.llm_client.generate(messages, temperature=temperature, max_tokens=max_tokens)

    async def generate(
        self,
        query: str,
        top_k: int | None = None,
        use_rerank: bool | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> tuple[str, list[str], list[dict | None]]:
        """
        Генерация ответа с использованием RAG

        Args:
            query: Запрос пользователя
            top_k: Количество документов для контекста (если None, используется значение из retriever config)
            use_rerank: Использовать ли reranking (если None, используется True по умолчанию)
            temperature: Температура генерации (если None, используется значение из llm config)
            max_tokens: Максимальное количество токенов (если None, используется значение из llm config)

        Returns:
            tuple[str, list[str], list[dict | None]]: (ответ, список doc_ids, список метаданных)

        Raises:
            ValueError: Если запрос пуст
        """
        if not query or not query.strip():
            raise ValueError("Запрос не может быть пустым")

        # Если use_rerank не указан, используем True по умолчанию
        use_rerank = use_rerank if use_rerank is not None else True

        logger.info(f"🔄 [generation_service] Начало генерации для запроса: {query[:50]}...")

        # Шаг 1: Поиск релевантных документов через Retriever API
        logger.debug(f"🔍 [generation_service] Поиск релевантных документов, top_k={top_k}, use_rerank={use_rerank}")
        context_documents = await self.retriever_client.search(
            query=query, top_k=top_k, top_n=top_k, use_rerank=use_rerank
        )

        if not context_documents:
            logger.warning("⚠️ [generation_service] Не найдено релевантных документов")
            return (
                "К сожалению, я не нашел релевантной информации в базе знаний для ответа на ваш вопрос.",
                [],
                [],
            )

        logger.info(f"✅ [generation_service] Найдено {len(context_documents)} релевантных документов")

        # Шаг 2: Формирование промпта
        logger.debug("🔄 [generation_service] Формирование промпта с контекстом")
        prompt = self._build_prompt(query, context_documents)

        # Шаг 3: Генерация ответа через LLM
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        logger.debug("🔄 [generation_service] Генерация ответа через LLM")
        answer = await self._call_llm(messages, temperature=temperature, max_tokens=max_tokens)
        logger.info("✅ [generation_service] Ответ успешно сгенерирован")

        # Извлекаем источники (всегда включаем)
        doc_ids = [doc_id for doc_id, _, _, _ in context_documents]
        metadatas = [metadata for _, _, _, metadata in context_documents]

        return answer, doc_ids, metadatas

    async def close(self) -> None:
        """Закрытие LLM клиента"""
        if hasattr(self, "llm_client") and hasattr(self.llm_client, "client"):
            await self.llm_client.client.close()
