"""Скрипт для оценки retrieval системы"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Добавляем src в путь
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from tqdm import tqdm
from tplexity.retriever.retriever_service import RetrieverService
from eval.metrics import precision_at_k, recall_at_k

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def evaluate_retrieval(
    queries_path: str = "src/eval/eval_data/queries.json",
    top_k: int = 5,
    use_rerank: bool = False,
    output_path: str = "src/eval/results.json",
    num_queries: int = None,
):
    """
    Оценка retrieval системы
    
    Args:
        queries_path: Путь к файлу с запросами
        top_k: Количество документов для поиска (K)
        use_rerank: Использовать ли reranking
        output_path: Путь для сохранения результатов
        num_queries: Количество запросов для оценки (None = все)
    """
    logger.info("=" * 80)
    logger.info("EVALUATION RETRIEVAL")
    logger.info("=" * 80)

    # Загрузка запросов
    logger.info(f"🔄 Загрузка запросов из {queries_path}...")
    with open(queries_path, "r", encoding="utf-8") as f:
        all_queries = json.load(f)

    if num_queries is not None and num_queries < len(all_queries):
        queries = all_queries[:num_queries]
        logger.info(f"✅ Используется {num_queries} запросов из {len(all_queries)}")
    else:
        queries = all_queries
        logger.info(f"✅ Используются все {len(queries)} запросов")

    # Инициализация RetrieverService
    logger.info("🔄 Инициализация RetrieverService...")
    retriever = RetrieverService()

    # Оценка для разных значений K
    k_values = [1, 3, 5, 10]
    k_values = [k for k in k_values if k <= top_k]
    
    logger.info(f"\n🔍 Начало оценки (top_k={top_k}, use_rerank={use_rerank})...")
    logger.info(f"Будут вычислены метрики для K: {k_values}")

    # Хранение результатов для каждого K
    all_precisions = {k: [] for k in k_values}
    all_recalls = {k: [] for k in k_values}
    results_detailed = []

    for idx, query_data in enumerate(tqdm(queries, desc="Evaluating")):
        query_text = query_data["query"]
        ground_truth_id = f"{query_data['id_channel']}_{query_data['id_message']}"

        # Выполняем поиск
        try:
            search_results = await retriever.search(
                query=query_text,
                top_k=top_k * 2,  # Берем больше для reranking
                top_n=top_k,
                use_rerank=use_rerank,
            )
        except Exception as e:
            logger.error(f"❌ Ошибка при поиске для запроса {idx+1}: {e}")
            for k in k_values:
                all_precisions[k].append(0.0)
                all_recalls[k].append(0.0)
            continue

        # Извлекаем ID документов
        retrieved_ids = [doc_id for doc_id, _, _, _ in search_results]

        # Для каждого K вычисляем метрики
        query_metrics = {}
        for k in k_values:
            # Ground truth - только один релевантный документ
            relevant_ids = [ground_truth_id]
            retrieved_k = retrieved_ids[:k]

            # Precision@K = 1/K если документ найден в топ-K, иначе 0
            # Recall@K = 1 если документ найден в топ-K, иначе 0 (так как у нас только 1 релевантный документ)
            precision = precision_at_k(retrieved_k, relevant_ids, k)
            recall = recall_at_k(retrieved_k, relevant_ids, k)

            all_precisions[k].append(precision)
            all_recalls[k].append(recall)
            
            query_metrics[f"precision@{k}"] = precision
            query_metrics[f"recall@{k}"] = recall

        # Сохраняем детальную информацию
        results_detailed.append({
            "query": query_text,
            "query_id": query_data.get("id_message"),
            "ground_truth_id": ground_truth_id,
            "retrieved_ids": retrieved_ids[:top_k],
            "found_in_results": ground_truth_id in retrieved_ids,
            "position": retrieved_ids.index(ground_truth_id) + 1 if ground_truth_id in retrieved_ids else None,
            **query_metrics,
        })

        if (idx + 1) % 50 == 0:
            logger.info(f"Обработано {idx + 1}/{len(queries)} запросов...")

    # Вычисляем средние метрики для каждого K
    avg_metrics = {}
    for k in k_values:
        avg_precision = sum(all_precisions[k]) / len(all_precisions[k]) if all_precisions[k] else 0.0
        avg_recall = sum(all_recalls[k]) / len(all_recalls[k]) if all_recalls[k] else 0.0
        avg_metrics[f"precision@{k}"] = avg_precision
        avg_metrics[f"recall@{k}"] = avg_recall

    # Результаты
    results = {
        "config": {
            "num_queries": len(queries),
            "top_k": top_k,
            "use_rerank": use_rerank,
            "k_values": k_values,
        },
        "metrics": avg_metrics,
        "detailed_results": results_detailed,
    }

    # Сохранение результатов
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info(f"\n✅ Результаты сохранены в {output_path}")

    # Вывод результатов
    logger.info("\n" + "=" * 80)
    logger.info("📊 РЕЗУЛЬТАТЫ EVALUATION")
    logger.info("=" * 80)
    logger.info(f"Количество запросов: {len(queries)}")
    logger.info(f"Top-K: {top_k}")
    logger.info(f"Use rerank: {use_rerank}")
    logger.info(f"\n🎯 Метрики:")
    
    for k in k_values:
        precision = avg_metrics[f"precision@{k}"]
        recall = avg_metrics[f"recall@{k}"]
        logger.info(f"  K={k}:")
        logger.info(f"    Precision@{k}: {precision:.4f} ({precision*100:.2f}%)")
        logger.info(f"    Recall@{k}: {recall:.4f} ({recall*100:.2f}%)")
    
    logger.info("=" * 80)

    return results


async def main():
    """Основная функция"""
    
    # === КОНФИГУРАЦИЯ ===
    # Здесь можно легко изменить параметры оценки
    
    CONFIG = {
        "queries_path": "src/eval/eval_data/queries.json",
        "top_k": 10,  # <-- Измените K здесь
        "use_rerank": False,  # <-- Включить/выключить reranking
        "output_path": "src/eval/results.json",
        "num_queries": None,  # None = все запросы, или укажите число
    }
    
    # ====================

    logger.info("🚀 Запуск evaluation...")
    logger.info(f"Конфигурация:")
    for key, value in CONFIG.items():
        logger.info(f"  {key}: {value}")

    try:
        await evaluate_retrieval(**CONFIG)
    except Exception as e:
        logger.error(f"❌ Ошибка при выполнении evaluation: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

