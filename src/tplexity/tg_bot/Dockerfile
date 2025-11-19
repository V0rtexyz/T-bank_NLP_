FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей из корня проекта
COPY pyproject.toml poetry.lock /app/

# Установка Poetry и зависимостей
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry lock && \
    poetry install --only=main --no-root --no-interaction --no-ansi

# Копирование исходного кода
COPY src/ /app/src/

# Установка переменных окружения по умолчанию
# TODO: remove this after testing
# ENV PYTHONPATH=/app

ENV PYTHONPATH=/app/src

ENV GENERATION_API_URL=http://generation:8012
# Переменные окружения передаются через env_file в docker-compose.yml
# из файла src/tplexity/tg_bot/.env

# Порт для FastAPI
EXPOSE 8013

# Запуск tg_bot сервиса
CMD ["uvicorn", "tplexity.tg_bot.app:app", "--host", "0.0.0.0", "--port", "8013"]

