"""
Telegram бот с интеграцией Generation API микросервиса.
Отправляет сообщения пользователя в Generation API (FastAPI) и возвращает ответ.
"""

import asyncio
import logging

from telegram import BotCommand, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

try:
    from .config import settings
    from .service_client import GenerationClient, create_service_client
except ImportError:
    # Для прямого запуска через python bot.py
    from config import settings
    from service_client import GenerationClient, create_service_client

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def get_keyboard():
    """Создает клавиатуру с кнопкой 'Выбор модели'."""
    keyboard = [[KeyboardButton("Выбор модели")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    await update.message.reply_text("start message", reply_markup=get_keyboard())


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает текстовые сообщения от пользователя."""
    user_message = update.message.text
    logger.info(f"Получено сообщение от {update.effective_user.username}: {user_message}")

    # Если пользователь нажал кнопку "Выбор модели"
    if user_message == "Выбор модели":
        await update.message.reply_text("Извините выбор модели пока не работает", reply_markup=get_keyboard())
        return

    # Получаем клиент сервиса из контекста приложения
    generation_client: GenerationClient = context.bot_data.get("generation_client")

    if not generation_client:
        await update.message.reply_text(
            "Ошибка: сервис генерации недоступен. Пожалуйста, попробуйте позже.", reply_markup=get_keyboard()
        )
        logger.error("Generation client not found in bot_data")
        return

    # Показываем индикатор печати
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Отправляем запрос в Generation API
        response_text = await generation_client.send_message(user_message)

        # Отправляем ответ пользователю с клавиатурой
        await update.message.reply_text(response_text, reply_markup=get_keyboard())

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)
        await update.message.reply_text(
            f"Произошла ошибка при обработке вашего сообщения: {str(e)}", reply_markup=get_keyboard()
        )


async def main() -> None:
    """Запуск бота."""
    # Получаем токен из настроек
    bot_token = settings.bot_token

    if not bot_token:
        logger.error("❌ BOT_TOKEN не установлен в .env файле!")
        logger.error("Пожалуйста, установите токен бота в файле .env")
        return

    # Создаем клиент Generation API
    try:
        generation_client = create_service_client()
        logger.info("✅ Клиент Generation API создан")
    except ValueError as e:
        logger.error(f"❌ Ошибка создания клиента Generation API: {e}")
        logger.error("Пожалуйста, установите GENERATION_API_URL в .env файле")
        return
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка при создании клиента Generation API: {e}")
        return

    # Создаем приложение
    application = Application.builder().token(bot_token).build()

    # Сохраняем клиент Generation API в bot_data для доступа из обработчиков
    application.bot_data["generation_client"] = generation_client

    # Регистрируем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Регистрируем обработчик для всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота
    logger.info("🤖 Бот запущен...")
    try:
        async with application:
            await application.initialize()
            await application.start()

            # Очищаем команды меню и устанавливаем только /start
            commands = [
                BotCommand("start", "Запустить бота"),
            ]
            await application.bot.set_my_commands(commands)

            await application.updater.start_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
            # Ожидаем бесконечно, пока бот работает
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Остановка бота...")
                await application.updater.stop()
                await application.stop()
                await application.shutdown()
    finally:
        # Закрываем соединение с Generation API
        await generation_client.close()
        logger.info("Соединение с Generation API закрыто")


def register_handlers(application: Application) -> None:
    """
    Регистрирует обработчики для Telegram бота.
    Используется при запуске через FastAPI.

    Args:
        application: Экземпляр Telegram Application
    """
    # Регистрируем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Регистрируем обработчик для всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info("✅ Обработчики Telegram бота зарегистрированы")


async def start_polling(application: Application) -> None:
    """
    Запускает polling для Telegram бота.
    Используется при запуске через FastAPI.

    Args:
        application: Экземпляр Telegram Application
    """
    try:
        await application.initialize()
        await application.start()

        # Устанавливаем команды меню
        commands = [
            BotCommand("start", "Запустить бота"),
        ]
        await application.bot.set_my_commands(commands)

        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        logger.info("✅ Polling запущен")

        # Ожидаем бесконечно, пока бот работает
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Остановка бота (polling отменен)...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
    except Exception as e:
        logger.error(f"Ошибка в polling: {e}", exc_info=True)
        try:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    asyncio.run(main())
