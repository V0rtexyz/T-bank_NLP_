from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки tg_parse микросервиса из .env файла"""

    # Telegram API credentials
    api_id: int | None = Field(default=None)

    @field_validator("api_id", mode="before")
    @classmethod
    def parse_api_id(cls, v):
        # Обрабатываем пустые строки и None
        if v == "" or v is None:
            return None
        # Преобразуем строку в int
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return None
        # Если уже int, возвращаем как есть
        if isinstance(v, int):
            return v
        return None

    api_hash: str | None = None
    phone: str | None = None
    session_name: str = "my_session"
    session_string: str | None = None  # Строка сессии (если указана, используется вместо файла)

    @field_validator("session_string", mode="before")
    @classmethod
    def parse_session_string(cls, v):
        # Обрабатываем пустые строки как None
        if v == "" or v is None:
            return None
        return v

    # Мониторинг каналов
    channels: str = "omyinvestments,alfa_investments,tb_invest_official,SberInvestments,centralbank_russia,selfinvestor"  # Список каналов через запятую
    retry_interval: int = 60  # Интервал повторных попыток отправки неудачных постов (в секундах)

    # Webhook настройки
    webhook_url: str | None = None

    # Директория данных
    data_dir: str = "data"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
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
