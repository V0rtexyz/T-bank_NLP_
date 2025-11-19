import asyncio
import logging
import time
from datetime import datetime

import httpx

from tplexity.generation.config import settings
from tplexity.generation.memory_service import MemoryService
from tplexity.generation.prompts import (
    QUERY_REFORMULATION_PROMPT,
    REACT_DECISION_PROMPT,
    RELEVANCE_EVALUATOR_PROMPT,
    SHORT_ANSWER_PROMPT,
    SYSTEM_PROMPT_WITH_RETRIEVER,
    SYSTEM_PROMPT_WITHOUT_RETRIEVER,
    USER_PROMPT,
)
from tplexity.llm_client import get_llm
from tplexity.retriever.retry_utils import retry_with_backoff

logger = logging.getLogger(__name__)


class RetrieverClient:
    """Клиент для взаимодействия с Retriever API"""

    def __init__(self, base_url: str, timeout: float = 60.0, max_retries: int = 3):
        """
        Инициализация клиента

        Args:
            base_url: Базовый URL Retriever API (например, http://localhost:8010)
            timeout: Таймаут запросов в секундах
            max_retries: Максимальное количество попыток при ошибках
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Создаем connection pool для переиспользования соединений
        timeout_config = httpx.Timeout(timeout, connect=10.0)
        limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
        self.client = httpx.AsyncClient(timeout=timeout_config, limits=limits)

        logger.info(
            f"🔄 [generation][generation_service] Инициализирован клиент для {self.base_url} (connection pool: max_connections=20)"
        )

    async def _search_internal(
        self,
        query: str,
        top_k: int | None = None,
        top_n: int | None = None,
        use_rerank: bool = False,
        messages: list[dict[str, str]] | None = None,
    ) -> list[tuple[str, float, str, dict | None]]:
        """
        Внутренний метод поиска (используется с retry)

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

        response = await self.client.post(f"{self.base_url}/retriever/search", json=payload)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        # Преобразуем в формат (doc_id, score, text, metadata)
        return [(r["doc_id"], r["score"], r["text"], r.get("metadata")) for r in results]

    async def search(
        self,
        query: str,
        top_k: int | None = None,
        top_n: int | None = None,
        use_rerank: bool = False,
        messages: list[dict[str, str]] | None = None,
    ) -> list[tuple[str, float, str, dict | None]]:
        """
        Поиск релевантных документов с retry механизмом

        Args:
            query: Поисковый запрос
            top_k: Количество документов до реранка
            top_n: Количество документов после реранка
            use_rerank: Использовать ли reranking
            messages: История диалога для переформулирования запроса

        Returns:
            list[tuple[str, float, str, dict | None]]: Список кортежей (doc_id, score, text, metadata)
        """
        try:
            results = await retry_with_backoff(
                self._search_internal,
                max_retries=self.max_retries,
                initial_delay=1.0,
                max_delay=30.0,
                exponential_base=2.0,
                jitter=True,
                query=query,
                top_k=top_k,
                top_n=top_n,
                use_rerank=use_rerank,
                messages=messages,
            )
            return results
        except httpx.TimeoutException:
            logger.error("⏱️ [generation][generation_service] Таймаут при запросе к Retriever API после всех попыток")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ [generation][generation_service] HTTP ошибка от Retriever API: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ [generation][generation_service] Ошибка при запросе к Retriever API: {e}")
            raise

    async def close(self) -> None:
        """Закрывает соединение с Retriever API"""
        await self.client.aclose()
        logger.info("🔌 [generation][generation_service] Соединение с Retriever API закрыто")


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
        logger.info("🔄 [generation][generation_service] Инициализация сервиса генерации")

        # Инициализируем клиент для Retriever API
        retriever_url = retriever_url or settings.retriever_api_url
        self.retriever_client = RetrieverClient(retriever_url, timeout=settings.retriever_api_timeout)

        # Выбираем провайдер LLM
        self.llm_provider = llm_provider or settings.llm_provider
        self.llm_client = get_llm(self.llm_provider)
        self.router_llm_provider = settings.router_llm_provider
        self.router_llm_client = get_llm(self.router_llm_provider)

        # Инициализируем сервис памяти
        self.memory_service = memory_service or MemoryService()

        logger.info(f"✅ [generation][generation_service] Сервис генерации инициализирован: provider={self.llm_provider}")

    def _get_agent_llm_client(self, override_provider: str | None = None):
        """
        Возвращает LLM клиента для вспомогательных агентов (роутер, переформулировщик)
        и гарантирует, что deepseek используется только для финальной генерации ответа.
        """

        provider = override_provider or self.router_llm_provider
        if provider == self.llm_provider:
            provider = self.router_llm_provider

        if provider == self.router_llm_provider and override_provider is None:
            return self.router_llm_client

        return get_llm(provider)

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

        llm_client = self._get_agent_llm_client(llm_provider)

        messages = [{"role": "user", "content": decision_prompt}]

        try:
            decision = await llm_client.generate(messages, temperature=0.0, max_tokens=10)
            decision = decision.strip().upper()

            use_retriever = decision.startswith("YES")
            return use_retriever
        except Exception as e:
            logger.warning(
                f"⚠️ [generation][generation_service] Ошибка при принятии решения ReAct агентом: {e}. Используется retriever по умолчанию."
            )
            return True

    async def _reformulate_query(
        self, query: str, session_id: str | None = None, llm_provider: str | None = None
    ) -> str:
        """
        Агент перефразировки: переписывает исходный запрос в форму, удобную для поиска

        Args:
            query (str): Исходный запрос пользователя
            session_id (str | None): Идентификатор сессии для получения истории диалога
            llm_provider (str | None): Провайдер LLM для переформулирования

        Returns:
            str: Переформулированный запрос
        """
        # Получаем историю диалога для контекста
        history_text = ""
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
                if history_messages:
                    history_text = "\n".join(history_messages[-6:])  # Последние 6 сообщений

        reformulation_prompt = QUERY_REFORMULATION_PROMPT.format(history=history_text, query=query)

        llm_client = self._get_agent_llm_client(llm_provider)

        messages = [{"role": "user", "content": reformulation_prompt}]

        try:
            reformulated_query = await llm_client.generate(messages, temperature=0.0, max_tokens=200)
            reformulated_query = reformulated_query.strip()
            logger.info(
                f"✅ [generation][generation_service] Запрос переформулирован: '{query[:50]}...' -> '{reformulated_query[:50]}...'"
            )
            return reformulated_query
        except Exception as e:
            logger.warning(
                f"⚠️ [generation][generation_service] Ошибка при переформулировании запроса: {e}. Используется оригинальный запрос."
            )
            return query

    async def _evaluate_document_relevance(
        self, reformulated_query: str, document_text: str, llm_provider: str | None = None
    ) -> bool:
        """
        Агент-оценщик релевантности: бинарно решает, релевантен ли документ переформулированному запросу

        Args:
            reformulated_query (str): Переформулированный запрос
            document_text (str): Текст документа для оценки
            llm_provider (str | None): Не используется, агент-оценщик всегда использует Qwen

        Returns:
            bool: True если документ релевантен, False если нет
        """
        evaluator_prompt = RELEVANCE_EVALUATOR_PROMPT.format(
            reformulated_query=reformulated_query, document_text=document_text
        )

        # Агент-оценщик всегда использует Qwen
        llm_client = get_llm("qwen")

        messages = [{"role": "user", "content": evaluator_prompt}]

        try:
            decision = await llm_client.generate(messages, temperature=0.0, max_tokens=10)
            decision = decision.strip().upper()
            is_relevant = decision.startswith("YES")
            return is_relevant
        except Exception as e:
            logger.warning(
                f"⚠️ [generation][generation_service] Ошибка при оценке релевантности документа: {e}. Документ считается релевантным по умолчанию."
            )
            return True  # В случае ошибки считаем документ релевантным

    async def _evaluate_documents_relevance_parallel(
        self,
        reformulated_query: str,
        documents: list[tuple[str, float, str, dict | None]],
        llm_provider: str | None = None,
    ) -> list[tuple[str, float, str, dict | None]]:
        """
        Параллельная оценка релевантности всех документов через агента-оценщика

        Args:
            reformulated_query (str): Переформулированный запрос
            documents: Список кортежей (doc_id, score, text, metadata)
            llm_provider (str | None): Не используется, агент-оценщик всегда использует Qwen

        Returns:
            list[tuple[str, float, str, dict | None]]: Список только релевантных документов
        """
        if not documents:
            return []

        # Создаем задачи для параллельной оценки всех документов
        # Агент-оценщик всегда использует Qwen, поэтому передаем None
        tasks = [
            self._evaluate_document_relevance(reformulated_query, text, None)
            for _, _, text, _ in documents
        ]

        # Запускаем все оценки параллельно
        relevance_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Фильтруем документы по результатам оценки
        relevant_documents = []
        for idx, (doc_id, score, text, metadata) in enumerate(documents):
            if isinstance(relevance_results[idx], Exception):
                logger.warning(
                    f"⚠️ [generation][generation_service] Ошибка при оценке документа {doc_id}: {relevance_results[idx]}. Документ считается релевантным."
                )
                relevant_documents.append((doc_id, score, text, metadata))
            elif relevance_results[idx]:  # True означает релевантность
                relevant_documents.append((doc_id, score, text, metadata))
            else:
                logger.debug(f"🔍 [generation][generation_service] Документ {doc_id} признан нерелевантным")

        logger.info(
            f"✅ [generation][generation_service] Оценка релевантности завершена: {len(relevant_documents)}/{len(documents)} документов релевантны"
        )
        return relevant_documents

    def _validate_documents(
        self, documents: list[tuple[str, float, str, dict | None]], min_score: float = 0.0, min_text_length: int = 10
    ) -> list[tuple[str, float, str, dict | None]]:
        """
        Валидирует и фильтрует документы по релевантности и качеству

        Args:
            documents: Список кортежей (doc_id, score, text, metadata)
            min_score: Минимальный score для включения документа
            min_text_length: Минимальная длина текста документа

        Returns:
            list[tuple[str, float, str, dict | None]]: Отфильтрованный список документов
        """
        validated = []
        for doc_id, score, text, metadata in documents:
            # Проверяем score
            if score < min_score:
                logger.debug(f"🔍 [generation][generation_service] Документ {doc_id} отфильтрован: score {score:.3f} < {min_score}")
                continue

            # Проверяем наличие и длину текста
            if not text or not isinstance(text, str):
                logger.debug(f"🔍 [generation][generation_service] Документ {doc_id} отфильтрован: пустой или некорректный текст")
                continue

            if len(text.strip()) < min_text_length:
                logger.debug(
                    f"🔍 [generation][generation_service] Документ {doc_id} отфильтрован: длина текста {len(text)} < {min_text_length}"
                )
                continue

            validated.append((doc_id, score, text, metadata))

        if len(validated) < len(documents):
            logger.info(
                f"🔍 [generation][generation_service] Валидация документов: {len(documents)} -> {len(validated)} "
                f"(отфильтровано {len(documents) - len(validated)})"
            )

        return validated

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
            context_parts.append(f"[{idx}] Документ {idx} (релевантность: {score:.3f})\n{text}")

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
        logger.debug("🔄 [generation][generation_service] Отправка запроса к LLM")
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
    ) -> tuple[str, list[str], list[dict | None], float | None, float, float]:
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
            tuple[str, list[str], list[dict | None], float | None, float, float]:
            (ответ, список doc_ids, список метаданных, время поиска, время генерации, общее время)

        Raises:
            ValueError: Если запрос пуст
        """
        if not query or not query.strip():
            raise ValueError("Запрос не может быть пустым")

        # Начало измерения общего времени
        total_start_time = time.time()

        # Если use_rerank не указан, используем True по умолчанию
        use_rerank = use_rerank if use_rerank is not None else True

        # Выбираем провайдер LLM (если указан в запросе, используем его, иначе используем из self)
        provider = llm_provider or self.llm_provider
        logger.info(f"🔄 [generation][generation_service] Генерация для запроса: '{query[:50]}...'")

        # ReAct агент: решение о необходимости retriever
        react_start_time = time.time()
        use_retriever = await self._should_use_retriever(query, session_id, llm_provider)
        react_time = time.time() - react_start_time
        logger.info(
            f"✅ [generation][generation_service] ReAct агент: {'использовать' if use_retriever else 'НЕ использовать'} retriever ({react_time:.2f}с)"
        )

        context_documents = []
        search_time = None
        if use_retriever:
            # Шаг 1: Агент перефразировки - переписывает запрос для поиска
            reformulation_start_time = time.time()
            reformulated_query = await self._reformulate_query(query, session_id, llm_provider)
            reformulation_time = time.time() - reformulation_start_time
            logger.info(
                f"✅ [generation][generation_service] Агент перефразировки: запрос переформулирован за {reformulation_time:.2f}с"
            )

            # Шаг 2: Поиск документов через Retriever API
            # Передаем уже переформулированный запрос и messages=None, чтобы retriever не выполнял свою переформулировку
            search_start_time = time.time()
            raw_documents = await self.retriever_client.search(
                query=reformulated_query, top_k=top_k, top_n=None, use_rerank=use_rerank, messages=None
            )
            retrieval_time = time.time() - search_start_time
            logger.info(
                f"✅ [generation][generation_service] Retriever: найдено {len(raw_documents)} документов за {retrieval_time:.2f}с"
            )

            # Валидация документов по базовым критериям (длина, наличие текста)
            validated_documents = self._validate_documents(raw_documents, min_score=0.0, min_text_length=10)

            if not validated_documents:
                logger.warning("⚠️ [generation][generation_service] Документы не прошли базовую валидацию")
                error_message = "К сожалению, я не нашел релевантной информации в базе знаний для ответа на ваш вопрос."
                total_time = time.time() - total_start_time
                return (
                    error_message,
                    [],
                    [],
                    time.time() - search_start_time,
                    0.0,
                    total_time,
                )

            # Шаг 3: Агент-оценщик релевантности - параллельная проверка всех документов
            evaluation_start_time = time.time()
            context_documents = await self._evaluate_documents_relevance_parallel(
                reformulated_query, validated_documents, llm_provider
            )
            evaluation_time = time.time() - evaluation_start_time
            search_time = time.time() - search_start_time  # Общее время поиска + оценки
            logger.info(
                f"✅ [generation][generation_service] Агент-оценщик релевантности: {len(context_documents)}/{len(validated_documents)} документов релевантны за {evaluation_time:.2f}с"
            )

            if not context_documents:
                logger.warning("⚠️ [generation][generation_service] Нет релевантных документов после оценки")
                error_message = "К сожалению, я не нашел релевантной информации в базе знаний для ответа на ваш вопрос."
                total_time = time.time() - total_start_time
                return (
                    error_message,
                    [],
                    [],
                    search_time,
                    0.0,
                    total_time,
                )

        # Шаг 4: Формирование промпта для генерации ответа
        if context_documents:
            prompt = self._build_prompt(query, context_documents)
        else:
            # Если retriever не использовался, формируем промпт без контекста
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prompt = f"Вопрос пользователя: {query}\n\nТекущее время: {current_time}"

        # Шаг 3: Выбираем правильный системный промпт в зависимости от использования retriever
        system_prompt = SYSTEM_PROMPT_WITH_RETRIEVER if context_documents else SYSTEM_PROMPT_WITHOUT_RETRIEVER

        # Шаг 4: Формируем список сообщений для LLM
        # Всегда добавляем системный промпт в начале
        messages = [{"role": "system", "content": system_prompt}]

        # Получаем историю диалога из памяти (если указан session_id)
        if session_id:
            history = await self.memory_service.get_history(session_id)
            if history:
                history_messages = [message for message in history if message.get("role") in ("user", "assistant")]
                for message in history_messages:
                    messages.append({"role": message.get("role"), "content": message.get("content", "")})
                if history_messages:
                    logger.debug(f"📚 [generation][generation_service] Использована история: {len(history_messages)} сообщений")

        # Добавляем текущий запрос пользователя
        messages.append({"role": "user", "content": prompt})

        # Если указан провайдер, получаем соответствующий клиент
        if llm_provider:
            llm_client = get_llm(llm_provider)
        else:
            llm_client = self.llm_client

        generation_start_time = time.time()
        answer = await llm_client.generate(messages, temperature=temperature, max_tokens=max_tokens)
        generation_time = time.time() - generation_start_time
        logger.info(
            f"✅ [generation][generation_service] Ответ сгенерирован за {generation_time:.2f}с (модель: {llm_client.model})"
        )

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
                logger.debug(f"💾 [generation][generation_service] История сохранена для сессии {session_id}")
            except Exception as e:
                logger.error(f"❌ [generation][generation_service] Ошибка при сохранении истории для сессии {session_id}: {e}")
                # Продолжаем выполнение даже если сохранение не удалось

        # Извлекаем источники (всегда включаем)
        doc_ids = [doc_id for doc_id, _, _, _ in context_documents]
        metadatas = [metadata for _, _, _, metadata in context_documents]

        # Вычисляем общее время
        total_time = time.time() - total_start_time
        search_str = f"{search_time:.2f}с" if search_time is not None else "N/A"
        logger.info(
            f"✅ [generation][generation_service] Обработка завершена за {total_time:.2f}с (поиск: {search_str}, генерация: {generation_time:.2f}с)"
        )

        return answer, doc_ids, metadatas, search_time, generation_time, total_time

    async def generate_short_answer(
        self,
        detailed_answer: str,
        llm_provider: str | None = None,
    ) -> str:
        """
        Генерация краткого ответа на основе детального ответа.

        Args:
            detailed_answer: Детальный ответ для сокращения
            llm_provider: Провайдер LLM для использования (если None, используется значение из self.llm_provider)

        Returns:
            str: Краткий ответ
        """
        # Выбираем провайдер LLM
        provider = llm_provider or self.llm_provider
        logger.info(f"🔄 [generation][generation_service] Генерация краткого ответа (провайдер: {provider})")

        # Формируем промпт для краткого ответа
        prompt = SHORT_ANSWER_PROMPT.format(detailed_answer=detailed_answer)

        # Формируем список сообщений для LLM
        messages = [
            {"role": "system", "content": "Ты — агент генерации кратких ответов мультиагентной системы RAG."},
            {"role": "user", "content": prompt},
        ]

        # Если указан провайдер, получаем соответствующий клиент
        if llm_provider:
            llm_client = get_llm(llm_provider)
        else:
            llm_client = self.llm_client

        # Генерируем краткий ответ
        short_answer = await llm_client.generate(messages)
        logger.info(f"✅ [generation][generation_service] Краткий ответ сгенерирован")

        return short_answer

    async def clear_session(self, session_id: str) -> None:
        """
        Очищает историю диалога для указанной сессии

        Args:
            session_id: Идентификатор сессии
        """
        await self.memory_service.clear_history(session_id)

    async def close(self) -> None:
        """Закрытие LLM клиента, Retriever клиента и сервиса памяти"""
        if hasattr(self, "retriever_client"):
            await self.retriever_client.close()
        if hasattr(self, "llm_client") and hasattr(self.llm_client, "client"):
            await self.llm_client.client.close()
        if hasattr(self, "memory_service"):
            await self.memory_service.close()
