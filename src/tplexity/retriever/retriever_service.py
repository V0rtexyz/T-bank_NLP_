import asyncio
import logging

from tplexity.retriever.config import settings
from tplexity.retriever.vector_search import VectorSearch

logger = logging.getLogger(__name__)


class RetrieverService:
    """Класс для гибридного поиска с использованием Qdrant

    1. Prefetch
    - Sparse Embeddings: BM25 с лемматизацией
    - Dense Embeddings: Jina Embeddings v3
    2. RRF для объединения векторов
    3. Reranking: Jina Reranker v3
    """

    def __init__(
        self,
        documents: list[str] | None = None,
        metadatas: list[dict] | None = None,
        collection_name: str | None = None,
        host: str | None = None,
        port: int | None = None,
        api_key: str | None = None,
        timeout: int | None = None,
    ):
        """
        Инициализация гибридного поисковика

        Args:
            documents (list[str] | None): Список документов для индексации
            metadatas (list[dict] | None): Список словарей с метаданными для каждого документа
            collection_name (str | None): Имя коллекции в Qdrant
            host (str | None): Хост Qdrant
            port (int | None): Порт Qdrant
            api_key (str | None): API ключ для Qdrant
            timeout (int | None): Таймаут для подключения
        """
        self.documents = documents or []
        logger.info("🔄 [retriever_service] Инициализация гибридного поисковика")

        # Единая точка чтения всех параметров из config
        self._init_config_params(
            collection_name=collection_name,
            host=host,
            port=port,
            api_key=api_key,
            timeout=timeout,
        )

        # Передаем все параметры в VectorSearch
        self.vector_search = VectorSearch(
            collection_name=self.collection_name,
            host=self.host,
            port=self.port,
            api_key=self.api_key,
            timeout=self.timeout,
            prefetch_ratio=self.prefetch_ratio,
        )

        # self.reranker = get_reranker()
        # logger.info(
        #     f"✅ [retriever_service] Гибридный поисковик инициализирован: "
        #     f"top_k={self.top_k}, top_n={self.top_n}, prefetch_ratio={self.prefetch_ratio}"
        # )

        # Индексация документов в векторной базе, если они предоставлены
        # Примечание: __init__ не может быть async, поэтому используем синхронный вызов через asyncio.run
        if self.documents:
            logger.info(f"🔄 [retriever_service] Индексация {len(self.documents)} документов")
            asyncio.run(self.vector_search.add_documents(self.documents, ids=None, metadatas=metadatas))
            logger.info("✅ [retriever_service] Индексация завершена")

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
            self.documents.extend(documents)
            logger.info(f"✅ [retriever_service] Документы добавлены, всего документов: {len(self.documents)}")
        except Exception as e:
            logger.error(f"❌ [retriever_service] Ошибка при добавлении документов в Qdrant: {e}")
            raise

    async def search(
        self,
        query: str,
        top_k: int | None = None,
        top_n: int | None = None,
        use_rerank: bool = True,
    ) -> list[tuple[str, float, str, dict | None]]:
        """
        Гибридный поиск: BM25 + Embeddings → RRF (в Qdrant) → Rerank

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

        logger.debug(f"🔄 [retriever_service] Выполнение гибридного поиска, top_k: {top_k}")
        hybrid_results = await self.vector_search.search(query, top_k=top_k, search_type="hybrid")
        logger.info(f"✅ [retriever_service] Гибридный поиск завершен, найдено результатов: {len(hybrid_results)}")

        if not hybrid_results:
            logger.warning("⚠️ [retriever_service] Гибридный поиск не вернул результатов")
            return []

        # Создаем словарь для быстрого доступа к метаданным и документам
        # Формат hybrid_results: (doc_id, score, text, metadata)
        metadata_map = {doc_id: metadata for doc_id, _, _, metadata in hybrid_results}
        doc_id_to_score = {doc_id: score for doc_id, score, _, _ in hybrid_results}
        doc_id_to_text = {doc_id: text for doc_id, _, text, _ in hybrid_results}

        # Шаг 2: Reranking (опционально)
        if use_rerank and hybrid_results:
            logger.debug(f"🔄 [retriever_service] Выполнение reranking для топ-{top_k} результатов, вернем топ-{top_n}")
            rerank_doc_ids = [doc_id for doc_id, _, _, _ in hybrid_results[:top_k]]
            rerank_documents = [doc_id_to_text.get(doc_id, "") for doc_id in rerank_doc_ids]

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
        """Удалить все документы из векторной базы данных и очистить внутренний список"""
        logger.warning("⚠️ [retriever_service] Удаление всех документов")
        try:
            await self.vector_search.delete_all_documents()
            self.documents = []

            logger.info("✅ [retriever_service] Все документы удалены")
        except Exception as e:
            logger.error(f"❌ [retriever_service] Ошибка при удалении всех документов: {e}")
            raise
