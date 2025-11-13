"""Модуль для reranking результатов."""

from sentence_transformers import CrossEncoder


class Reranker:
    """Класс для reranking результатов поиска."""

    def __init__(self, model_name: str | None = None):
        """
        Инициализация reranker.

        Args:
            model_name: Имя модели для reranking.
                       Если None, используется модель по умолчанию
        """
        # Используем CrossEncoder для reranking
        # По умолчанию используем модель для reranking
        if model_name is None:
            # Используем легкую модель для reranking
            model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"

        self.model_name = model_name
        self.reranker = CrossEncoder(model_name)

    def rerank(self, query: str, documents: list[str], top_k: int = 10) -> list[tuple[int, float]]:
        """
        Переранжировать документы относительно запроса.

        Args:
            query: Поисковый запрос
            documents: Список документов для reranking
            top_k: Количество возвращаемых результатов

        Returns:
            Список кортежей (индекс документа, rerank score)
        """
        if not documents:
            return []

        # Подготовка пар (query, document) для модели
        pairs = [[query, doc] for doc in documents]

        # Получение scores от reranker модели
        scores = self.reranker.predict(pairs)

        # Создание списка (индекс, score) и сортировка
        results = [(idx, float(score)) for idx, score in enumerate(scores)]
        results.sort(key=lambda x: x[1], reverse=True)

        # Возвращаем топ-k результатов
        return results[:top_k]
