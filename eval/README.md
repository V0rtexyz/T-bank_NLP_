# RAG Evaluation Pipeline

Reproducible pipeline для оценки RAG-системы с использованием LLM-as-a-judge и Ragas.

## 📁 Структура проекта

```
eval/
├── config/
│   ├── model_config.yaml      # Конфигурация моделей (inference, judge)
│   └── metrics_config.yaml     # Конфигурация метрик
├── data/
│   ├── messages_diverse_1000posts_all_channels.json  # Сообщения
│   ├── queries.json             # Запросы для оценки
│   └── sample_dataset.jsonl     # Пример dataset (минимум 5 примеров)
├── src/
│   ├── __init__.py
│   ├── dataset_loader.py       # Загрузка и валидация данных
│   ├── context_extractor.py    # Извлечение контекста
│   ├── inference_client.py     # Клиент для inference endpoint
│   ├── judge_prompts.py        # Промпты для LLM-as-a-judge
│   ├── custom_metrics.py       # Кастомные метрики через judge
│   ├── ragas_runner.py         # Интеграция с Ragas
│   └── main.py                 # Главный CLI модуль
├── outputs/
│   ├── results.parquet         # Результаты оценки (по примерам)
│   ├── summary.json            # Агрегированные метрики
│   └── logs/
│       └── run.log             # Логи выполнения
├── requirements.txt
└── README.md
```

## 🚀 Установка

1. Установите зависимости:

```bash
pip install -r eval/requirements.txt
```

2. Настройте конфигурацию (опционально):

Отредактируйте `eval/config/model_config.yaml`:

```yaml
inference_endpoint: ""  # URL вашего inference endpoint (пусто = mock)
inference_api_key: ""

judge:
  provider: qwen  # qwen (по умолчанию), openai, или mock
  model: ""  # для qwen игнорируется, для openai - название модели
  api_key: ""  # для qwen игнорируется, для openai - API ключ
  temperature: 0.0
  max_retries: 2
```

**По умолчанию используется Qwen** из сервиса generation (настройки берутся из `tplexity.llm_client.config`).

Если Qwen недоступен или указан другой провайдер:
- Для `openai`: требуется `OPENAI_API_KEY` или укажите `api_key` в конфиге
- Если провайдер не настроен: используется mock judge

## 📊 Использование

### Базовый запуск (с mock inference и Qwen judge по умолчанию)

```bash
python eval/src/main.py \
  --posts eval/data/messages_diverse_1000posts_all_channels.json \
  --queries eval/data/queries.json \
  --out eval/outputs/
```

### Автоматический запуск сервисов

Pipeline может автоматически запускать необходимые сервисы (generation, retriever):

```bash
# С автоматическим запуском сервисов через docker-compose (по умолчанию)
python eval/src/main.py \
  --posts eval/data/messages_diverse_1000posts_all_channels.json \
  --queries eval/data/queries.json \
  --out eval/outputs/ \
  --inference-endpoint http://localhost:8022/generation/generate

# Только 10 запросов для быстрого тестирования
python eval/src/main.py \
  --posts eval/data/messages_diverse_1000posts_all_channels.json \
  --queries eval/data/queries.json \
  --out eval/outputs/ \
  --inference-endpoint http://localhost:8022/generation/generate \
  --limit 10

# Без автоматического запуска сервисов
python eval/src/main.py \
  --posts eval/data/messages_diverse_1000posts_all_channels.json \
  --queries eval/data/queries.json \
  --out eval/outputs/ \
  --inference-endpoint http://localhost:8022/generation/generate \
  --no-auto-start-services

# Запуск сервисов напрямую (без docker-compose)
python eval/src/main.py \
  --posts eval/data/messages_diverse_1000posts_all_channels.json \
  --queries eval/data/queries.json \
  --out eval/outputs/ \
  --inference-endpoint http://localhost:8022/generation/generate \
  --no-docker
```

### Ручной запуск сервисов локально

Если хотите запустить сервисы вручную перед запуском eval:

