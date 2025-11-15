from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки Telegram Bot микросервиса из .env файла"""

    # Telegram Bot настройки
    bot_token: str = "your_bot_token_here"

    # Generation API настройки
    generation_api_url: str = "http://localhost:8000"
    generation_api_timeout: float = 60.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Создаем экземпляр настроек
settings = Settings()

