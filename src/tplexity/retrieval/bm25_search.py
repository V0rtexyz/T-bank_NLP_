"""Модуль для BM25 текстового поиска."""

import numpy as np
from rank_bm25 import BM25Okapi


class BM25Searcher:
    """Класс для BM25 поиска."""

    def __init__(self, documents: list[str], k1: float = 1.5, b: float = 0.75):
        """
        Инициализация BM25 поисковика.

        Args:
            documents: Список документов для индексации
            k1: Параметр k1 для BM25 (контролирует насыщение частоты терминов)
            b: Параметр b для BM25 (контролирует нормализацию по длине документа)
        """
        self.k1 = k1
        self.b = b
        self.documents = documents
        # Токенизация документов
        tokenized_docs = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs, k1=k1, b=b)

    def search(self, query: str, top_k: int = 10) -> list[tuple[int, float]]:
        """
        Поиск документов по запросу.

        Args:
            query: Поисковый запрос
            top_k: Количество возвращаемых результатов

        Returns:
            Список кортежей (индекс документа, BM25 score)
        """
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        # Получаем топ-k результатов с их индексами
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = [(int(idx), float(scores[idx])) for idx in top_indices if scores[idx] > 0]
        return results

    def add_documents(self, documents: list[str]) -> None:
        """
        Добавить новые документы в индекс.

        Args:
            documents: Список новых документов
        """
        self.documents.extend(documents)
        tokenized_docs = [doc.lower().split() for doc in documents]
        # Пересоздаем индекс с новыми документами
        all_tokenized = [doc.lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(all_tokenized, k1=self.k1, b=self.b)
