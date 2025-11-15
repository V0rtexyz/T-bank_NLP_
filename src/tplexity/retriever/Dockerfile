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

# Установка переменных окружения по умолчанию
ENV PYTHONPATH=/app
# Переменные окружения передаются через env_file в docker-compose.yml
# из файла src/tplexity/retriever/.env

# Порт для FastAPI
EXPOSE 8000

# Запуск retriever сервиса
CMD ["uvicorn", "tplexity.retriever.app:app", "--host", "0.0.0.0", "--port", "8000"]

