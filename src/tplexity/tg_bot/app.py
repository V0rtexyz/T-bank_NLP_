"""
FastAPI приложение для Telegram Bot микросервиса.
Запускается через uvicorn как отдельный сервис.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from tplexity.tg_bot.api import router as tg_bot_router

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Схема для health check"""

    status: str = Field(description="Статус здоровья сервиса")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    import asyncio

    from tplexity.tg_bot.api.dependencies import get_bot_app
    from tplexity.tg_bot.bot import start_polling

    logger.info("🚀 [Telegram Bot Service] Запуск микросервиса")

    # Инициализируем бота и запускаем polling в фоне
    bot_app = get_bot_app()

    # Запускаем polling в фоновой задаче
    polling_task = asyncio.create_task(start_polling(bot_app))

    yield

    # Останавливаем polling
    logger.info("🛑 [Telegram Bot Service] Остановка микросервиса")
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass

    # Закрываем клиент Generation API
    generation_client = bot_app.bot_data.get("generation_client")
    if generation_client:
        await generation_client.close()
        logger.info("Соединение с Generation API закрыто")


app = FastAPI(
    title="Telegram Bot Service API",
    description="Микросервис для Telegram бота с интеграцией Generation API",
    version="1.0.0",
    lifespan=lifespan,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутер TG бота
app.include_router(tg_bot_router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """
    Health check эндпоинт

    Returns:
        HealthResponse: Статус сервиса
    """
    return HealthResponse(status="healthy")


@app.get("/", tags=["info"])
async def root():
    """Корневой эндпоинт с информацией о сервисе"""
    return {
        "service": "Telegram Bot Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "webhook": "/tg_bot/webhook",
            "docs": "/docs",
            "openapi": "/openapi.json",
        },
    }


if __name__ == "__main__":
    import uvicorn

    # Запуск через uvicorn
    uvicorn.run(
        "tplexity.tg_bot.app:app",
        host="0.0.0.0",
        port=8013,  # Порт для tg_bot (8010=retriever, 8011=tg_parse, 8012=generation)
        reload=True,  # Автоперезагрузка при изменении кода (для разработки)
    )
