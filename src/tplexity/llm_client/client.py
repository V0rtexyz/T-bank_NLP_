import logging

from openai import AsyncOpenAI

from tplexity.llm_client.config import settings

logger = logging.getLogger(__name__)


# Singleton для каждого провайдера
_llm_instances: dict[str, "LLMClient"] = {}


class LLMClient:
    """Клиент для работы с LLM через OpenAI-совместимый API"""

    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str | None = None,
        timeout: int = 60,
        **kwargs,
    ):
        """
        Инициализация LLM клиента

        Args:
            model: Название модели
            api_key: API ключ
            base_url: Базовый URL для API (если None, используется стандартный OpenAI API)
            timeout: Таймаут для запросов в секундах
            **kwargs: Дополнительные параметры для AsyncOpenAI (например, default_headers={"x-folder-id": "..."})
        """
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

        logger.info(f"🔄 [llm_client] Инициализация LLM клиента: model={model}, base_url={base_url}")

        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout,
            **kwargs,
        )

        logger.info("✅ [llm_client] LLM клиент инициализирован")

    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Генерация ответа через LLM

        Args:
            messages (list[dict[str, str]]): Список сообщений в формате OpenAI
                Пример: [
                    {"role": "system", "content": "Ты - помощник"},
                    {"role": "user", "content": "Привет!"}
                ]
            temperature (float | None): Температура генерации (если None, используется из settings.llm.temperature)
            max_tokens (int | None): Максимальное количество токенов (если None, используется из settings.llm.max_tokens)

        Returns:
            str: Сгенерированный ответ

        Raises:
            Exception: При ошибке вызова LLM API
        """
        temperature = temperature or settings.temperature
        max_tokens = max_tokens or settings.max_tokens

        logger.info(f"🔄 [llm_client] Отправка запроса к LLM: model={self.model}, base_url={self.base_url}")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            answer = response.choices[0].message.content

            logger.info(f"✅ [llm_client] Ответ получен от LLM (model={self.model})")
            return answer
        except Exception as e:
            logger.error(f"❌ [llm_client] Ошибка при вызове LLM: {e}")
            raise


def get_llm(provider: str) -> LLMClient:
    """
    Получить LLM клиент для указанного провайдера (singleton)

    Args:
        provider (str): Провайдер LLM

    Returns:
        LLMClient: Экземпляр LLM клиента для указанного провайдера
    """
    global _llm_instances

    if provider in _llm_instances:
        return _llm_instances[provider]

    if provider == "qwen":
        client = LLMClient(
            model=settings.qwen_model,
            api_key=settings.qwen_api_key,
            base_url=settings.qwen_base_url,
            timeout=settings.timeout,
        )
    elif provider == "yandexgpt":
        model_name = f"gpt://{settings.yandexgpt_folder_id}/{settings.yandexgpt_model}"
        client = LLMClient(
            model=model_name,
            api_key=settings.yandexgpt_api_key,
            base_url=settings.yandexgpt_base_url,
            timeout=settings.timeout,
            default_headers={"x-folder-id": settings.yandexgpt_folder_id},
        )
    elif provider == "chatgpt":
        client = LLMClient(
            model=settings.chatgpt_model,
            api_key=settings.chatgpt_api_key,
            base_url=None,
            timeout=settings.timeout,
        )
    elif provider == "deepseek":
        client = LLMClient(
            model=settings.deepseek_model,
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            timeout=settings.timeout,
        )
    else:
        raise ValueError(f"Неизвестный провайдер LLM: {provider}")

    _llm_instances[provider] = client
    return client
