from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки tg_parse микросервиса из .env файла"""

    # Telegram API credentials
    api_id: int | None = None
    api_hash: str | None = None
    phone: str | None = None
    session_name: str = "my_session"

    # Мониторинг каналов
    channels: str = ""  # Список каналов через запятую
    check_interval: int = 60
    initial_messages_limit: int = 100

    # Webhook настройки
    webhook_url: str | None = None

    # Директория данных
    data_dir: str = "data"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def get_channels_list(self) -> list[str]:
        """Преобразует строку каналов в список"""
        if not self.channels:
            return []
        return [ch.strip() for ch in self.channels.split(",") if ch.strip()]


# Создаем экземпляр настроек
settings = Settings()
