"""Модуль для Reciprocal Rank Fusion (RRF) ранжирования."""

from collections import defaultdict


class RRFRanker:
    """Класс для RRF ранжирования результатов."""

    def __init__(self, k: int = 60):
        """
        Инициализация RRF ранжировщика.

        Args:
            k: Параметр k для RRF (обычно 60)
        """
        self.k = k

    def rank(self, *rankings: list[tuple[int, float]]) -> list[tuple[int, float]]:
        """
        Объединить несколько ранжирований с помощью RRF.

        Args:
            *rankings: Списки результатов от разных поисковиков.
                      Каждый список содержит кортежи (doc_id, score)

        Returns:
            Отсортированный список кортежей (doc_id, rrf_score)
        """
        # Словарь для хранения RRF scores
        rrf_scores: dict[int, float] = defaultdict(float)

        # Обработка каждого ранжирования
        for ranking in rankings:
            # Создаем словарь rank -> doc_id для текущего ранжирования
            rank_map: dict[int, int] = {}
            for rank, (doc_id, _) in enumerate(ranking, start=1):
                rank_map[rank] = doc_id

            # Вычисляем RRF score для каждого документа
            for rank, doc_id in rank_map.items():
                rrf_scores[doc_id] += 1.0 / (self.k + rank)

        # Сортируем по убыванию RRF score
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        return sorted_results

