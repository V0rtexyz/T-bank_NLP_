"""
Утилиты для retry логики с exponential backoff
"""

import asyncio
import logging
import random
from functools import wraps
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryableError(Exception):
    """Исключение, которое можно повторить"""
    pass


class NonRetryableError(Exception):
    """Исключение, которое нельзя повторить"""
    pass


def is_retryable_error(error: Exception) -> bool:
    """
    Определяет, можно ли повторить запрос при данной ошибке

    Args:
        error: Исключение для проверки

    Returns:
        bool: True если ошибка retryable, False иначе
    """
    error_type = type(error).__name__
    error_str = str(error).lower()

    # Сетевые ошибки - можно повторить
    retryable_errors = (
        "ConnectionError",
        "TimeoutError",
        "Timeout",
        "ConnectionRefusedError",
        "ConnectionResetError",
        "httpx.ConnectError",
        "httpx.ConnectTimeout",
        "httpx.ReadTimeout",
        "httpx.WriteTimeout",
        "httpx.PoolTimeout",
        "httpx.NetworkError",
    )

    # HTTP ошибки - некоторые можно повторить
    retryable_http_statuses = (429, 500, 502, 503, 504)

    # Проверяем тип ошибки
    if any(retryable in error_type for retryable in retryable_errors):
        return True

    # Проверяем HTTP статус коды
    if hasattr(error, "status_code") and error.status_code in retryable_http_statuses:
        return True

    # Проверяем строковое представление
    if any(retryable in error_str for retryable in ["timeout", "connection", "network", "429", "500", "502", "503", "504"]):
        return True

    return False


async def retry_with_backoff(
    func: Callable[..., Any],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Выполняет функцию с retry логикой и exponential backoff

    Args:
        func: Асинхронная функция для выполнения
        max_retries: Максимальное количество попыток (включая первую)
        initial_delay: Начальная задержка в секундах
        max_delay: Максимальная задержка в секундах
        exponential_base: База для exponential backoff
        jitter: Добавлять ли случайную задержку (jitter)
        *args: Позиционные аргументы для функции
        **kwargs: Именованные аргументы для функции

    Returns:
        Результат выполнения функции

    Raises:
        Последнее исключение, если все попытки исчерпаны
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e

            # Проверяем, можно ли повторить
            if not is_retryable_error(e):
                logger.warning(
                    f"⚠️ [retry] Невозможно повторить запрос: {type(e).__name__}: {e}"
                )
                raise

            # Если это последняя попытка, выбрасываем исключение
            if attempt == max_retries - 1:
                logger.error(
                    f"❌ [retry] Все попытки исчерпаны ({max_retries}). Последняя ошибка: {type(e).__name__}: {e}"
                )
                raise

            # Вычисляем задержку с exponential backoff
            delay = min(initial_delay * (exponential_base ** attempt), max_delay)

            # Добавляем jitter (случайную задержку до 25% от delay)
            if jitter:
                jitter_amount = delay * 0.25 * random.random()
                delay += jitter_amount

            logger.warning(
                f"⚠️ [retry] Попытка {attempt + 1}/{max_retries} не удалась: {type(e).__name__}: {e}. "
                f"Повтор через {delay:.2f}с"
            )

            await asyncio.sleep(delay)

    # Этот код не должен выполняться, но на всякий случай
    if last_exception:
        raise last_exception

    raise RuntimeError("Unexpected error in retry_with_backoff")


def retry_async(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
):
    """
    Декоратор для автоматического retry асинхронных функций

    Args:
        max_retries: Максимальное количество попыток
        initial_delay: Начальная задержка в секундах
        max_delay: Максимальная задержка в секундах
        exponential_base: База для exponential backoff
        jitter: Добавлять ли случайную задержку

    Returns:
        Декоратор
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await retry_with_backoff(
                func,
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter,
                *args,
                **kwargs,
            )
        return wrapper
    return decorator

