# Архитектура T-Bank NLP системы

## Общая схема работы

```
Пользователь → Telegram Bot / API
    ↓
Generation Service (RAG)
    ↓
ReAct Agent (решает, нужен ли retriever)
    ↓
Retriever Service (гибридный поиск)
    ↓
Qdrant (векторная БД)
    ↓
LLM (генерация ответа)
```

## Пайплайн поиска документов (Retriever)

### 1. Query Reformulation (опционально)
- **Что делает**: Переформулирует запрос пользователя через LLM для лучшего поиска
- **Настройка**: `src/tplexity/retriever/.env`
  ```env
  ENABLE_QUERY_REFORMULATION=true
  QUERY_REFORMULATION_LLM_PROVIDER=qwen
  ```

### 2. Prefetch (гибридный поиск)
- **Sparse Search (BM25)**: Поиск по ключевым словам с лемматизацией
- **Dense Search (FRIDA)**: Семантический поиск по embeddings
- **RRF (Reciprocal Rank Fusion)**: Объединение результатов двух поисков

**Параметры:**
- `prefetch_ratio` (по умолчанию: 1.0) - во сколько раз больше документов брать для prefetch
  - Например, если `top_k=20` и `prefetch_ratio=1.5`, то для каждого типа поиска (sparse/dense) будет взято 30 документов
  - Настройка: `src/tplexity/retriever/.env` → `PREFETCH_RATIO=1.0`

### 3. Reranking
- **Что делает**: Переранжирует документы через Jina Reranker v3 для более точного порядка
- **Параметры:**
  - `top_k` - количество документов ДО реранка (по умолчанию: 20)
  - `top_n` - количество документов ПОСЛЕ реранка, которые возвращаются (по умолчанию: 10)
  - `use_rerank` - использовать ли reranking (по умолчанию: true)

## Параметры поиска документов

### Где настраиваются:

#### 1. В конфигурации Retriever (по умолчанию)
**Файл**: `src/tplexity/retriever/.env`
```env
# Количество документов до реранка
TOP_K=20

# Количество документов после реранка (возвращаемые)
TOP_N=10

# Коэффициент для prefetch (во сколько раз больше брать документов)
PREFETCH_RATIO=1.0
```

#### 2. Через API запрос (переопределяет значения по умолчанию)

**Generation API** (`POST /generation/generate`):
```json
{
  "query": "Что такое банковский вклад?",
  "top_k": 15,        // Количество документов (переопределяет значение из config)
  "use_rerank": true  // Использовать ли reranking
}
```

**Retriever API** (`POST /retriever/search`):
```json
{
  "query": "Что такое банковский вклад?",
  "top_k": 20,        // Документы до реранка
  "top_n": 10,        // Документы после реранка (возвращаемые)
  "use_rerank": true  // Использовать ли reranking
}
```

#### 3. В коде Generation Service
В `generation_service.py` при вызове retriever:
```python
context_documents = await self.retriever_client.search(
    query=query,
    top_k=top_k,      # Если None, используется из retriever config
    top_n=top_k,      # В generation всегда равно top_k
    use_rerank=use_rerank
)
```

## Как работает весь процесс

### Пример запроса: "Что такое банковский вклад?"

1. **Generation Service получает запрос**
   - ReAct агент решает: нужен ли retriever? → YES (финансовый вопрос)

2. **Retriever Service выполняет поиск:**
   ```
   Query Reformulation (опционально)
   ↓
   Prefetch:
     - BM25 поиск: берет top_k * prefetch_ratio документов (например, 20 * 1.0 = 20)
     - Dense поиск: берет top_k * prefetch_ratio документов (например, 20 * 1.0 = 20)
   ↓
   RRF объединяет результаты → получаем top_k документов (20)
   ↓
   Reranking (если use_rerank=true):
     - Переранжирует 20 документов через Jina Reranker
     - Возвращает top_n лучших (10)
   ```

3. **Generation Service формирует промпт:**
   - Берет top_n документов (10) из retriever
   - Формирует промпт с контекстом
   - Использует `SYSTEM_PROMPT_WITH_RETRIEVER` (требует цитаты и разделение на подробный/краткий ответ)

4. **LLM генерирует ответ:**
   - Использует контекст из 10 документов
   - Формирует ответ с цитатами [1], [2], ...
   - Разделяет на подробный и краткий ответ

## Как изменить параметры

### Вариант 1: Изменить значения по умолчанию
Отредактируйте `src/tplexity/retriever/.env`:
```env
TOP_K=30        # Больше документов до реранка
TOP_N=15        # Больше документов после реранка
PREFETCH_RATIO=1.5  # Брать в 1.5 раза больше для prefetch
```

### Вариант 2: Передать параметры в API запросе
```python
# Через Generation API
response = await client.post(
    "http://localhost:8012/generation/generate",
    json={
        "query": "Что такое банковский вклад?",
        "top_k": 25,        # Переопределяет значение по умолчанию
        "use_rerank": True
    }
)
```

### Вариант 3: Изменить в коде
В `generation_service.py`:
```python
# Изменить значение по умолчанию для top_k
context_documents = await self.retriever_client.search(
    query=query,
    top_k=top_k or 30,  # Вместо значения из config
    top_n=top_k or 30,
    use_rerank=use_rerank
)
```

## Важные моменты

1. **top_k vs top_n:**
   - `top_k` - сколько документов брать для реранка (больше = лучше качество, но медленнее)
   - `top_n` - сколько документов возвращать после реранка (меньше = меньше контекста для LLM)

2. **prefetch_ratio:**
   - Больше значение = больше документов для prefetch = лучше покрытие поиска, но медленнее
   - Рекомендуется: 1.0 - 2.0

3. **use_rerank:**
   - `true` - лучше качество, но медленнее (нужен GPU для Jina Reranker)
   - `false` - быстрее, но качество может быть хуже

4. **В Generation Service:**
   - `top_k` передается как `top_k` и `top_n` одновременно
   - То есть если передать `top_k=15`, то retriever вернет 15 документов после реранка

## Рекомендуемые значения

### Для быстрого поиска:
```env
TOP_K=10
TOP_N=5
PREFETCH_RATIO=1.0
USE_RERANK=false
```

### Для качественного поиска:
```env
TOP_K=30
TOP_N=15
PREFETCH_RATIO=1.5
USE_RERANK=true
```

### Для баланса скорости и качества:
```env
TOP_K=20
TOP_N=10
PREFETCH_RATIO=1.0
USE_RERANK=true
```

