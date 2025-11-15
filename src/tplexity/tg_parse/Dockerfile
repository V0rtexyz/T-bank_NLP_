FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей из корня проекта
COPY pyproject.toml poetry.lock /app/
COPY requirements.txt /app/

# Установка Poetry и зависимостей
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Копирование исходного кода
COPY src/ /app/src/

# Создание директории для данных
RUN mkdir -p /app/data

# Переменные окружения передаются через env_file в docker-compose.yml
# из файла src/tplexity/tg_parse/.env

# Установка переменных окружения по умолчанию
ENV PYTHONPATH=/app
ENV WEBHOOK_URL=http://retriever:8000/retriever/documents
ENV DATA_DIR=/app/data

# Порт для FastAPI
EXPOSE 8001

# Запуск tg_parse сервиса
CMD ["uvicorn", "tplexity.tg_parse.app:app", "--host", "0.0.0.0", "--port", "8001"]

