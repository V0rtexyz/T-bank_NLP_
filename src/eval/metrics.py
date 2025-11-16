"""Метрики для оценки качества retrieval систем"""

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def precision_at_k(retrieved: list[Any], relevant: list[Any], k: int) -> float:
    """
    Вычисляет Precision@K - долю релевантных документов среди топ-K результатов

    Precision@K = |retrieved_k ∩ relevant| / k

    Args:
        retrieved (list[Any]): Список ID полученных документов (упорядочены по релевантности)
        relevant (list[Any]): Список ID релевантных документов (ground truth)
        k (int): Количество топ результатов для оценки

    Returns:
        float: Значение Precision@K в диапазоне [0, 1]

    Examples:
        >>> retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
        >>> relevant = ['doc1', 'doc3', 'doc6']
        >>> precision_at_k(retrieved, relevant, k=5)
        0.4  # 2 из 5 документов релевантны
    """
    if k <= 0:
        raise ValueError(f"k должно быть положительным числом, получено: {k}")

    if not retrieved:
        logger.warning("Список retrieved пуст")
        return 0.0

    if not relevant:
        logger.warning("Список relevant пуст")
        return 0.0

    # Берем только топ-k результатов
    retrieved_k = retrieved[:k]

    # Преобразуем в множества для быстрого поиска
    relevant_set = set(relevant)

    # Считаем количество релевантных документов в топ-k
    relevant_in_k = sum(1 for doc_id in retrieved_k if doc_id in relevant_set)

    precision = relevant_in_k / k
    return precision


def recall_at_k(retrieved: list[Any], relevant: list[Any], k: int) -> float:
    """
    Вычисляет Recall@K - долю найденных релевантных документов от всех релевантных

    Recall@K = |retrieved_k ∩ relevant| / |relevant|

    Args:
        retrieved (list[Any]): Список ID полученных документов (упорядочены по релевантности)
        relevant (list[Any]): Список ID релевантных документов (ground truth)
        k (int): Количество топ результатов для оценки

    Returns:
        float: Значение Recall@K в диапазоне [0, 1]

    Examples:
        >>> retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
        >>> relevant = ['doc1', 'doc3', 'doc6']
        >>> recall_at_k(retrieved, relevant, k=5)
        0.6667  # 2 из 3 релевантных документов найдены
    """
    if k <= 0:
        raise ValueError(f"k должно быть положительным числом, получено: {k}")

    if not retrieved:
        logger.warning("Список retrieved пуст")
        return 0.0

    if not relevant:
        logger.warning("Список relevant пуст")
        return 0.0

    # Берем только топ-k результатов
    retrieved_k = retrieved[:k]

    # Преобразуем в множества для быстрого поиска
    relevant_set = set(relevant)

    # Считаем количество релевантных документов в топ-k
    relevant_in_k = sum(1 for doc_id in retrieved_k if doc_id in relevant_set)

    recall = relevant_in_k / len(relevant)
    return recall


def f1_score_at_k(retrieved: list[Any], relevant: list[Any], k: int) -> float:
    """
    Вычисляет F1-score@K - гармоническое среднее Precision@K и Recall@K

    F1@K = 2 * (Precision@K * Recall@K) / (Precision@K + Recall@K)

    Args:
        retrieved (list[Any]): Список ID полученных документов (упорядочены по релевантности)
        relevant (list[Any]): Список ID релевантных документов (ground truth)
        k (int): Количество топ результатов для оценки

    Returns:
        float: Значение F1-score@K в диапазоне [0, 1]
    """
    precision = precision_at_k(retrieved, relevant, k)
    recall = recall_at_k(retrieved, relevant, k)

    if precision + recall == 0:
        return 0.0

    f1 = 2 * (precision * recall) / (precision + recall)
    return f1


