import logging

from fastapi import APIRouter, Depends
from telegram.ext import Application

from tplexity.tg_bot.api.dependencies import get_bot_app

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tg_bot", tags=["tg_bot"])


@router.get("/status")
async def status(
    bot_app: Application = Depends(get_bot_app),
) -> dict:
    """
    Статус бота

    Args:
        bot_app: Экземпляр Telegram Application

    Returns:
        dict: Статус бота
    """
    try:
        bot_info = await bot_app.bot.get_me()
        return {
            "status": "running",
            "bot_username": bot_info.username,
            "bot_id": bot_info.id,
            "bot_name": bot_info.first_name,
        }
    except Exception as e:
        logger.error(f"[tg_bot][routers] Ошибка при получении статуса бота: {e}")
        return {
            "status": "error",
            "error": str(e),
        }
