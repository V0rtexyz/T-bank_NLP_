"""
Клиент для взаимодействия с Generation API (FastAPI микросервис).
"""

import logging

import httpx

from tplexity.tg_bot.config import settings

logger = logging.getLogger(__name__)


class GenerationClient:
    """Клиент для отправки запросов к Generation API."""

    def __init__(self, base_url: str, timeout: float = 60.0):
        """
        Инициализация клиента.

        Args:
            base_url: Базовый URL сервиса (например, http://localhost:8010)
            timeout: Таймаут запросов в секундах
        """
        # Убираем trailing slash если есть
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._httpx_client: httpx.AsyncClient | None = None

    async def _ensure_client(self) -> None:
        """Инициализирует HTTP клиент, если он еще не создан."""
        if self._httpx_client is None:
            timeout_config = httpx.Timeout(self.timeout)
            self._httpx_client = httpx.AsyncClient(timeout=timeout_config, headers={"Content-Type": "application/json"})
            logger.info("Generation client initialized")

    async def send_message(
        self,
        message_text: str,
        top_k: int | None = None,
        use_rerank: bool | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        llm_provider: str | None = None,
        session_id: str | None = None,
    ) -> tuple[str, list[dict]]:
        """
        Отправляет запрос на генерацию ответа в Generation API.

        Args:
            message_text: Текст вопроса пользователя
            top_k: Количество релевантных документов (опционально)
            use_rerank: Использовать ли reranking (опционально)
            temperature: Температура генерации (опционально)
            max_tokens: Максимальное количество токенов (опционально)
            llm_provider: Провайдер LLM для использования (опционально)
            session_id: Идентификатор сессии для сохранения истории диалога (опционально)

        Returns:
            tuple[str, list[dict]]: Кортеж (сгенерированный ответ, список источников с метаданными)

        Raises:
            httpx.HTTPError: При ошибке HTTP запроса
            ValueError: При ошибке валидации ответа
        """
        await self._ensure_client()

        # Формируем URL эндпоинта
        url = f"{self.base_url}/generation/generate"

        # Формируем тело запроса
        payload = {"query": message_text}
        if top_k is not None:
            payload["top_k"] = top_k
        if use_rerank is not None:
            payload["use_rerank"] = use_rerank
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if llm_provider is not None:
            payload["llm_provider"] = llm_provider
            logger.info(f"📤 [tg_bot.service_client] Отправка запроса с llm_provider={llm_provider}")
        else:
            logger.info("📤 [tg_bot.service_client] Отправка запроса без указания llm_provider (будет использована модель по умолчанию)")
        if session_id is not None:
            payload["session_id"] = session_id
            logger.debug(f"📤 [tg_bot.service_client] Отправка запроса с session_id={session_id}")

        try:
            logger.info(f"Sending request to generation API: {message_text[:50]}...")
            response = await self._httpx_client.post(url, json=payload)
            response.raise_for_status()  # Вызовет исключение при ошибке HTTP

            response_data = response.json()

            # Извлекаем ответ из FastAPI response
            answer = response_data.get("answer", "")

            if not answer:
                logger.warning("Empty answer received from generation API")
                answer = "Не удалось получить ответ от сервиса генерации."

            # Извлекаем источники из FastAPI response
            sources = response_data.get("sources", [])
            
            # Логируем структуру источников для отладки
            logger.info(f"📋 [tg_bot.service_client] Получено источников: {len(sources)}")
            if sources:
                logger.info(f"📋 [tg_bot.service_client] Первый источник (структура): {sources[0]}")
                if isinstance(sources[0], dict):
                    logger.info(f"📋 [tg_bot.service_client] Первый источник (metadata): {sources[0].get('metadata')}")

            logger.info(f"Received response from generation API: {answer[:50]}... (sources: {len(sources)})")
            return answer, sources

        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e))
            except Exception as e:
                error_detail = str(e)
                print(error_detail)

            logger.error(f"HTTP error from generation API: {error_detail}")
            raise ValueError(f"Ошибка от generation API: {error_detail}") from e
        except httpx.RequestError as e:
            logger.error(f"Request error to generation API: {e}")
            raise ValueError(f"Ошибка подключения к generation API: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    async def clear_session(self, session_id: str) -> None:
        """
        Очищает историю диалога для указанной сессии.

        Args:
            session_id: Идентификатор сессии для очистки

        Raises:
            ValueError: При ошибке запроса к API
        """
        await self._ensure_client()

        url = f"{self.base_url}/generation/clear-session"
        payload = {"session_id": session_id}

        try:
            logger.info(f"🗑️ [tg_bot.service_client] Очистка истории сессии: {session_id}")
            response = await self._httpx_client.post(url, json=payload)
            response.raise_for_status()

            response_data = response.json()
            if response_data.get("success"):
                logger.info(f"✅ [tg_bot.service_client] История сессии {session_id} успешно очищена")
            else:
                logger.warning(f"⚠️ [tg_bot.service_client] Очистка истории сессии {session_id} не удалась")

        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e))
            except Exception:
                error_detail = str(e)

            logger.error(f"HTTP error from generation API when clearing session: {error_detail}")
            raise ValueError(f"Ошибка от generation API при очистке сессии: {error_detail}") from e
        except httpx.RequestError as e:
            logger.error(f"Request error to generation API when clearing session: {e}")
            raise ValueError(f"Ошибка подключения к generation API при очистке сессии: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error when clearing session: {e}")
            raise

    async def close(self) -> None:
        """Закрывает соединения с сервисом."""
        if self._httpx_client:
            await self._httpx_client.aclose()
            self._httpx_client = None
            logger.info("Generation client closed")


def create_service_client() -> GenerationClient:
    """
    Создает клиент Generation API из настроек.

    Returns:
        Настроенный клиент Generation API

    Raises:
        ValueError: Если не указаны необходимые настройки
    """
    if not settings.generation_api_url or settings.generation_api_url == "your_generation_api_url_here":
        raise ValueError("GENERATION_API_URL не установлен в .env файле")

    return GenerationClient(base_url=settings.generation_api_url, timeout=settings.generation_api_timeout)