def average_precision(retrieved: list[Any], relevant: list[Any], k: int | None = None) -> float:
    """
    Вычисляет Average Precision (AP) - среднюю точность по всем позициям релевантных документов

    AP = (∑_{i=1}^k Precision@i * rel(i)) / |relevant|
    где rel(i) = 1 если документ на позиции i релевантен, иначе 0

    Args:
        retrieved (list[Any]): Список ID полученных документов (упорядочены по релевантности)
        relevant (list[Any]): Список ID релевантных документов (ground truth)
        k (int | None): Количество топ результатов для оценки. Если None, используются все результаты

    Returns:
        float: Значение Average Precision в диапазоне [0, 1]

    Examples:
        >>> retrieved = ['doc1', 'doc2', 'doc3', 'doc4', 'doc5']
        >>> relevant = ['doc1', 'doc3']
        >>> average_precision(retrieved, relevant)
        0.8333  # (1.0/1 + 2.0/3) / 2
    """
    if not retrieved:
        logger.warning("Список retrieved пуст")
        return 0.0

    if not relevant:
        logger.warning("Список relevant пуст")
        return 0.0

    # Если k не указан, используем все результаты
    if k is None:
        k = len(retrieved)

    # Берем только топ-k результатов
    retrieved_k = retrieved[:k]
    relevant_set = set(relevant)

    # Считаем precision в каждой позиции, где есть релевантный документ
    precisions = []
    num_relevant_found = 0

    for i, doc_id in enumerate(retrieved_k, start=1):
        if doc_id in relevant_set:
            num_relevant_found += 1
            # Precision на позиции i
            precision_at_i = num_relevant_found / i
            precisions.append(precision_at_i)

    if not precisions:
        return 0.0

    # Average Precision = среднее по всем позициям релевантных документов
    ap = sum(precisions) / len(relevant)
    return ap


def mean_average_precision(
    all_retrieved: list[list[Any]],
    all_relevant: list[list[Any]],
    k: int | None = None,
) -> float:
    """
    Вычисляет Mean Average Precision (MAP) - среднее значение AP по всем запросам

    MAP = (∑_{q=1}^Q AP(q)) / Q

    Args:
        all_retrieved (list[list[Any]]): Список списков полученных документов для каждого запроса
        all_relevant (list[list[Any]]): Список списков релевантных документов для каждого запроса
        k (int | None): Количество топ результатов для оценки. Если None, используются все результаты

    Returns:
        float: Значение MAP в диапазоне [0, 1]
    """
    if len(all_retrieved) != len(all_relevant):
        raise ValueError(
            f"Количество запросов не совпадает: {len(all_retrieved)} retrieved vs {len(all_relevant)} relevant"
        )

    if not all_retrieved:
        logger.warning("Список запросов пуст")
        return 0.0

    aps = []
    for retrieved, relevant in zip(all_retrieved, all_relevant, strict=False):
        ap = average_precision(retrieved, relevant, k)
        aps.append(ap)

    map_score = np.mean(aps)
    return float(map_score)


def dcg_at_k(retrieved: list[Any], relevant: list[Any], k: int) -> float:
    """
    Вычисляет Discounted Cumulative Gain (DCG@K) - метрику, учитывающую позицию документов

    DCG@K = ∑_{i=1}^k rel(i) / log2(i + 1)
    где rel(i) = 1 если документ на позиции i релевантен, иначе 0

    Args:
        retrieved (list[Any]): Список ID полученных документов (упорядочены по релевантности)
        relevant (list[Any]): Список ID релевантных документов (ground truth)
        k (int): Количество топ результатов для оценки

    Returns:
        float: Значение DCG@K
    """
    if k <= 0:
        raise ValueError(f"k должно быть положительным числом, получено: {k}")

    if not retrieved:
        return 0.0

    if not relevant:
        return 0.0

    retrieved_k = retrieved[:k]
    relevant_set = set(relevant)

    dcg = 0.0
    for i, doc_id in enumerate(retrieved_k, start=1):
        if doc_id in relevant_set:
            # rel(i) / log2(i + 1)
            dcg += 1.0 / np.log2(i + 1)

    return dcg


