from pydantic_settings import BaseSettings, SettingsConfigDict

from tplexity.retriever.config import RetrieverSettings


class Settings(BaseSettings):
    """Глобальные настройки приложения, объединяющие настройки всех микросервисов"""

    retriever: RetrieverSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
