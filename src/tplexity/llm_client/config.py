from pydantic import BaseModel, Field


class LLMSettings(BaseModel):
    """Настройки для LLM клиентов (общие и для каждого провайдера)"""

    # Общие настройки генерации (для всех провайдеров)
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Температура генерации по умолчанию (0.0 - детерминированная, 2.0 - креативная)",
    )
    max_tokens: int = Field(
        default=1000,
        ge=1,
        le=4000,
        description="Максимальное количество токенов в ответе по умолчанию",
    )
    timeout: int = Field(
        default=60,
        ge=1,
        description="Таймаут для запросов к LLM в секундах",
    )

    # Qwen настройки
    qwen_model: str = Field(
        default="QuantTrio/Qwen3-VL-30B-A3B-Instruct-AWQ",
        description="Название модели Qwen",
    )
    qwen_api_key: str = Field(
        default="sk-no-key-required",
        description="API ключ для Qwen",
    )
    qwen_base_url: str | None = Field(
        default="http://195.209.210.28:8000/v1",
        description="Базовый URL для Qwen API",
    )

    # YandexGPT настройки
    yandexgpt_model: str = Field(
        default="yandexgpt-lite",
        description="Название модели YandexGPT",
    )
    yandexgpt_api_key: str = Field(
        default="",
        description="API ключ для YandexGPT",
    )
    yandexgpt_folder_id: str = Field(
        default="",
        description="Folder ID для YandexGPT (обязательно для работы)",
    )
    yandexgpt_base_url: str | None = Field(
        default="https://llm.api.cloud.yandex.net/v1",
        description="Базовый URL для YandexGPT API",
    )

    # ChatGPT настройки
    chatgpt_model: str = Field(
        default="gpt-4o-mini",
        description="Название модели ChatGPT",
    )
    chatgpt_api_key: str = Field(
        default="",
        description="API ключ для ChatGPT (OpenAI)",
    )

    # Gemini настройки
    gemini_model: str = Field(
        default="gemini-2.5-flash",
        description="Название модели Gemini",
    )
    gemini_api_key: str = Field(
        default="",
        description="API ключ для Gemini",
    )
    gemini_base_url: str | None = Field(
        default="https://generativelanguage.googleapis.com/v1beta/openai/",
        description="Базовый URL для Gemini API",
    )