def ndcg_at_k(retrieved: list[Any], relevant: list[Any], k: int) -> float:
    """
    Вычисляет Normalized Discounted Cumulative Gain (NDCG@K)

    NDCG@K = DCG@K / IDCG@K
    где IDCG@K - идеальный DCG (если бы все релевантные документы были в начале)

    Args:
        retrieved (list[Any]): Список ID полученных документов (упорядочены по релевантности)
        relevant (list[Any]): Список ID релевантных документов (ground truth)
        k (int): Количество топ результатов для оценки

    Returns:
        float: Значение NDCG@K в диапазоне [0, 1]
    """
    if k <= 0:
        raise ValueError(f"k должно быть положительным числом, получено: {k}")

    if not retrieved:
        return 0.0

    if not relevant:
        return 0.0

    # Вычисляем DCG для текущего ranking
    dcg = dcg_at_k(retrieved, relevant, k)

    # Вычисляем идеальный DCG (все релевантные документы идут первыми)
    # Идеальный ranking - это все релевантные документы в начале
    ideal_retrieved = list(relevant)
    idcg = dcg_at_k(ideal_retrieved, relevant, k)

    if idcg == 0:
        return 0.0

    ndcg = dcg / idcg
    return ndcg


def mean_reciprocal_rank(all_retrieved: list[list[Any]], all_relevant: list[list[Any]]) -> float:
    """
    Вычисляет Mean Reciprocal Rank (MRR) - среднее обратного ранга первого релевантного документа

    MRR = (∑_{q=1}^Q 1/rank_q) / Q
    где rank_q - позиция первого релевантного документа для запроса q

    Args:
        all_retrieved (list[list[Any]]): Список списков полученных документов для каждого запроса
        all_relevant (list[list[Any]]): Список списков релевантных документов для каждого запроса

    Returns:
        float: Значение MRR в диапазоне [0, 1]
    """
    if len(all_retrieved) != len(all_relevant):
        raise ValueError(
            f"Количество запросов не совпадает: {len(all_retrieved)} retrieved vs {len(all_relevant)} relevant"
        )

    if not all_retrieved:
        logger.warning("Список запросов пуст")
        return 0.0

    reciprocal_ranks = []

    for retrieved, relevant in zip(all_retrieved, all_relevant, strict=False):
        if not retrieved or not relevant:
            reciprocal_ranks.append(0.0)
            continue

        relevant_set = set(relevant)

        # Находим позицию первого релевантного документа
        rank = None
        for i, doc_id in enumerate(retrieved, start=1):
            if doc_id in relevant_set:
                rank = i
                break

        if rank is not None:
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

    mrr = np.mean(reciprocal_ranks)
    return float(mrr)


def evaluate_retrieval(
    all_retrieved: list[list[Any]],
    all_relevant: list[list[Any]],
    k_values: list[int] = [1, 3, 5, 10, 20],
) -> dict[str, float]:
    """
    Вычисляет все метрики для оценки retrieval системы

    Args:
        all_retrieved (list[list[Any]]): Список списков полученных документов для каждого запроса
        all_relevant (list[list[Any]]): Список списков релевантных документов для каждого запроса
        k_values (list[int]): Список значений K для вычисления метрик

    Returns:
        dict[str, float]: Словарь с метриками
    """
    if len(all_retrieved) != len(all_relevant):
        raise ValueError(
            f"Количество запросов не совпадает: {len(all_retrieved)} retrieved vs {len(all_relevant)} relevant"
        )

    metrics = {}

    # Вычисляем метрики для каждого значения K
    for k in k_values:
        precisions = []
        recalls = []
        f1_scores = []
        ndcgs = []

        for retrieved, relevant in zip(all_retrieved, all_relevant, strict=False):
            precisions.append(precision_at_k(retrieved, relevant, k))
            recalls.append(recall_at_k(retrieved, relevant, k))
            f1_scores.append(f1_score_at_k(retrieved, relevant, k))
            ndcgs.append(ndcg_at_k(retrieved, relevant, k))

        metrics[f"precision@{k}"] = float(np.mean(precisions))
        metrics[f"recall@{k}"] = float(np.mean(recalls))
        metrics[f"f1@{k}"] = float(np.mean(f1_scores))
        metrics[f"ndcg@{k}"] = float(np.mean(ndcgs))

    # MAP и MRR
    metrics["map"] = mean_average_precision(all_retrieved, all_relevant)
    metrics["mrr"] = mean_reciprocal_rank(all_retrieved, all_relevant)

    return metrics

