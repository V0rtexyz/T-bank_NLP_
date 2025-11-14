import logging

from tplexity.config import settings
from tplexity.retrieval.rerank import get_reranker
from tplexity.retrieval.vector_search import VectorSearch

logger = logging.getLogger(__name__)


class HybridRetrieval:
    """Класс для гибридного поиска с использованием Qdrant (BM25 + Embeddings → RRF → rerank).

    Использует встроенный гибридный поиск Qdrant с prefetch и RRF для объединения
    dense и sparse (BM25) векторов, затем применяет reranking для финального ранжирования.
    """

    def __init__(
        self,
        documents: list[str] | None = None,
        metadatas: list[dict] | None = None,
    ):
        """
        Инициализация гибридного поисковика.

        Args:
            documents: Список документов для индексации
            metadatas: Список словарей с метаданными для каждого документа
        """
        self.documents = documents or []
        logger.info("🔄 [hybrid_retrieval] Инициализация гибридного поисковика")

        self.vector_search = VectorSearch()

        self.reranker = get_reranker()
        self.rerank_top_k = settings.rerank_top_k
        logger.info(f"✅ [hybrid_retrieval] Гибридный поисковик инициализирован, rerank_top_k: {self.rerank_top_k}")

        # Индексация документов в векторной базе, если они предоставлены
        if self.documents:
            logger.info(f"🔄 [hybrid_retrieval] Индексация {len(self.documents)} документов")
            ids = list(range(len(self.documents)))
            self.vector_search.add_documents(self.documents, ids=ids, metadatas=metadatas)
            logger.info("✅ [hybrid_retrieval] Индексация завершена")

    def add_documents(self, documents: list[str], metadatas: list[dict] | None = None) -> None:
        """
        Добавить новые документы в векторную базу данных.

        Args:
            documents: Список новых документов
            metadatas: Список словарей с метаданными для каждого документа
        """
        logger.info(f"🔄 [hybrid_retrieval] Добавление {len(documents)} новых документов")
        self.documents.extend(documents)

        # Получаем текущее количество документов для правильной индексации в Qdrant
        start_id = len(self.documents) - len(documents)
        ids = list(range(start_id, len(self.documents)))
        self.vector_search.add_documents(documents, ids=ids, metadatas=metadatas)
        logger.info(f"✅ [hybrid_retrieval] Документы добавлены, всего документов: {len(self.documents)}")

    def search(
        self,
        query: str,
        top_k: int = 10,
        use_rerank: bool = True,
        hybrid_top_k: int = 50,
    ) -> list[tuple[int, float, str, dict | None]]:
        """
        Гибридный поиск: BM25 + Embeddings → RRF (в Qdrant) → Rerank.

        Args:
            query: Поисковый запрос
            top_k: Количество возвращаемых результатов
            use_rerank: Использовать ли reranking
            hybrid_top_k: Количество результатов от гибридного поиска для reranking

        Returns:
            Список кортежей (doc_id, score, document_text, metadata)
        """
        logger.info(f"🔍 [hybrid_retrieval] Начало поиска для запроса: {query[:50]}...")

        # Шаг 1: Гибридный поиск в Qdrant (BM25 + Dense → RRF)
        # VectorSearch использует встроенный гибридный поиск Qdrant с prefetch и RRF
        logger.debug(f"🔄 [hybrid_retrieval] Выполнение гибридного поиска, top_k: {hybrid_top_k}")
        hybrid_results = self.vector_search.search(query, top_k=hybrid_top_k, with_metadata=True, use_hybrid=True)
        logger.info(f"✅ [hybrid_retrieval] Гибридный поиск завершен, найдено результатов: {len(hybrid_results)}")

        if not hybrid_results:
            logger.warning("⚠️ [hybrid_retrieval] Гибридный поиск не вернул результатов")
            return []

        # Создаем словарь для быстрого доступа к метаданным и документам
        # Формат hybrid_results: (doc_id, score, text, metadata)
        metadata_map = {doc_id: metadata for doc_id, _, _, metadata in hybrid_results}
        doc_id_to_score = {doc_id: score for doc_id, score, _, _ in hybrid_results}
        doc_id_to_text = {doc_id: text for doc_id, _, text, _ in hybrid_results}

        # Шаг 2: Reranking (опционально)
        if use_rerank and hybrid_results:
            logger.debug(f"🔄 [hybrid_retrieval] Выполнение reranking для топ-{self.rerank_top_k} результатов")
            # Получаем документы для reranking
            rerank_doc_ids = [doc_id for doc_id, _, _, _ in hybrid_results[: self.rerank_top_k]]
            # Получаем тексты документов из результатов поиска
            rerank_documents = [doc_id_to_text.get(doc_id, "") for doc_id in rerank_doc_ids]

            # Reranking
            rerank_results = self.reranker.rerank(query, rerank_documents, top_n=top_k)
            logger.info(f"✅ [hybrid_retrieval] Reranking завершен, возвращено результатов: {len(rerank_results)}")

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
            # Без reranking, просто берем топ-k из гибридных результатов
            final_results = [
                (doc_id, score, text, metadata_map.get(doc_id)) for doc_id, score, text, _ in hybrid_results[:top_k]
            ]

        logger.info(f"✅ [hybrid_retrieval] Поиск завершен, возвращено {len(final_results)} результатов")
        return final_results

    def delete_documents(self, doc_ids: list[int]) -> None:
        """
        Удалить документы из векторной базы данных и из внутреннего списка.

        Args:
            doc_ids: Список ID документов для удаления
        """
        if not doc_ids:
            logger.warning("⚠️ [hybrid_retrieval] Передан пустой список ID для удаления")
            return

        logger.info(f"🔄 [hybrid_retrieval] Удаление {len(doc_ids)} документов")
        try:
            # Удаляем из Qdrant
            self.vector_search.delete_documents(doc_ids)

            # Удаляем из внутреннего списка документов
            # Создаем множество для быстрого поиска
            doc_ids_set = set(doc_ids)
            # Фильтруем документы, оставляя только те, которых нет в списке для удаления
            self.documents = [doc for idx, doc in enumerate(self.documents) if idx not in doc_ids_set]

            logger.info(f"✅ [hybrid_retrieval] Документы удалены, осталось документов: {len(self.documents)}")
        except Exception as e:
            logger.error(f"❌ [hybrid_retrieval] Ошибка при удалении документов: {e}")
            raise

    def delete_all_documents(self) -> None:
        """
        Удалить все документы из векторной базы данных и очистить внутренний список.
        """
        logger.warning("⚠️ [hybrid_retrieval] Удаление всех документов")
        try:
            # Удаляем все из Qdrant
            self.vector_search.delete_all_documents()

            # Очищаем внутренний список
            self.documents = []

            logger.info("✅ [hybrid_retrieval] Все документы удалены")
        except Exception as e:
            logger.error(f"❌ [hybrid_retrieval] Ошибка при удалении всех документов: {e}")
            raise