```bash
# Вариант 1: Использовать готовый скрипт
./eval/start_services_local.sh

# Вариант 2: Вручную в отдельных терминалах

# Терминал 1: Retriever
cd /srv/nlp1/T-bank_NLP_
export PYTHONPATH=src:$PYTHONPATH
export RETRIEVER_API_URL=http://localhost:8020
python -m uvicorn tplexity.retriever.app:app --host 0.0.0.0 --port 8020

# Терминал 2: Generation
cd /srv/nlp1/T-bank_NLP_
export PYTHONPATH=src:$PYTHONPATH
export RETRIEVER_API_URL=http://localhost:8020
export LLM_PROVIDER=qwen
python -m uvicorn tplexity.generation.app:app --host 0.0.0.0 --port 8022

# Примечание: Redis не нужен, т.к. память отключена (session_id=None)

# Затем запускайте eval без auto-start
python eval/src/main.py \
  --posts eval/data/messages_diverse_1000posts_all_channels.json \
  --queries eval/data/queries.json \
  --out eval/outputs/ \
  --inference-endpoint http://localhost:8022/generation/generate \
  --no-auto-start-services

# Оставить сервисы запущенными после завершения
python eval/src/main.py \
  --posts eval/data/messages_diverse_1000posts_all_channels.json \
  --queries eval/data/queries.json \
  --out eval/outputs/ \
  --inference-endpoint http://localhost:8022/generation/generate \
  --keep-services
```

### С реальным inference endpoint

```bash
python eval/src/main.py \
  --posts eval/data/messages_diverse_1000posts_all_channels.json \
  --queries eval/data/queries.json \
  --out eval/outputs/ \
  --inference-endpoint http://localhost:8100/generate
```

### С Qwen judge (по умолчанию)

```bash
# Qwen используется автоматически из сервиса generation
python eval/src/main.py \
  --posts eval/data/messages_diverse_1000posts_all_channels.json \
  --queries eval/data/queries.json \
  --out eval/outputs/
```

### С OpenAI judge

```bash
export OPENAI_API_KEY=your_key_here

python eval/src/main.py \
  --posts eval/data/messages_diverse_1000posts_all_channels.json \
  --queries eval/data/queries.json \
  --out eval/outputs/ \
  --judge-model openai:gpt-4o-mini
```

### С Ragas (если установлен)

Ragas будет использовать Qwen LLM из конфигурации judge (по умолчанию) или указанную LLM:

```bash
python eval/src/main.py \
  --posts eval/data/messages_diverse_1000posts_all_channels.json \
  --queries eval/data/queries.json \
  --out eval/outputs/ \
  --use-ragas
```

**Важно:** Ragas использует LLM из конфигурации judge для оценки метрик. По умолчанию используется Qwen из `tplexity.llm_client.config`. Если нужна другая LLM, укажите через `--judge-model` или в конфиге.

### Все параметры

```bash
python eval/src/main.py \
  --posts <path_to_messages.json> \
  --queries <path_to_queries.json> \
  --out <output_dir> \
  --inference-endpoint <URL> \
  --judge-model <provider:model> \
  --window <window_size> \
  --config <path_to_config.yaml> \
  --use-ragas
```

**Параметры:**
- `--posts`: Путь к JSON файлу с сообщениями (обязательно)
- `--queries`: Путь к JSON файлу с запросами (обязательно)
- `--out`: Директория для сохранения результатов (по умолчанию: `eval/outputs/`)
- `--inference-endpoint`: URL inference endpoint (если пусто - используется mock)
- `--judge-model`: Модель для judge (например, `qwen`, `openai:gpt-4o-mini` или `mock`). По умолчанию используется `qwen`.
- `--window`: Размер окна для контекста (по умолчанию: 2)
- `--config`: Путь к конфигурационному файлу (по умолчанию: `eval/config/model_config.yaml`)
- `--use-ragas`: Использовать Ragas для оценки (если доступен)
- `--limit`: Ограничить количество обрабатываемых запросов (для тестирования)
- `--auto-start-services`: Автоматически запускать необходимые сервисы (по умолчанию: True)
- `--no-auto-start-services`: Не запускать сервисы автоматически
- `--use-docker`: Использовать docker-compose для запуска сервисов (по умолчанию: True)
- `--no-docker`: Запускать сервисы напрямую (без docker-compose)
- `--keep-services`: Не останавливать сервисы после завершения

