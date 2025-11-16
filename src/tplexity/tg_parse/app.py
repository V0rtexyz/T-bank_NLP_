"""
Telegram Parser микросервис

Микросервис для мониторинга Telegram каналов, чанкирования постов и отправки данных.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tplexity.tg_parse.api import router

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения

    Запускается при старте и остановке приложения
    """
    logger.info("🚀 [tg_parse] Запуск Telegram Parser микросервиса")
    yield
    logger.info("🛑 [tg_parse] Остановка Telegram Parser микросервиса")


# Создание FastAPI приложения
app = FastAPI(
    title="Telegram Parser API",
    description="Микросервис для мониторинга Telegram каналов и чанкирования постов",
    version="1.0.0",
    lifespan=lifespan,
)

# Добавление CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check эндпоинт"""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Информация о сервисе"""
    return {
        "service": "Telegram Parser API",
        "version": "1.0.0",
        "endpoints": {
            "download": "POST /download - Скачать последние n сообщений из каналов",
            "start": "POST /start - Запустить мониторинг",
            "stop": "POST /stop - Остановить мониторинг",
            "status": "GET /status - Статус сервиса",
            "health": "GET /health - Health check",
            "docs": "GET /docs - Swagger UI",
        },
    }


if __name__ == "__main__":
    import uvicorn

    # Запуск сервера на порту 8011
    uvicorn.run(
        "tplexity.tg_parse.app:app",
        host="0.0.0.0",
        port=8011,
        reload=True,
        log_level="info",
    )
