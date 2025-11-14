import logging
from typing import Literal

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Поддерживаемые задачи для jina-embeddings-v3
TaskType = Literal[
    "retrieval.query",
    "retrieval.passage",
    "separation",
    "classification",
    "text-matching",
]

# Поддерживаемые размерности Matryoshka embeddings
MatryoshkaDim = Literal[32, 64, 128, 256, 512, 768, 1024]


class Embedding:
    """
    Класс для работы с embeddings модели jina-embeddings-v3

    Модель поддерживает:
    - Task-specific embeddings через LoRA адаптеры
    - Matryoshka embeddings (32, 64, 128, 256, 512, 768, 1024)
    - Максимальная длина последовательности: 8192 токена
    """

    def __init__(self, model_name: str = "jinaai/jina-embeddings-v3"):
        """
        Инициализация класса Embedding

        Args:
            model_name (str): Имя модели для загрузки
        """
        self.model_name = model_name
        logger.info(f"🔄 [embedding] Инициализация модели: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"✅ [embedding] Модель {model_name} успешно инициализирована")
        except Exception as e:
            logger.error(f"❌ [embedding] Ошибка инициализации модели: {e}")
            raise

    def encode(
        self,
        texts: list[str] | str,
        task: TaskType = "retrieval.query",
        max_length: int = 8192,
        truncate_dim: MatryoshkaDim | None = None,
    ) -> list[list[float]] | list[float]:
        """
        Кодировать тексты в embeddings

        Args:
            texts (list[str] | str): Текст или список текстов для кодирования
            task (TaskType): Тип задачи для task-specific embeddings:
                - "retrieval.query": для запросов в асимметричном поиске
                - "retrieval.passage": для пассажей в асимметричном поиске
                - "separation": для кластеризации и reranking
                - "classification": для классификации
                - "text-matching": для симметричного поиска (STS)
            max_length (int): Максимальная длина последовательности (до 8192 токенов)
            truncate_dim (MatryoshkaDim | None): Размерность Matryoshka embeddings (32, 64, 128, 256, 512, 768, 1024)

        Returns:
            list[list[float]] | list[float]: Список embeddings (или один embedding, если передан один текст)
        """
        # Нормализация входных данных
        if isinstance(texts, str):
            texts = [texts]
            single_text = True
        else:
            single_text = False

        encode_kwargs = {
            "task": task,
            "prompt_name": task,
            "max_length": max_length,
        }
        if truncate_dim is not None:
            encode_kwargs["truncate_dim"] = truncate_dim

        logger.debug(f"🔄 [embedding] Кодирование {len(texts)} текстов, task: {task}")
        embeddings = self.model.encode(texts, **encode_kwargs)

        # Возвращаем один embedding, если был передан один текст
        if single_text:
            return embeddings[0].tolist() if hasattr(embeddings[0], "tolist") else embeddings[0]

        return [emb.tolist() if hasattr(emb, "tolist") else emb for emb in embeddings]

    def encode_query(self, query: str) -> list[float]:
        """
        Кодировать запрос в embedding

        Args:
            query: Текст запроса

        Returns:
            Embedding запроса как список float
        """
        logger.debug(f"🔄 [embedding] Кодирование запроса: {query[:50]}...")
        return self.encode(query, task="retrieval.query")

    def encode_document(self, documents: list[str]) -> list[list[float]]:
        """
        Кодировать документы в embeddings

        Args:
            documents: Список документов для кодирования

        Returns:
            Список embeddings документов
        """
        logger.debug(f"🔄 [embedding] Кодирование {len(documents)} документов")
        return self.encode(documents, task="retrieval.passage")

    def get_sentence_embedding_dimension(self) -> int | None:
        """
        Получить размерность embeddings

        Returns:
            Размерность embeddings или None, если не удалось определить
        """
        embedding_dim = self.model.get_sentence_embedding_dimension()

        if embedding_dim is None:
            logger.warning(
                "⚠️ [embedding] Не удалось определить размерность через get_sentence_embedding_dimension(), определяем эмпирически"
            )
            test_embedding = self.encode("test")
            embedding_dim = len(test_embedding)
            logger.info(f"✅ [embedding] Размерность определена эмпирически: {embedding_dim}")

        return embedding_dim

    def get_model(self) -> SentenceTransformer:
        """
        Получить экземпляр модели SentenceTransformer

        Returns:
            Экземпляр модели SentenceTransformer
        """
        return self.model


# Singleton
_embedding_instance: Embedding | None = None


def get_embedding_model() -> Embedding:
    """
    Получить экземпляр модели для embeddings (singleton).

    Returns:
        Экземпляр Embedding модели jinaai/jina-embeddings-v3
    """
    global _embedding_instance
    if _embedding_instance is None:
        _embedding_instance = Embedding()
    return _embedding_instance
