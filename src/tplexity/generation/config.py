from typing import Literal

from pydantic import BaseModel, Field


class GenerationSettings(BaseModel):
    """Настройки для generation микросервиса"""

    # LLM провайдер (для выбора из settings.llm)
    llm_provider: Literal["qwen", "yandexgpt", "chatgpt", "gemini"] = Field(
        default="chatgpt",
        description="Провайдер LLM: 'qwen', 'yandexgpt', 'chatgpt', 'gemini'",
    )
