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

    # Gemini настройки
    gemini_model: str = "gemini-2.5-flash"
    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Создаем экземпляр настроек
settings = Settings()
