"""
Клиент для взаимодействия с Generation API (FastAPI микросервис).
"""

import logging
import httpx
from typing import Optional

from tplexity.tg_bot.config import settings

logger = logging.getLogger(__name__)


class GenerationClient:
    """Клиент для отправки запросов к Generation API."""
    
    def __init__(self, base_url: str, timeout: float = 60.0):
        """
        Инициализация клиента.
        
        Args:
            base_url: Базовый URL сервиса (например, http://localhost:8000)
            timeout: Таймаут запросов в секундах
        """
        # Убираем trailing slash если есть
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._httpx_client: Optional[httpx.AsyncClient] = None
    
    async def _ensure_client(self) -> None:
        """Инициализирует HTTP клиент, если он еще не создан."""
        if self._httpx_client is None:
            timeout_config = httpx.Timeout(self.timeout)
            self._httpx_client = httpx.AsyncClient(
                timeout=timeout_config,
                headers={"Content-Type": "application/json"}
            )
            logger.info("Generation client initialized")
    
    async def send_message(
        self,
        message_text: str,
        top_k: Optional[int] = None,
        use_rerank: Optional[bool] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Отправляет запрос на генерацию ответа в Generation API.
        
        Args:
            message_text: Текст вопроса пользователя
            top_k: Количество релевантных документов (опционально)
            use_rerank: Использовать ли reranking (опционально)
            temperature: Температура генерации (опционально)
            max_tokens: Максимальное количество токенов (опционально)
            
        Returns:
            str: Сгенерированный ответ
            
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
            
            logger.info(f"Received response from generation API: {answer[:50]}...")
            return answer
            
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e))
            except:
                error_detail = str(e)
            
            logger.error(f"HTTP error from generation API: {error_detail}")
            raise ValueError(f"Ошибка от generation API: {error_detail}") from e
        except httpx.RequestError as e:
            logger.error(f"Request error to generation API: {e}")
            raise ValueError(f"Ошибка подключения к generation API: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
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
