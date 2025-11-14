import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from tplexity.generation.api import router as generation_router
from tplexity.retriever.api import router as retriever_router

logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Схема для health check"""

    status: str = Field(description="Статус здоровья сервиса")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("🚀 [API] Запуск приложения")
    yield
    logger.info("🛑 [API] Остановка приложения")


app = FastAPI(
    title="T-Plexity API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(retriever_router)
app.include_router(generation_router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """
    Health check эндпоинт

    Returns:
        HealthResponse: Статус сервиса
    """
    return HealthResponse(status="healthy")
