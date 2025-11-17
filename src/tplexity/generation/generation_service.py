import logging
from datetime import datetime

import httpx

from tplexity.generation.config import settings
from tplexity.generation.memory_service import MemoryService
from tplexity.generation.prompts import (
    REACT_DECISION_PROMPT,
    SYSTEM_PROMPT_WITHOUT_RETRIEVER,
    SYSTEM_PROMPT_WITH_RETRIEVER,
    USER_PROMPT,
)
from tplexity.llm_client import get_llm

logger = logging.getLogger(__name__)


class RetrieverClient:
    """Клиент для взаимодействия с Retriever API"""

    def __init__(self, base_url: str, timeout: float = 60.0):
        """
        Инициализация клиента

        Args:
            base_url: Базовый URL Retriever API (например, http://localhost:8010)
            timeout: Таймаут запросов в секундах
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        logger.info(f"🔄 [retriever_client] Инициализирован клиент для {self.base_url}")

    async def search(
        self,
        query: str,
        top_k: int | None = None,
        top_n: int | None = None,
        use_rerank: bool = True,
        messages: list[dict[str, str]] | None = None,
    ) -> list[tuple[str, float, str, dict | None]]:
        """
        Поиск релевантных документов

        Args:
            query: Поисковый запрос
            top_k: Количество документов до реранка
            top_n: Количество документов после реранка
            use_rerank: Использовать ли reranking
            messages: История диалога для переформулирования запроса

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
        if messages is not None:
            payload["messages"] = messages

        try:
            timeout_config = httpx.Timeout(self.timeout)
            async with httpx.AsyncClient(timeout=timeout_config) as client:
                response = await client.post(f"{self.base_url}/retriever/search", json=payload)
                response.raise_for_status()

                data = response.json()
                results = data.get("results", [])

                # Преобразуем в формат (doc_id, score, text, metadata)
                return [(r["doc_id"], r["score"], r["text"], r.get("metadata")) for r in results]

        except httpx.TimeoutException:
            logger.error("⏱️ [retriever_client] Таймаут при запросе к Retriever API")
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
        llm_provider: str | None = None,
        retriever_url: str | None = None,
        memory_service: MemoryService | None = None,
    ):
        """
        Инициализация сервиса генерации

        Args:
            llm_provider (str | None): Провайдер LLM (если None, берется из config)
            retriever_url (str | None): URL Retriever API (если None, берется из config)
            memory_service (MemoryService | None): Сервис для работы с памятью диалогов
        """
        logger.info("🔄 [generation_service] Инициализация сервиса генерации")

        # Инициализируем клиент для Retriever API
        retriever_url = retriever_url or settings.retriever_api_url
        self.retriever_client = RetrieverClient(retriever_url, timeout=settings.retriever_api_timeout)

        # Выбираем провайдер LLM
        self.llm_provider = llm_provider or settings.llm_provider
        self.llm_client = get_llm(self.llm_provider)

        # Инициализируем сервис памяти
        self.memory_service = memory_service or MemoryService()

        logger.info(f"✅ [generation_service] Сервис генерации инициализирован: provider={self.llm_provider}")

    async def _should_use_retriever(
        self, query: str, session_id: str | None = None, llm_provider: str | None = None
    ) -> bool:
        """
        ReAct агент: решает, нужен ли retriever для ответа на запрос

        Args:
            query (str): Запрос пользователя
            session_id (str | None): Идентификатор сессии для получения истории диалога
            llm_provider (str | None): Провайдер LLM для принятия решения

        Returns:
            bool: True если нужен retriever, False если не нужен
        """
        
        history_text = "Истории диалога нет."
        if session_id:
            history = await self.memory_service.get_history(session_id)
            if history:
                history_messages = []
                for message in history:
                    role = message.get("role", "unknown")
                    content = message.get("content", "")
                    if role == "user":
                        history_messages.append(f"Пользователь: {content}")
                    elif role == "assistant":
                        history_messages.append(f"Ассистент: {content}")
                history_text = "\n".join(history_messages) if history_messages else "Истории диалога нет."

        decision_prompt = REACT_DECISION_PROMPT.format(history=history_text, query=query)

        provider = llm_provider or self.llm_provider
        llm_client = get_llm(provider)

        messages = [{"role": "user", "content": decision_prompt}]
        logger.debug("🤔 [generation_service] ReAct агент анализирует необходимость retriever")

        try:
            decision = await llm_client.generate(messages, temperature=0.0, max_tokens=10)
            decision = decision.strip().upper()

            use_retriever = decision.startswith("YES")
            logger.info(
                f"✅ [generation_service] ReAct агент решил: {'использовать' if use_retriever else 'НЕ использовать'} retriever"
            )
            return use_retriever
        except Exception as e:
            logger.warning(
                f"⚠️ [generation_service] Ошибка при принятии решения ReAct агентом: {e}. Используется retriever по умолчанию."
            )
            return True

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

        # Получаем текущее время и используем промпт из prompts.py
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return USER_PROMPT.format(context=context, query=query, current_time=current_time)

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

    async def generate(  # noqa: C901
        self,
        query: str,
        top_k: int | None = None,
        use_rerank: bool | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        llm_provider: str | None = None,
        session_id: str | None = None,
    ) -> tuple[str, list[str], list[dict | None]]:
        """
        Генерация ответа с использованием RAG

        Args:
            query: Запрос пользователя
            top_k: Количество документов для контекста (если None, используется значение из retriever config)
            use_rerank: Использовать ли reranking (если None, используется True по умолчанию)
            temperature: Температура генерации (если None, используется значение из llm config)
            max_tokens: Максимальное количество токенов (если None, используется значение из llm config)
            llm_provider: Провайдер LLM для использования (если None, используется значение из self.llm_provider)
            session_id: Идентификатор сессии для сохранения истории диалога (если None, история не сохраняется)

        Returns:
            tuple[str, list[str], list[dict | None]]: (ответ, список doc_ids, список метаданных)

        Raises:
            ValueError: Если запрос пуст
        """
        if not query or not query.strip():
            raise ValueError("Запрос не может быть пустым")

        # Если use_rerank не указан, используем True по умолчанию
        use_rerank = use_rerank if use_rerank is not None else True

        # Выбираем провайдер LLM (если указан в запросе, используем его, иначе используем из self)
        provider = llm_provider or self.llm_provider
        if llm_provider:
            logger.info(
                f"🔄 [generation_service] Получен запрос с llm_provider={llm_provider}, будет использован провайдер: {provider}"
            )
        else:
            logger.info(
                f"🔄 [generation_service] Запрос без указания llm_provider, используется провайдер по умолчанию: {provider}"
            )
        logger.info(f"🔄 [generation_service] Начало генерации для запроса: {query[:50]}...")

        use_retriever = await self._should_use_retriever(query, session_id, llm_provider)

        context_documents = []
        if use_retriever:
            # Получаем историю диалога для передачи в retriever (если указан session_id)
            messages = None
            if session_id:
                history = await self.memory_service.get_history(session_id)
                if history:
                    messages = [message for message in history if message.get("role") != "system"]

            # Шаг 1: Поиск релевантных документов через Retriever API
            logger.debug(f"🔍 [generation_service] Поиск релевантных документов, top_k={top_k}, use_rerank={use_rerank}")
            context_documents = await self.retriever_client.search(
                query=query, top_k=top_k, top_n=top_k, use_rerank=use_rerank, messages=messages
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
        logger.debug("🔄 [generation_service] Формирование промпта")
        if context_documents:
            prompt = self._build_prompt(query, context_documents)
        else:
            # Если retriever не использовался, формируем промпт без контекста
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prompt = f"Вопрос пользователя: {query}\n\nТекущее время: {current_time}"

        # Шаг 3: Выбираем правильный системный промпт в зависимости от использования retriever
        system_prompt = SYSTEM_PROMPT_WITH_RETRIEVER if context_documents else SYSTEM_PROMPT_WITHOUT_RETRIEVER
        logger.debug(
            f"📝 [generation_service] Используется системный промпт: {'с retriever' if context_documents else 'без retriever'}"
        )

        # Шаг 4: Формируем список сообщений для LLM
        # Всегда добавляем системный промпт в начале
        messages = [{"role": "system", "content": system_prompt}]

        # Получаем историю диалога из памяти (если указан session_id)
        if session_id:
            history = await self.memory_service.get_history(session_id)
            if history:
                for message in history:
                    role = message.get("role")
                    if role in ("user", "assistant"):
                        messages.append({"role": role, "content": message.get("content", "")})
                logger.info(f"📚 [generation_service] Использована история диалога: {len([message for message in history if message.get('role') in ('user', 'assistant')])} сообщений")

        # Добавляем текущий запрос пользователя
        messages.append({"role": "user", "content": prompt})

        # Если указан провайдер, получаем соответствующий клиент
        if llm_provider:
            # Используем запрошенный провайдер (даже если он совпадает с дефолтным)
            llm_client = get_llm(llm_provider)
            logger.info(
                f"✅ [generation_service] Использование запрошенного LLM провайдера: {llm_provider} (модель: {llm_client.model}, base_url: {llm_client.base_url})"
            )
        else:
            # Используем провайдер по умолчанию
            llm_client = self.llm_client
            logger.info(
                f"✅ [generation_service] Использование провайдера по умолчанию: {self.llm_provider} (модель: {llm_client.model}, base_url: {llm_client.base_url})"
            )

        logger.info(
            f"🔄 [generation_service] Генерация ответа через LLM провайдер={llm_provider or self.llm_provider}, модель={llm_client.model}"
        )
        answer = await llm_client.generate(messages, temperature=temperature, max_tokens=max_tokens)
        logger.info("✅ [generation_service] Ответ успешно сгенерирован")

        # Шаг 5: Сохраняем историю диалога в память (если указан session_id)
        # Сохраняем только user и assistant сообщения, системный промпт не сохраняется
        if session_id:
            try:
                # Добавляем оригинальный запрос пользователя (без контекста документов) и ответ ассистента
                # Сохраняем оригинальный query, а не prompt с контекстом, чтобы история была чище
                await self.memory_service.add_message(session_id, "user", query)
                await self.memory_service.add_message(session_id, "assistant", answer)

                # Обновляем TTL сессии
                await self.memory_service.update_ttl(session_id)
                logger.info(f"💾 [generation_service] История диалога сохранена для сессии {session_id}")
            except Exception as e:
                logger.error(f"❌ [generation_service] Ошибка при сохранении истории для сессии {session_id}: {e}")
                # Продолжаем выполнение даже если сохранение не удалось

        # Извлекаем источники (всегда включаем)
        doc_ids = [doc_id for doc_id, _, _, _ in context_documents]
        metadatas = [metadata for _, _, _, metadata in context_documents]

        return answer, doc_ids, metadatas

    async def clear_session(self, session_id: str) -> None:
        """
        Очищает историю диалога для указанной сессии

        Args:
            session_id: Идентификатор сессии
        """
        await self.memory_service.clear_history(session_id)
        logger.info(f"🗑️ [generation_service] История сессии {session_id} очищена")

    async def close(self) -> None:
        """Закрытие LLM клиента и сервиса памяти"""
        if hasattr(self, "llm_client") and hasattr(self.llm_client, "client"):
            await self.llm_client.client.close()
        if hasattr(self, "memory_service"):
            await self.memory_service.close()
