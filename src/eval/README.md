# Evaluation Retrieval

Скрипты для оценки качества retrieval системы.

## Быстрый старт

### 1. Загрузка данных в Qdrant

```bash
python src/eval/load_data.py
```

Загружает сообщения из `eval_data/messages_diverse_1000posts_all_channels.json` в Qdrant.

### 2. Запуск evaluation

```bash
python src/eval/eval_retrieval.py
```

Оценивает качество retrieval на запросах из `eval_data/queries.json`.

## Конфигурация

В файле `eval_retrieval.py` в функции `main()` есть словарь `CONFIG`:

```python
CONFIG = {
    "queries_path": "src/eval/eval_data/queries.json",
    "top_k": 10,  # <-- Измените K здесь
    "use_rerank": False,  # <-- Включить/выключить reranking
    "output_path": "src/eval/results.json",
    "num_queries": None,  # None = все запросы, или укажите число
}
```

## Метрики

Скрипт вычисляет **Precision@K** и **Recall@K** для разных значений K (1, 3, 5, 10).

- **Precision@K**: доля релевантных документов среди топ-K результатов
- **Recall@K**: доля найденных релевантных документов от всех релевантных

Результаты сохраняются в JSON файл с детальной информацией по каждому запросу.

## Структура файлов

```
src/eval/
├── load_data.py           # Загрузка данных в Qdrant
├── eval_retrieval.py      # Основной скрипт evaluation
├── metrics.py             # Функции для вычисления метрик
└── eval_data/
    ├── messages_diverse_1000posts_all_channels.json  # Документы
    └── queries.json       # Запросы для оценки
```