## 📈 Метрики

Pipeline вычисляет следующие метрики:

### 1. **Relevance** (Релевантность)
Оценивает, насколько ответ релевантен вопросу. Шкала: 0.0 (не релевантен) - 1.0 (полностью релевантен).

**Как вычисляется:** LLM-as-a-judge оценивает соответствие ответа вопросу.

### 2. **Faithfulness** (Правдивость)
Оценивает, насколько ответ основан на предоставленных контекстах и не содержит галлюцинаций. Шкала: 0.0 (много галлюцинаций) - 1.0 (полностью основан на контекстах).

**Как вычисляется:** LLM-as-a-judge проверяет, подтверждаются ли утверждения в ответе контекстами.

### 3. **Hallucination Rate** (Частота галлюцинаций)
Показывает долю галлюцинированных утверждений в ответе. Шкала: 0.0 (нет галлюцинаций) - 1.0 (много галлюцинаций).

**Как вычисляется:** На основе списка галлюцинированных утверждений из метрики Faithfulness.

### 4. **Completeness** (Полнота)
Оценивает, насколько полно ответ покрывает вопрос. Шкала: 0.0 (ответ неполный) - 1.0 (полностью отвечает на вопрос).

**Как вычисляется:** LLM-as-a-judge проверяет, отвечает ли ответ на все аспекты вопроса.

### 5. **Latency** (Задержка)
Время генерации ответа в миллисекундах.

**Как вычисляется:** Измеряется время от запроса до получения ответа от inference endpoint.

### Дополнительные метрики (при использовании Ragas)

- **Context Precision**: Точность извлеченных контекстов
- **Context Recall**: Полнота извлеченных контекстов

**Примечание:** При использовании Ragas метрики `answer_relevancy`, `faithfulness`, `context_precision` и `context_recall` вычисляются через Ragas с использованием LLM из конфигурации judge (по умолчанию Qwen). Дополнительные метрики (`completeness`, `hallucination_rate`) вычисляются через кастомный judge.

## 📤 Результаты

После выполнения pipeline создаются следующие файлы:

### `outputs/results.parquet`
DataFrame с метриками для каждого примера:
- `query_id`: ID запроса
- `question`: Текст вопроса
- `n_contexts`: Количество контекстов
- `relevance`: Оценка релевантности
- `faithfulness`: Оценка правдивости
- `hallucination_rate`: Частота галлюцинаций
- `completeness`: Оценка полноты
- `latency_ms`: Задержка в миллисекундах
- `judge_errors`: Флаг ошибок judge

### `outputs/summary.json`
Агрегированные метрики:
- Средние значения (mean), медиана (median), стандартное отклонение (std)
- Минимальные и максимальные значения
- Количество примеров
- Top 20 примеров с наибольшим hallucination_rate

### `outputs/logs/run.log`
Логи выполнения pipeline.

## 🔧 Конфигурация

### `config/model_config.yaml`

```yaml
inference_endpoint: ""  # URL endpoint или пусто для mock
inference_api_key: ""
inference_timeout: 120

judge:
  provider: qwen  # qwen (по умолчанию), openai, или mock
  model: ""  # для qwen игнорируется, для openai - название модели
  api_key: ""  # для qwen игнорируется, для openai - API ключ
  temperature: 0.0
  max_retries: 2
  timeout: 120

batch_size: 10
```

### `config/metrics_config.yaml`

```yaml
metrics:
  - relevance
  - faithfulness
  - hallucination_rate
  - completeness
  - latency

thresholds:
  relevance: 0.7
  faithfulness: 0.8
```

## 📝 Формат входных данных

### `messages_diverse_1000posts_all_channels.json`

Массив объектов сообщений:

```json
[
  {
    "id": 7078,
    "channel_id": 1418181070,
    "text": "Текст сообщения...",
    "date": "2025-11-14T12:14:02+00:00",
    "link": "https://t.me/...",
    "views": 8318,
    ...
  }
]
```

