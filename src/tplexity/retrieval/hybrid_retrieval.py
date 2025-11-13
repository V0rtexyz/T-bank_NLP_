from tplexity.config import settings
from tplexity.retrieval.bm25_search import BM25Searcher
from tplexity.retrieval.rerank import Reranker
from tplexity.retrieval.rrf import RRFRanker
from tplexity.retrieval.vector_search import VectorSearcher


class HybridRetrieval:
    """Класс для гибридного поиска с использованием BM25, векторного поиска, RRF и reranking."""

    def __init__(
        self,
        documents: list[str] | None = None,
        metadatas: list[dict] | None = None,
        bm25_k1: float | None = None,
        bm25_b: float | None = None,
        rrf_k: int | None = None,
        rerank_model_name: str | None = None,
        rerank_top_k: int | None = None,
        qdrant_collection_name: str | None = None,
        embedding_model_name: str | None = None,
    ):
        """
        Инициализация гибридного поисковика.

        Args:
            documents: Список документов для индексации
            metadatas: Список словарей с метаданными для каждого документа
            bm25_k1: Параметр k1 для BM25
            bm25_b: Параметр b для BM25
            rrf_k: Параметр k для RRF
            rerank_model_name: Имя модели для reranking
            rerank_top_k: Количество документов для reranking
            qdrant_collection_name: Имя коллекции в Qdrant
            embedding_model_name: Имя модели для embeddings
        """
        self.documents = documents or []

        # Инициализация компонентов
        self.bm25_searcher = BM25Searcher(
            documents=self.documents,
            k1=bm25_k1 or settings.bm25_k1,
            b=bm25_b or settings.bm25_b,
        )

        self.vector_searcher = VectorSearcher(
            collection_name=qdrant_collection_name,
        )

        self.rrf_ranker = RRFRanker(k=rrf_k or settings.rrf_k)

        self.reranker = Reranker(model_name=rerank_model_name or settings.rerank_model_name)

        self.rerank_top_k = rerank_top_k or settings.rerank_top_k

        # Индексация документов в векторной базе, если они предоставлены
        if self.documents:
            self.vector_searcher.add_documents(self.documents, metadatas=metadatas)

    def add_documents(self, documents: list[str], metadatas: list[dict] | None = None) -> None:
        """
        Добавить новые документы в оба индекса.

        Args:
            documents: Список новых документов
            metadatas: Список словарей с метаданными для каждого документа
        """
        self.documents.extend(documents)
        self.bm25_searcher.add_documents(documents)

        # Получаем текущее количество документов для правильной индексации в Qdrant
        start_id = len(self.documents) - len(documents)
        ids = list(range(start_id, len(self.documents)))
        self.vector_searcher.add_documents(documents, ids=ids, metadatas=metadatas)

    def search(
        self,
        query: str,
        top_k: int = 10,
        use_rerank: bool = True,
        bm25_top_k: int = 50,
        vector_top_k: int = 50,
    ) -> list[tuple[int, float, str, dict | None]]:
        """
        Гибридный поиск: BM25 + Vector → RRF → Rerank.

        Args:
            query: Поисковый запрос
            top_k: Количество возвращаемых результатов
            use_rerank: Использовать ли reranking
            bm25_top_k: Количество результатов от BM25 для RRF
            vector_top_k: Количество результатов от векторного поиска для RRF

        Returns:
            Список кортежей (doc_id, score, document_text, metadata)
        """
        # Шаг 1: Поиск через BM25
        bm25_results = self.bm25_searcher.search(query, top_k=bm25_top_k)

        # Шаг 2: Поиск через векторную базу (с метаданными)
        vector_results_with_metadata = self.vector_searcher.search(query, top_k=vector_top_k, with_metadata=True)
        # Создаем словарь для быстрого доступа к метаданным
        metadata_map = {doc_id: metadata for doc_id, _, metadata in vector_results_with_metadata}
        # Извлекаем только (doc_id, score) для RRF
        vector_results = [(doc_id, score) for doc_id, score, _ in vector_results_with_metadata]

        # Шаг 3: RRF ранжирование
        rrf_results = self.rrf_ranker.rank(bm25_results, vector_results)

        # Шаг 4: Reranking (опционально)
        if use_rerank and rrf_results:
            # Получаем документы для reranking
            rerank_doc_ids = [doc_id for doc_id, _ in rrf_results[: self.rerank_top_k]]
            rerank_documents = [self.documents[doc_id] for doc_id in rerank_doc_ids]

            # Reranking
            rerank_results = self.reranker.rerank(query, rerank_documents, top_k=top_k)

            # Маппинг обратно к оригинальным doc_id с метаданными
            final_results = [
                (
                    rerank_doc_ids[rerank_idx],
                    score,
                    self.documents[rerank_doc_ids[rerank_idx]],
                    metadata_map.get(rerank_doc_ids[rerank_idx]),
                )
                for rerank_idx, score in rerank_results
            ]
        else:
            # Без reranking, просто берем топ-k из RRF результатов
            final_results = [
                (
                    doc_id,
                    score,
                    self.documents[doc_id],
                    metadata_map.get(doc_id),
                )
                for doc_id, score in rrf_results[:top_k]
            ]

        return final_results
