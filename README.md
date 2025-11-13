# T-bank NLP

## Разработка

### Установка зависимостей

```bash
poetry install
```

### Настройка pre-commit hooks

После установки зависимостей настройте pre-commit hooks для автоматической проверки кода:

```bash
poetry run pre-commit install
```

Теперь при каждом коммите будут автоматически запускаться линтеры (ruff) для проверки и форматирования кода.

### Ручной запуск линтеров

Проверка кода:
```bash
poetry run ruff check .
```

Форматирование кода:
```bash
poetry run ruff format .
```

Исправление ошибок автоматически:
```bash
poetry run ruff check --fix .
```

### Проверка типов

```bash
poetry run mypy src/
```

### Запуск тестов

```bash
# Все тесты
poetry run pytest

# С покрытием кода
poetry run pytest --cov=src/tplexity --cov-report=term-missing
```

### Запуск pre-commit вручную

```bash
poetry run pre-commit run --all-files
```

## Внесение вклада

Перед началом работы ознакомьтесь с [CONTRIBUTING.md](CONTRIBUTING.md) для получения подробных инструкций по процессу разработки.

