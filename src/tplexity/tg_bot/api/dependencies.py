"""Зависимости для Telegram Bot API"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram.ext import Application

from tplexity.tg_bot.service_client import create_service_client, GenerationClient

logger = logging.getLogger(__name__)

# Загружаем переменные окружения
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

# Singleton для Application
_bot_app_instance: Application | None = None


def get_bot_app() -> Application:
    """
    Получить экземпляр Telegram Application (singleton)
    
    Returns:
        Application: Экземпляр Telegram Application
    """
    global _bot_app_instance
    
    if _bot_app_instance is None:
        bot_token = os.getenv("BOT_TOKEN")
        
        if not bot_token or bot_token == "your_bot_token_here":
            raise ValueError("BOT_TOKEN не установлен в .env файле")
        
        # Создаем клиент Generation API
        try:
            generation_client = create_service_client()
            logger.info("✅ Клиент Generation API создан")
        except ValueError as e:
            logger.error(f"❌ Ошибка создания клиента Generation API: {e}")
            raise ValueError(f"Ошибка создания клиента Generation API: {e}") from e
        
        # Создаем приложение Telegram
        application = Application.builder().token(bot_token).build()
        
        # Сохраняем клиент Generation API в bot_data
        application.bot_data['generation_client'] = generation_client
        
        # Импортируем и регистрируем обработчики
        from tplexity.tg_bot.bot import register_handlers
        
        register_handlers(application)
        
        _bot_app_instance = application
        logger.info("✅ Telegram Bot Application создан")
    
    return _bot_app_instance

