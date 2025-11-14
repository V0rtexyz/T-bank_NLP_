import logging

from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    Fusion,
    FusionQuery,
    Modifier,
    PointIdsList,
    PointStruct,
    Prefetch,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from tplexity.config import settings
from tplexity.retrieval.embedding import get_embedding_model

logger = logging.getLogger(__name__)


class VectorSearch:
    """Класс для векторного поиска через Qdrant с поддержкой dense и sparse векторов"""

    def __init__(self):
        """Инициализация векторного поисковика"""
        self.collection_name = settings.qdrant_collection_name
        self.host = settings.qdrant_host
        self.port = settings.qdrant_port
        self.api_key = settings.qdrant_api_key
        self.timeout = settings.qdrant_timeout

        logger.info("🔄 [vector_search] Инициализация клиента Qdrant")
        try:
            if self.api_key:
                self.client = QdrantClient(
                    url=f"https://{self.host}:{self.port}",
                    api_key=self.api_key,
                    timeout=self.timeout,
                )
            else:
                self.client = QdrantClient(
                    host=self.host,
                    port=self.port,
                    timeout=self.timeout,
                )
            logger.info(f"✅ [vector_search] Клиент Qdrant инициализирован: {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"❌ [vector_search] Ошибка инициализации клиента Qdrant: {e}")
            raise

        self.embedding_model = get_embedding_model()
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        logger.info(f"✅ [vector_search] Dense модель инициализирована, размерность: {self.embedding_dim}")

        self.sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25")
        logger.info("✅ [vector_search] Sparse модель (BM25) инициализирована")

        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Создать коллекцию с поддержкой dense и sparse векторов, если не существует"""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]

        if self.collection_name not in collection_names:
            vectors_config = {
                "dense": VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE,
                )
            }

            sparse_vectors_config = {
                "bm25": SparseVectorParams(
                    modifier=Modifier.IDF,
                ),
            }

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=vectors_config,
                sparse_vectors_config=sparse_vectors_config,
            )
            logger.info(f"✅ [vector_search] Коллекция {self.collection_name} создана с dense и sparse векторами")
        else:
            logger.info(f"✅ [vector_search] Коллекция {self.collection_name} уже существует")

    def add_documents(
        self,
        documents: list[str],
        ids: list[int] | None = None,
        metadatas: list[dict] | None = None,
    ) -> None:
        """
        Добавить документы в векторную базу данных с dense и sparse векторами.

        Args:
            documents (list[str]): Список документов для добавления
            ids (list[int] | None): Список ID для документов. Если None, используются индексы
            metadatas (list[dict] | None): Список словарей с метаданными для каждого документа
        """
        if metadatas is None:
            metadatas = [{}] * len(documents)

        if len(metadatas) != len(documents):
            logger.error(
                f"❌ [vector_search] Количество метаданных ({len(metadatas)}) не совпадает с количеством документов ({len(documents)})"
            )
            return

        if ids is None:
            ids = list(range(len(documents)))

        # Генерация dense embeddings и sparse embeddings
        dense_embeddings = self.embedding_model.encode_document(documents)
        sparse_embeddings = list(self.sparse_model.passage_embed(documents))

        # Подготовка точек для Qdrant с метаданными
        points = []
        for document_id, document, dense_emb, sparse_emb, metadata in zip(
            ids, documents, dense_embeddings, sparse_embeddings, metadatas, strict=False
        ):
            vectors = {
                "dense": dense_emb,
                "bm25": sparse_emb.as_object(),
            }
            payload = {"text": document, **metadata}

            points.append(PointStruct(id=document_id, vector=vectors, payload=payload))

        # Загрузка в Qdrant
        try:
            self.client.upsert(collection_name=self.collection_name, points=points)
            logger.info(f"✅ [vector_search] Добавлено {len(documents)} документов в коллекцию {self.collection_name}")
        except Exception as e:
            logger.error(f"❌ [vector_search] Ошибка при добавлении документов в Qdrant: {e}")
            raise

    def search(
        self,
        query: str,
        top_k: int = 10,
        with_metadata: bool = True,
        use_hybrid: bool = True,
    ) -> list[tuple[int, float, str, dict | None]]:
        """
        Поиск документов по запросу (dense или hybrid)

        Args:
            query (str): Поисковый запрос
            top_k (int): Количество возвращаемых результатов
            with_metadata (bool): Возвращать ли метаданные в результатах
            use_hybrid (bool): Использовать ли гибридный поиск (dense + sparse) с RRF

        Returns:
            list[tuple[int, float, str, dict | None]]: Список кортежей (ID документа, score, текст, метаданные или None)
        """
        if use_hybrid:
            return self._hybrid_search(query, top_k, with_metadata)
        else:
            return self._dense_search(query, top_k, with_metadata)

    def _dense_search(self, query: str, top_k: int, with_metadata: bool) -> list[tuple[int, float, str, dict | None]]:
        """
        Поиск только по dense векторам

        Args:
            query (str): Поисковый запрос
            top_k (int): Количество возвращаемых результатов
            with_metadata (bool): Возвращать ли метаданные в результатах

        Returns:
            list[tuple[int, float, str, dict | None]]: Список кортежей (ID документа, score, текст, метаданные или None)
        """
        logger.debug(f"🔍 [vector_search] Выполнение dense поиска для запроса: {query[:50]}...")

        query_embedding = self.embedding_model.encode_query(query)
        try:
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=("dense", query_embedding),
                limit=top_k,
                with_payload=True,
            )
        except Exception as e:
            logger.error(f"❌ [vector_search] Ошибка при dense поиске: {e}")
            return []

        results = []
        for result in search_results:
            text = result.payload.get("text", "")
            metadata = {k: v for k, v in result.payload.items() if k != "text"} if with_metadata else None
            results.append((result.id, float(result.score), text, metadata))

        return results

    def _hybrid_search(
        self,
        query: str,
        top_k: int,
        prefetch_ratio: float,
        with_metadata: bool,
    ) -> list[tuple[int, float, str, dict | None]]:
        """
        Гибридный поиск с использованием prefetch и RRF

        Args:
            query (str): Поисковый запрос
            top_k (int): Количество возвращаемых результатов
            prefetch_ratio (float): Во сколько раз больше результатов для prefetch
            with_metadata (bool): Возвращать ли метаданные в результатах

        Returns:
            list[tuple[int, float, str, dict | None]]: Список кортежей (ID документа, score, текст, метаданные или None)
        """
        logger.debug(f"🔍 [vector_search] Выполнение гибридного поиска для запроса: {query[:50]}...")
        dense_query = self.embedding_model.encode_query(query)
        sparse_query_dict = list(self.sparse_model.query_embed(query))[0].as_object()
        sparse_query = SparseVector(**sparse_query_dict)

        prefetch = [
            Prefetch(
                query=dense_query,
                using="dense",
                limit=int(top_k * prefetch_ratio),
            ),
            Prefetch(
                query=sparse_query,
                using="bm25",
                limit=int(top_k * prefetch_ratio),
            ),
        ]

        try:
            search_results = self.client.query_points(
                collection_name=self.collection_name,
                prefetch=prefetch,
                query=FusionQuery(
                    fusion=Fusion.RRF,
                ),
                with_payload=True,
                limit=top_k,
            )
        except Exception as e:
            logger.error(f"❌ [vector_search] Ошибка при гибридном поиске: {e}")
            return []

        results = []
        for result in search_results.points:
            text = result.payload.get("text", "")
            metadata = {k: v for k, v in result.payload.items() if k != "text"} if with_metadata else None
            results.append((result.id, float(result.score), text, metadata))

        return results

    def delete_documents(self, ids: list[int]) -> None:
        """
        Удалить документы из векторной базы данных по их ID.

        Args:
            ids (list[int]): Список ID документов для удаления
        """
        if not ids:
            logger.warning("⚠️ [vector_search] Передан пустой список ID для удаления")
            return

        logger.info(f"🔄 [vector_search] Удаление {len(ids)} документов из коллекции {self.collection_name}")
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=PointIdsList(points=ids),
            )
            logger.info(f"✅ [vector_search] Успешно удалено {len(ids)} документов из коллекции {self.collection_name}")
        except Exception as e:
            logger.error(f"❌ [vector_search] Ошибка при удалении документов из Qdrant: {e}")
            raise

    def delete_all_documents(self) -> None:
        """
        Удалить все документы из коллекции.
        """
        logger.warning("⚠️ [vector_search] Удаление всех документов из коллекции")
        try:
            # Получаем все точки из коллекции
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000,  # Максимальное количество для одной операции
                with_payload=False,
                with_vectors=False,
            )
            all_ids = [point.id for point in scroll_result[0]]

            if not all_ids:
                logger.info("ℹ️ [vector_search] Коллекция уже пуста")
                return

            # Удаляем все точки
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=PointIdsList(points=all_ids),
            )
            logger.info(
                f"✅ [vector_search] Успешно удалено {len(all_ids)} документов из коллекции {self.collection_name}"
            )
        except Exception as e:
            logger.error(f"❌ [vector_search] Ошибка при удалении всех документов: {e}")
            raise
