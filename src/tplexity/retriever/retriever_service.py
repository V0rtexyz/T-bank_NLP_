import asyncio
import logging

from tplexity.llm_client import get_llm
from tplexity.retriever.config import settings
from tplexity.retriever.reranker import get_reranker
from tplexity.retriever.vector_search import VectorSearch

logger = logging.getLogger(__name__)

QUERY_REFORMULATION_PROMPT = """
Переформулируй следующий поисковый запрос так, чтобы он был более эффективным для поиска релевантной информации в базе знаний.
Сохрани смысл и ключевые термины, но сделай запрос более четким и структурированным для поиска.
Переформулированный запрос должен быть на русском языке.
Не давай пояснений или комментариев, только текст запроса.

{conversation_context}

Исходный запрос: {query}

Переформулированный запрос:
"""


class RetrieverService:
    """Класс для гибридного поиска с использованием Qdrant

    0. Query Reformulation: Переформулирование запроса через LLM
    1. Prefetch
    - Sparse Embeddings: BM25 с лемматизацией
    - Dense Embeddings: ai-forever/FRIDA
    2. RRF для объединения векторов
    3. Reranking: Jina Reranker v3
    """

    def __init__(
        self,
        collection_name: str | None = None,
        host: str | None = None,
        port: int | None = None,
        api_key: str | None = None,
        timeout: int | None = None,
    ):
        """
        Инициализация гибридного поисковика

        Args:
            collection_name (str | None): Имя коллекции в Qdrant
            host (str | None): Хост Qdrant
            port (int | None): Порт Qdrant
            api_key (str | None): API ключ для Qdrant
            timeout (int | None): Таймаут для подключения
        """
        logger.info("🔄 [retriever_service] Инициализация гибридного поисковика")

        self._init_config_params(
            collection_name=collection_name,
            host=host,
            port=port,
            api_key=api_key,
            timeout=timeout,
        )

        self.vector_search = VectorSearch(
            collection_name=self.collection_name,
            host=self.host,
            port=self.port,
            api_key=self.api_key,
            timeout=self.timeout,
            prefetch_ratio=self.prefetch_ratio,
        )

        # Инициализация reranker
        self.reranker = get_reranker()

        # Инициализация query reformulation (опционально)
        self.enable_query_reformulation = settings.enable_query_reformulation
        if self.enable_query_reformulation:
            provider = settings.query_reformulation_llm_provider
            try:
                self.llm_client = get_llm(provider)  # type: ignore
                logger.info(
                    f"✅ [retriever_service] LLM клиент для переформулирования инициализирован: provider={provider}"
                )
            except Exception as e:
                logger.warning(
                    f"⚠️ [retriever_service] Не удалось инициализировать LLM клиент для переформулирования: {e}. "
                    f"Переформулирование будет отключено."
                )
                self.enable_query_reformulation = False
        else:
            self.llm_client = None

        logger.info(
            f"✅ [retriever_service] Гибридный поисковик инициализирован: "
            f"top_k={self.top_k}, top_n={self.top_n}, prefetch_ratio={self.prefetch_ratio}"
        )

    def _init_config_params(
        self,
        collection_name: str | None = None,
        host: str | None = None,
        port: int | None = None,
        api_key: str | None = None,
        timeout: int | None = None,
    ) -> None:
        """
        Инициализация всех параметров из config в одном месте.
        Все параметры читаются здесь и сохраняются в атрибуты класса.

        Args:
            collection_name: Имя коллекции (если None, берется из config)
            host: Хост Qdrant (если None, берется из config)
            port: Порт Qdrant (если None, берется из config)
            api_key: API ключ (если None, берется из config)
            timeout: Таймаут (если None, берется из config)
        """
        # Qdrant параметры
        self.collection_name = collection_name or settings.qdrant_collection_name
        self.host = host or settings.qdrant_host
        self.port = port or settings.qdrant_port
        self.api_key = api_key or settings.qdrant_api_key
        self.timeout = timeout or settings.qdrant_timeout

        # Retriever параметры
        self.top_k = settings.top_k
        self.top_n = settings.top_n
        self.prefetch_ratio = settings.prefetch_ratio

    async def add_documents(self, documents: list[str], metadatas: list[dict] | None = None) -> None:
        """
        Добавить новые документы в векторную базу данных

        Args:
            documents (list[str]): Список новых документов
            metadatas (list[dict] | None): Список словарей с метаданными для каждого документа

        Raises:
            ValueError: Если документы пусты или невалидны
        """
        if not documents:
            raise ValueError("Список документов не может быть пустым")

        if any(not doc or not doc.strip() for doc in documents):
            raise ValueError("Документы не могут быть пустыми или содержать только пробелы")

        logger.info(f"🔄 [retriever_service] Добавление {len(documents)} новых документов")

        try:
            await self.vector_search.add_documents(documents, ids=None, metadatas=metadatas)
            logger.info("✅ [retriever_service] Документы добавлены в Qdrant")
        except Exception as e:
            logger.error(f"❌ [retriever_service] Ошибка при добавлении документов в Qdrant: {e}")
            raise

    async def _reformulate_query(self, query: str, messages: list[dict[str, str]] | None = None) -> str:
        """
        Переформулировать запрос для улучшения качества поиска

        Args:
            query (str): Исходный поисковый запрос
            messages (list[dict[str, str]] | None): История диалога для контекста

        Returns:
            str: Переформулированный запрос
        """
        try:
            logger.debug(f"🔄 [retriever_service] Переформулирование запроса: {query[:50]}...")

            conversation_context = ""
            if messages:
                recent_messages = messages[-6:] if len(messages) > 6 else messages
                context_parts = []
                for message in recent_messages:
                    role = message.get("role", "")
                    content = message.get("content", "")
                    if role == "user":
                        context_parts.append(f"Пользователь: {content}")
                    elif role == "assistant":
                        context_parts.append(f"Ассистент: {content}")

                if context_parts:
                    conversation_context = "Контекст предыдущего диалога:\n" + "\n".join(context_parts) + "\n\n"

            messages = [
                {
                    "role": "user",
                    "content": QUERY_REFORMULATION_PROMPT.format(
                        conversation_context=conversation_context,
                        query=query,
                    ),
                }
            ]
            reformulated_query = await self.llm_client.generate(messages, temperature=0.0, max_tokens=200)
            reformulated_query = reformulated_query.strip()

            logger.info(
                f"✅ [retriever_service] Запрос переформулирован: '{query[:50]}...' -> '{reformulated_query[:50]}...'"
            )
            return reformulated_query
        except Exception as e:
            logger.warning(
                f"⚠️ [retriever_service] Ошибка при переформулировании запроса: {e}. Используется оригинальный запрос."
            )
            return query

    async def search(
        self,
        query: str,
        top_k: int | None = None,
        top_n: int | None = None,
        use_rerank: bool = True,
        messages: list[dict[str, str]] | None = None,
    ) -> list[tuple[str, float, str, dict | None]]:
        """
        Гибридный поиск: Query Reformulation → BM25 + Embeddings → RRF (в Qdrant) → Rerank

        Args:
            query (str): Поисковый запрос
            top_k (int | None): Количество документов до реранка. Если None, используется значение из config
            top_n (int | None): Количество документов после реранка (возвращаемые). Если None, используется значение из config
            use_rerank (bool): Использовать ли reranking

        Returns:
            list[tuple[str, float, str, dict | None]]: Список кортежей (doc_id, score, document_text, metadata)

        Raises:
            ValueError: Если запрос пуст или параметры невалидны
        """
        if not query or not query.strip():
            raise ValueError("Поисковый запрос не может быть пустым")

        # Используем значения из config, если не переданы явно
        top_k = top_k or self.top_k
        top_n = top_n or self.top_n

        if top_k < 1:
            raise ValueError(f"top_k должен быть >= 1, получено: {top_k}")
        if top_n < 1:
            raise ValueError(f"top_n должен быть >= 1, получено: {top_n}")

        logger.info(f"🔍 [retriever_service] Начало поиска для запроса: {query[:50]}...")

        # Шаг 0: Переформулирование запроса
        if self.enable_query_reformulation and self.llm_client:
            search_query = await self._reformulate_query(query, messages)
        else:
            search_query = query

        logger.debug(f"🔄 [retriever_service] Выполнение гибридного поиска, top_k: {top_k}")
        hybrid_results = await self.vector_search.search(search_query, top_k=top_k, search_type="hybrid")
        logger.info(f"✅ [retriever_service] Гибридный поиск завершен, найдено результатов: {len(hybrid_results)}")

        if not hybrid_results:
            logger.warning("⚠️ [retriever_service] Гибридный поиск не вернул результатов")
            return []

        # Создаем словарь для быстрого доступа к метаданным и документам
        # Формат hybrid_results: (doc_id, score, text, metadata)
        metadata_map = {}
        doc_id_to_score = {}
        doc_id_to_text = {}
        for doc_id, score, text, metadata in hybrid_results:
            metadata_map[doc_id] = metadata
            doc_id_to_score[doc_id] = score
            doc_id_to_text[doc_id] = text

        # Шаг 2: Reranking (опционально)
        if use_rerank and hybrid_results:
            logger.info(f"🔄 [retriever_service] Выполнение reranking для топ-{top_k} результатов, вернем топ-{top_n}")
            rerank_doc_ids = [doc_id for doc_id, _, _, _ in hybrid_results[:top_k]]
            rerank_documents = [doc_id_to_text.get(doc_id, "") for doc_id in rerank_doc_ids]

            # Reranking - используем оригинальный запрос для reranking
            # Reranking - возвращаем top_n результатов (асинхронно)
            rerank_results = await asyncio.to_thread(self.reranker.rerank, query, rerank_documents, top_n=top_n)
            logger.info(f"✅ [retriever_service] Reranking завершен, возвращено результатов: {len(rerank_results)}")

            # Маппинг обратно к оригинальным doc_id с метаданными
            final_results = []
            for rerank_idx, _rerank_score in rerank_results:
                doc_id = rerank_doc_ids[rerank_idx]
                final_results.append(
                    (
                        doc_id,
                        doc_id_to_score.get(doc_id, 0.0),
                        doc_id_to_text.get(doc_id, ""),
                        metadata_map.get(doc_id),
                    )
                )
        else:
            # Без reranking, просто берем топ-n из гибридных результатов
            final_results = [
                (doc_id, score, text, metadata_map.get(doc_id)) for doc_id, score, text, _ in hybrid_results[:top_n]
            ]

        logger.info(f"✅ [retriever_service] Поиск завершен, возвращено {len(final_results)} результатов")
        return final_results

    async def get_documents(self, doc_ids: list[str]) -> list[tuple[str, str, dict | None]]:
        """
        Получить документы по их ID

        Args:
            doc_ids (list[str]): Список ID документов

        Returns:
            list[tuple[str, str, dict | None]]: Список кортежей (doc_id, text, metadata)

        Raises:
            ValueError: Если список ID пуст
        """
        if not doc_ids:
            raise ValueError("Список ID документов не может быть пустым")

        logger.info(f"🔄 [retriever_service] Получение {len(doc_ids)} документов")
        try:
            results = await self.vector_search.get_documents(doc_ids)
            logger.info(f"✅ [retriever_service] Получено {len(results)} документов")
            return results
        except Exception as e:
            logger.error(f"❌ [retriever_service] Ошибка при получении документов: {e}")
            raise

    async def get_all_documents(self) -> list[tuple[str, str, dict | None]]:
        """
        Получить все документы из векторной базы данных

        Returns:
            list[tuple[str, str, dict | None]]: Список кортежей (doc_id, text, metadata)
        """
        logger.info("🔄 [retriever_service] Получение всех документов")
        try:
            results = await self.vector_search.get_all_documents()
            logger.info(f"✅ [retriever_service] Получено {len(results)} документов")
            return results
        except Exception as e:
            logger.error(f"❌ [retriever_service] Ошибка при получении всех документов: {e}")
            raise

    async def delete_documents(self, doc_ids: list[str]) -> None:
        """
        Удалить документы из векторной базы данных

        Args:
            doc_ids (list[str]): Список ID документов для удаления

        Raises:
            ValueError: Если список ID пуст
        """
        if not doc_ids:
            raise ValueError("Список ID документов для удаления не может быть пустым")

        logger.info(f"🔄 [retriever_service] Удаление {len(doc_ids)} документов")
        try:
            # Удаляем из Qdrant
            await self.vector_search.delete_documents(doc_ids)
            logger.info("✅ [retriever_service] Документы удалены из векторной базы")
        except Exception as e:
            logger.error(f"❌ [retriever_service] Ошибка при удалении документов: {e}")
            raise

    async def delete_all_documents(self) -> None:
        """Удалить все документы из векторной базы данных"""
        logger.warning("⚠️ [retriever_service] Удаление всех документов")
        try:
            await self.vector_search.delete_all_documents()
            logger.info("✅ [retriever_service] Все документы удалены")
        except Exception as e:
            logger.error(f"❌ [retriever_service] Ошибка при удалении всех документов: {e}")
            raise