### `queries.json`

Массив объектов запросов:

```json
[
  {
    "query": "Текст вопроса",
    "id_channel": 1418181070,
    "id_message": 7078,
    "query_num": 1
  }
]
```

## 🚀 Локальный запуск сервисов (без Docker)

### Быстрый старт

Используйте готовый скрипт для запуска всех сервисов:

```bash
# Запуск всех сервисов
./eval/start_services_local.sh

# Остановка всех сервисов
./eval/stop_services_local.sh
```

### Требования

1. **Python зависимости**: 
   - Все зависимости из `pyproject.toml` должны быть установлены
   - `PYTHONPATH` должен включать `src/`

3. **Переменные окружения**:
   - Настройки в `src/tplexity/retriever/.env` (для Retriever)
   - Настройки в `src/tplexity/generation/.env` (для Generation)
   - Настройки в `src/tplexity/llm_client/.env` (для Qwen LLM)

### Ручной запуск в отдельных терминалах

#### 1. Retriever (порт 8020)

```bash
cd /srv/nlp1/T-bank_NLP_
export PYTHONPATH=src:$PYTHONPATH
export RETRIEVER_API_URL=http://localhost:8020

# Убедитесь, что есть .env файл с настройками Qdrant
python -m uvicorn tplexity.retriever.app:app --host 0.0.0.0 --port 8020
```

#### 2. Generation (порт 8022)

```bash
cd /srv/nlp1/T-bank_NLP_
export PYTHONPATH=src:$PYTHONPATH
export RETRIEVER_API_URL=http://localhost:8020
export LLM_PROVIDER=qwen

# Убедитесь, что есть .env файлы с настройками
python -m uvicorn tplexity.generation.app:app --host 0.0.0.0 --port 8022
```

**Примечание:** Redis не нужен, т.к. память отключена для eval (session_id=None).

### Проверка работы сервисов

```bash
# Проверка Retriever
curl http://localhost:8020/health

# Проверка Generation
curl http://localhost:8022/health
```

### Запуск eval с локальными сервисами

После запуска сервисов вручную:

```bash
python eval/src/main.py \
  --posts eval/data/messages_diverse_1000posts_all_channels.json \
  --queries eval/data/queries.json \
  --out eval/outputs/ \
  --inference-endpoint http://localhost:8022/generation/generate \
  --no-auto-start-services  # Не запускать сервисы автоматически
```

Или с автоматическим запуском (но без Docker):

```bash
python eval/src/main.py \
  --posts eval/data/messages_diverse_1000posts_all_channels.json \
  --queries eval/data/queries.json \
  --out eval/outputs/ \
  --inference-endpoint http://localhost:8022/generation/generate \
  --no-docker  # Запускать через uvicorn, а не docker-compose
```

**Примечание:** При использовании `--no-docker`:
- Retriever и Generation запускаются через `uvicorn` в фоне
- Redis не нужен, т.к. память отключена (session_id=None)
- Переменные окружения автоматически настраиваются для локального запуска

## 🛠️ Разработка

### Структура модулей

- **dataset_loader.py**: Загрузка и валидация входных данных
- **context_extractor.py**: Извлечение контекста (целевое сообщение + окно соседних)
- **inference_client.py**: Клиент для вызова inference endpoint (с поддержкой mock)
- **judge_prompts.py**: Промпты для LLM-as-a-judge (на русском языке)
- **custom_metrics.py**: Реализация метрик через judge модель
- **ragas_runner.py**: Интеграция с Ragas (с fallback на кастомные метрики)
- **main.py**: Главный CLI модуль, объединяющий все компоненты

### Обработка ошибок

Pipeline обрабатывает ошибки gracefully:
- Если inference endpoint недоступен - используется mock
- Если judge модель недоступна - используется mock judge
- Если Ragas не установлен - используется fallback на кастомные метрики
- Ошибки отдельных примеров логируются, но не останавливают выполнение

## 📄 Лицензия

Внутренний проект для оценки RAG-системы.

