"""Модуль для векторного поиска через Qdrant."""

import logging

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from tplexity.config import settings
from tplexity.embedding import get_embedding_model

logger = logging.getLogger(__name__)


class VectorSearcher:
    """Класс для векторного поиска через Qdrant

    Args:
        collection_name (str | None): Имя коллекции в Qdrant
        host (str | None): Хост Qdrant сервера
        port (int | None): Порт Qdrant сервера
        api_key (str | None): API ключ для Qdrant (если требуется)
        timeout (int | None): Таймаут для запросов к Qdrant
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
        Инициализация векторного поисковика.

        Args:
            collection_name: Имя коллекции в Qdrant
            host: Хост Qdrant сервера
            port: Порт Qdrant сервера
            api_key: API ключ для Qdrant (если требуется)
            timeout: Таймаут для запросов к Qdrant
        """
        self.collection_name = collection_name or settings.qdrant_collection_name
        self.host = host or settings.qdrant_host
        self.port = port or settings.qdrant_port
        self.api_key = api_key or settings.qdrant_api_key
        self.timeout = timeout or settings.qdrant_timeout

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
        logger.info(f"✅ Qdrant client инициализирован: {self.client}")

        self.embedding_model = get_embedding_model()
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Создать коллекцию, если её не существует."""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
            )
            logger.info(f"✅ Коллекция {self.collection_name} создана")
        else:
            logger.info(f"✅ Коллекция {self.collection_name} уже существует")

    def add_documents(
        self,
        documents: list[str],
        ids: list[int],
        metadatas: list[dict] | None = None,
    ) -> None:
        """
        Добавить документы в векторную базу данных

        Args:
            documents (list[str]): Список документов для добавления
            ids (list[int]): Список ID для документов
            metadatas (list[dict] | None): Список словарей с метаданными для каждого документа
        """
        if metadatas is None:
            metadatas = [{}] * len(documents)

        if len(metadatas) != len(documents):
            logger.error("❌ Количество метаданных должно совпадать с количеством документов")

        # Генерация embeddings
        embeddings = self.embedding_model.encode(documents, show_progress_bar=False)

        # Подготовка точек для Qdrant с метаданными
        points = []
        for document_id, document, embedding, metadata in zip(ids, documents, embeddings, metadatas, strict=False):
            payload = {"text": document, **metadata}
            points.append(PointStruct(id=document_id, vector=embedding.tolist(), payload=payload))

        # Загрузка в Qdrant
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, query: str, top_k: int = 10, with_metadata: bool = True) -> list[tuple[int, float, dict | None]]:
        """
        Поиск документов по запросу.

        Args:
            query: Поисковый запрос
            top_k: Количество возвращаемых результатов
            with_metadata: Возвращать ли метаданные в результатах

        Returns:
            Список кортежей (ID документа, cosine similarity score, метаданные или None)
        """
        # Генерация embedding для запроса
        query_embedding = self.embedding_model.encode(query, show_progress_bar=False)

        # Поиск в Qdrant
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=top_k,
            with_payload=True,
        )

        # Форматирование результатов
        if with_metadata:
            results = [
                (
                    result.id,
                    float(result.score),
                    {k: v for k, v in result.payload.items() if k != "text"},
                )
                for result in search_results
            ]
        else:
            results = [(result.id, float(result.score), None) for result in search_results]

        return results
