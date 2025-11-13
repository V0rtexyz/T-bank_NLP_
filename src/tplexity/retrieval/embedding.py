import logging

from sentence_transformers import SentenceTransformer

from tplexity.config import settings

logger = logging.getLogger(__name__)

# Singleton
_embedding_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """
    Получить экземпляр модели для embeddings (singleton).

    Returns:
        Экземпляр SentenceTransformer модели
    """
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(settings.embedding_model_name)
        logger.info(f"✅ Embedding модель {settings.embedding_model_name} инициализирована")
    return _embedding_model
