"""Модуль для оценки качества retrieval системы с использованием LLM"""

try:
    # Пытаемся импортировать как из src
    from eval.metrics import (
        average_precision,
        dcg_at_k,
        evaluate_retrieval,
        f1_score_at_k,
        mean_average_precision,
        mean_reciprocal_rank,
        ndcg_at_k,
        precision_at_k,
        recall_at_k,
    )
except ImportError:
    # Если не получилось, добавляем src в путь
    import sys
    from pathlib import Path
    src_path = Path(__file__).parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    from eval.metrics import (
        average_precision,
        dcg_at_k,
        evaluate_retrieval,
        f1_score_at_k,
        mean_average_precision,
        mean_reciprocal_rank,
        ndcg_at_k,
        precision_at_k,
        recall_at_k,
    )

__all__ = [
    "precision_at_k",
    "recall_at_k",
    "f1_score_at_k",
    "average_precision",
    "mean_average_precision",
    "dcg_at_k",
    "ndcg_at_k",
    "mean_reciprocal_rank",
    "evaluate_retrieval",
]

