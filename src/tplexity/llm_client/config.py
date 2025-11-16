from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки LLM клиента из .env файла"""

    # Общие настройки генерации (для всех провайдеров)
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: int = 60

    # Qwen настройки
    qwen_model: str = "QuantTrio/Qwen3-VL-30B-A3B-Instruct-AWQ"
    qwen_api_key: str = "sk-no-key-required"
    qwen_base_url: str = "http://195.209.210.28:8000/v1"

    # YandexGPT настройки
    yandexgpt_model: str = "yandexgpt-lite"
    yandexgpt_api_key: str = ""
    yandexgpt_folder_id: str = ""
    yandexgpt_base_url: str = "https://llm.api.cloud.yandex.net/v1"

    # ChatGPT настройки
    chatgpt_model: str = "gpt-4o-mini"
    chatgpt_api_key: str = ""

    # DeepSeek настройки
    deepseek_model: str = "deepseek-chat"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"

    # Список доступных моделей для выбора
    # Если не указано в .env, по умолчанию используется только qwen
    available_models: str = "qwen"

    @field_validator("available_models", mode="after")
    @classmethod
    def parse_available_models(cls, v: str) -> list[str]:
        """Парсит строку с моделями в список"""
        if not v or not v.strip():
            return ["qwen"]  # По умолчанию только qwen
        # Парсим список моделей из .env без ограничений
        models = [m.strip().lower() for m in v.split(",") if m.strip()]
        return models if models else ["qwen"]  # Если список пустой, возвращаем qwen

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Создаем экземпляр настроек
settings = Settings()
