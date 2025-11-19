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
            logger.info("[tg_bot][service_client] Generation client инициализирован")

    async def send_message(  # noqa: C901
        self,
        message_text: str,
        top_k: int | None = None,
        use_rerank: bool | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        llm_provider: str | None = None,
        session_id: str | None = None,
    ) -> tuple[str, str, list[dict], float | None, float, float]:
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
            tuple[str, str, list[dict], float | None, float, float]:
            Кортеж (ответ, ответ (для обратной совместимости), список источников, время поиска, время генерации, общее время)

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
            logger.info(f"📤 [tg_bot][service_client] Отправка запроса с llm_provider={llm_provider}")
        else:
            logger.info(
                "📤 [tg_bot][service_client] Отправка запроса без указания llm_provider (будет использована модель по умолчанию)"
            )
        if session_id is not None:
            payload["session_id"] = session_id
            logger.debug(f"📤 [tg_bot][service_client] Отправка запроса с session_id={session_id}")

        try:
            logger.info(f"[tg_bot][service_client] Отправка запроса к generation API: {message_text[:50]}...")
            response = await self._httpx_client.post(url, json=payload)
            response.raise_for_status()  # Вызовет исключение при ошибке HTTP

            response_data = response.json()

            # Извлекаем ответ из FastAPI response
            answer = response_data.get("answer", "")

            if not answer:
                logger.warning("[tg_bot][service_client] Получен пустой ответ от generation API")
                error_message = "Не удалось получить ответ от сервиса генерации."
                return error_message, error_message, [], None, 0.0, 0.0

            # Извлекаем источники из FastAPI response
            sources = response_data.get("sources", [])

            # Извлекаем время генерации
            search_time = response_data.get("search_time")
            generation_time = response_data.get("generation_time", 0.0)
            total_time = response_data.get("total_time", 0.0)

            # Логируем структуру источников для отладки
            logger.info(f"📋 [tg_bot][service_client] Получено источников: {len(sources)}")
            if sources:
                logger.info(f"📋 [tg_bot][service_client] Первый источник (структура): {sources[0]}")
                if isinstance(sources[0], dict):
                    logger.info(f"📋 [tg_bot][service_client] Первый источник (metadata): {sources[0].get('metadata')}")

            logger.info(f"[tg_bot][service_client] Получен ответ от generation API: answer={len(answer)} chars (sources: {len(sources)})")
            # Возвращаем один ответ дважды для обратной совместимости с кодом бота
            return answer, answer, sources, search_time, generation_time, total_time

        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e))
            except Exception as e:
                error_detail = str(e)
                print(error_detail)

            logger.error(f"[tg_bot][service_client] HTTP ошибка от generation API: {error_detail}")
            raise ValueError(f"Ошибка от generation API: {error_detail}") from e
        except httpx.RequestError as e:
            logger.error(f"[tg_bot][service_client] Ошибка запроса к generation API: {e}")
            raise ValueError(f"Ошибка подключения к generation API: {str(e)}") from e
        except Exception as e:
            logger.error(f"[tg_bot][service_client] Неожиданная ошибка: {e}")
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
            logger.info(f"🗑️ [tg_bot][service_client] Очистка истории сессии: {session_id}")
            response = await self._httpx_client.post(url, json=payload)
            response.raise_for_status()

            response_data = response.json()
            if response_data.get("success"):
                logger.info(f"✅ [tg_bot][service_client] История сессии {session_id} успешно очищена")
            else:
                logger.warning(f"⚠️ [tg_bot][service_client] Очистка истории сессии {session_id} не удалась")

        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e))
            except Exception:
                error_detail = str(e)

            logger.error(f"[tg_bot][service_client] HTTP ошибка от generation API при очистке сессии: {error_detail}")
            raise ValueError(f"Ошибка от generation API при очистке сессии: {error_detail}") from e
        except httpx.RequestError as e:
            logger.error(f"[tg_bot][service_client] Ошибка запроса к generation API при очистке сессии: {e}")
            raise ValueError(f"Ошибка подключения к generation API при очистке сессии: {str(e)}") from e
        except Exception as e:
            logger.error(f"[tg_bot][service_client] Неожиданная ошибка при очистке сессии: {e}")
            raise

    async def generate_short_answer(
        self,
        detailed_answer: str,
        llm_provider: str | None = None,
    ) -> str:
        """
        Генерирует краткий ответ на основе детального ответа.

        Args:
            detailed_answer: Детальный ответ для сокращения
            llm_provider: Провайдер LLM для использования (опционально)

        Returns:
            str: Краткий ответ

        Raises:
            httpx.HTTPError: При ошибке HTTP запроса
            ValueError: При ошибке валидации ответа
        """
        await self._ensure_client()

        # Формируем URL эндпоинта
        url = f"{self.base_url}/generation/generate-short-answer"

        # Формируем тело запроса
        payload = {"detailed_answer": detailed_answer}
        if llm_provider is not None:
            payload["llm_provider"] = llm_provider
            logger.info(f"📤 [tg_bot][service_client] Отправка запроса на краткий ответ с llm_provider={llm_provider}")

        try:
            logger.info(f"[tg_bot][service_client] Отправка запроса на генерацию краткого ответа...")
            response = await self._httpx_client.post(url, json=payload)
            response.raise_for_status()

            response_data = response.json()

            # Извлекаем краткий ответ из FastAPI response
            short_answer = response_data.get("short_answer", "")

            if not short_answer:
                logger.warning("[tg_bot][service_client] Получен пустой краткий ответ от generation API")
                return detailed_answer  # Возвращаем детальный ответ как fallback

            logger.info(f"[tg_bot][service_client] Получен краткий ответ: {len(short_answer)} chars")
            return short_answer

        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e))
            except Exception:
                error_detail = str(e)

            logger.error(f"[tg_bot][service_client] HTTP ошибка от generation API при генерации краткого ответа: {error_detail}")
            raise ValueError(f"Ошибка от generation API: {error_detail}") from e
        except httpx.RequestError as e:
            logger.error(f"[tg_bot][service_client] Ошибка запроса к generation API при генерации краткого ответа: {e}")
            raise ValueError(f"Ошибка подключения к generation API: {str(e)}") from e
        except Exception as e:
            logger.error(f"[tg_bot][service_client] Неожиданная ошибка при генерации краткого ответа: {e}")
            raise

    async def close(self) -> None:
        """Закрывает соединения с сервисом."""
        if self._httpx_client:
            await self._httpx_client.aclose()
            self._httpx_client = None
            logger.info("[tg_bot][service_client] Generation client закрыт")


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
