"""
Generation микросервис

Микросервис для генерации ответов с использованием RAG (Retrieval-Augmented Generation).
Работает независимо и взаимодействует с Retriever микросервисом для получения контекста.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tplexity.generation.api import router

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения

    Запускается при старте и остановке приложения
    """
    logger.info("🚀 [generation] Запуск Generation микросервиса")
    yield
    logger.info("🛑 [generation] Остановка Generation микросервиса")


# Создание FastAPI приложения
app = FastAPI(
    title="Generation API",
    description="Микросервис для генерации ответов с использованием RAG",
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
        "service": "Generation API",
        "version": "1.0.0",
        "endpoints": {
            "generate": "POST /generation/generate - Генерация ответа с RAG",
            "health": "GET /health - Health check",
            "docs": "GET /docs - Swagger UI",
        },
    }


if __name__ == "__main__":
    import uvicorn

    # Запуск сервера на порту 8002 (отличается от других микросервисов)
    uvicorn.run(
        "tplexity.generation.app:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info",
    )
