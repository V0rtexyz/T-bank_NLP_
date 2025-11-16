"""
Telegram бот с интеграцией Generation API микросервиса.
Отправляет сообщения пользователя в Generation API (FastAPI) и возвращает ответ.
"""

import asyncio
import logging

from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

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
    """Создает клавиатуру с кнопками 'Выбор модели' и 'Удалить историю из памяти'."""
    keyboard = [
        [KeyboardButton("Выбор модели")],
        [KeyboardButton("Удалить историю из памяти")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_models_keyboard():
    """Создает inline клавиатуру с доступными моделями."""
    available_models = settings.available_models
    keyboard = []
    
    # Маппинг названий моделей для отображения
    model_names = {
        "qwen": "Qwen",
        "yandexgpt": "YandexGPT",
        "chatgpt": "ChatGPT",
        "gemini": "Gemini",
    }
    
    # Создаем кнопки для каждой модели
    for model in available_models:
        display_name = model_names.get(model, model.capitalize())
        keyboard.append([InlineKeyboardButton(display_name, callback_data=f"model_{model}")])
    
    return InlineKeyboardMarkup(keyboard)


def get_clear_history_confirmation_keyboard():
    """Создает inline клавиатуру для подтверждения очистки истории."""
    keyboard = [
        [
            InlineKeyboardButton("Да", callback_data="clear_history_yes"),
            InlineKeyboardButton("Нет", callback_data="clear_history_no"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def extract_channel_name_from_link(link: str) -> str:
    """
    Извлекает название канала из Telegram ссылки.
    
    Args:
        link: Telegram ссылка (например, https://t.me/selfinvestor/23422)
    
    Returns:
        str: Название канала (например, selfinvestor)
    """
    import re
    
    # Паттерн для обычного формата: https://t.me/channel_name/message_id
    # Извлекаем название канала между t.me/ и следующим /
    match = re.search(r"https?://t\.me/([^/]+)", link)
    if match:
        channel_name = match.group(1)
        # Убираем @ если есть
        return channel_name.lstrip("@")
    
    # Если не удалось извлечь через regex, пробуем через split
    parts = link.rstrip("/").split("/")
    if len(parts) >= 4:
        # Формат: https://t.me/channel_name/message_id
        # parts = ['https:', '', 't.me', 'channel_name', 'message_id']
        channel_name = parts[-2]  # Предпоследняя часть (название канала)
        return channel_name.lstrip("@")
    
    return "канал"  # Fallback


def format_sources(sources: list[dict], max_sources: int = 5) -> str:
    """
    Форматирует источники как Telegram ссылки с названием канала вместо полной ссылки.

    Args:
        sources: Список источников с метаданными
        max_sources: Максимальное количество источников для отображения

    Returns:
        str: Отформатированная строка с источниками в формате markdown
    """
    if not sources:
        logger.warning("⚠️ [tg_bot] format_sources: sources пуст")
        return ""

    # Берем топ-N источников
    top_sources = sources[:max_sources]
    logger.info(f"📋 [tg_bot] format_sources: обрабатываем {len(top_sources)} источников")

    # Формируем список ссылок
    source_links = []
    for idx, source in enumerate(top_sources, 1):
        logger.debug(f"📋 [tg_bot] format_sources: источник {idx}: {source}")
        
        # Источник может быть словарем с полями "doc_id" и "metadata"
        metadata = source.get("metadata") or {}
        
        # Логируем метаданные для отладки
        if idx == 1:
            logger.info(f"📋 [tg_bot] format_sources: метаданные первого источника: {metadata}")
        
        # Извлекаем ссылку из метаданных (приоритет 1: готовая ссылка)
        link = metadata.get("link")
        
        # Если нет готовой ссылки, пытаемся сформировать из channel_id и message_id
        if not link:
            channel_id = metadata.get("channel_id")
            message_id = metadata.get("message_id")
            
            if channel_id and message_id:
                # Формируем ссылку: https://t.me/c/{channel_id}/{message_id}
                # Для приватных каналов используется формат с channel_id
                link = f"https://t.me/c/{channel_id}/{message_id}"
                logger.debug(f"📋 [tg_bot] format_sources: источник {idx} сформирован из channel_id и message_id: {link}")
            else:
                # Пробуем старый формат (для обратной совместимости)
                channel_name = metadata.get("channel_name")
                original_id = metadata.get("original_id")
                original_link = metadata.get("original_link")
                
                if original_link:
                    link = original_link
                    logger.debug(f"📋 [tg_bot] format_sources: источник {idx} использует original_link: {link}")
                elif channel_name and original_id:
                    clean_channel = channel_name.lstrip("@")
                    link = f"https://t.me/{clean_channel}/{original_id}"
                    logger.debug(f"📋 [tg_bot] format_sources: источник {idx} сформирован из channel_name: {link}")
        
        if not link:
            # Если не удалось получить ссылку, пропускаем
            logger.warning(f"⚠️ [tg_bot] Недостаточно данных для источника {idx}: metadata={metadata}")
            continue

        # Извлекаем название канала из ссылки
        channel_name = extract_channel_name_from_link(link)
        
        # Форматируем как кликабельную ссылку в Telegram markdown: [текст](ссылка)
        # Экранируем специальные символы в ссылке для markdown
        escaped_link = link.replace("(", "\\(").replace(")", "\\)")
        source_links.append(f"топ-{idx} источник: [{channel_name}]({escaped_link})")

    if not source_links:
        logger.warning("⚠️ [tg_bot] format_sources: не удалось сформировать ни одной ссылки")
        return ""

    # Формируем итоговую строку
    sources_text = "Источники:\n" + "\n".join(source_links)
    logger.info(f"📋 [tg_bot] format_sources: сформирован текст с {len(source_links)} источниками")
    return sources_text


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    await update.message.reply_text("start message", reply_markup=get_keyboard())


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает текстовые сообщения от пользователя."""
    user_message = update.message.text
    logger.info(f"Получено сообщение от {update.effective_user.username}: {user_message}")

    # Если пользователь нажал кнопку "Выбор модели"
    if user_message == "Выбор модели":
        # Получаем текущую выбранную модель
        user_data = context.user_data
        current_model = user_data.get("selected_model")
        
        message_text = "Выберите модель для генерации ответов:"
        if current_model:
            model_names = {
                "qwen": "Qwen",
                "yandexgpt": "YandexGPT",
                "chatgpt": "ChatGPT",
                "gemini": "Gemini",
            }
            current_name = model_names.get(current_model, current_model.capitalize())
            message_text += f"\n\nТекущая модель: {current_name}"
        
        await update.message.reply_text(message_text, reply_markup=get_models_keyboard())
        return

    # Если пользователь нажал кнопку "Удалить историю из памяти"
    if user_message == "Удалить историю из памяти":
        await update.message.reply_text(
            "Вы уверены что хотите сбросить память?",
            reply_markup=get_clear_history_confirmation_keyboard(),
        )
        return

    # Получаем клиент сервиса из контекста приложения
    generation_client: GenerationClient = context.bot_data.get("generation_client")

    if not generation_client:
        await update.message.reply_text(
            "Ошибка: сервис генерации недоступен. Пожалуйста, попробуйте позже.", reply_markup=get_keyboard()
        )
        logger.error("Generation client not found in bot_data")
        return

    # Получаем выбранную модель из user_data
    user_data = context.user_data
    selected_model = user_data.get("selected_model")
    
    # Логируем выбранную модель
    if selected_model:
        logger.info(f"📌 [tg_bot] Использование выбранной модели: {selected_model}")
    else:
        logger.info("📌 [tg_bot] Модель не выбрана, будет использована модель по умолчанию из generation config")

    # Показываем индикатор печати
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Формируем session_id на основе user_id (один чат на пользователя)
        user_id = update.effective_user.id
        session_id = f"tg:{user_id}"

        # Отправляем запрос в Generation API с выбранной моделью и session_id
        answer, sources = await generation_client.send_message(
            user_message, llm_provider=selected_model, session_id=session_id
        )

        # Логируем полученные источники для отладки
        logger.info(f"📋 [tg_bot] Получено источников: {len(sources)}")
        if sources:
            logger.debug(f"📋 [tg_bot] Первый источник: {sources[0] if sources else 'нет'}")

        # Форматируем источники
        sources_text = format_sources(sources, max_sources=5)
        
        logger.info(f"📋 [tg_bot] Отформатированный текст источников: {sources_text[:100] if sources_text else 'пусто'}...")

        # Объединяем ответ и источники
        if sources_text:
            response_text = f"{answer}\n\n{sources_text}"
            # Используем Markdown для форматирования ссылок и отключаем предпросмотр
            await update.message.reply_text(
                response_text, 
                reply_markup=get_keyboard(),
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        else:
            response_text = answer
            logger.warning("⚠️ [tg_bot] Источники не были добавлены к ответу")
            # Отправляем ответ без markdown, если нет источников
            await update.message.reply_text(response_text, reply_markup=get_keyboard())

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)
        await update.message.reply_text(
            f"Произошла ошибка при обработке вашего сообщения: {str(e)}", reply_markup=get_keyboard()
        )


async def model_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик выбора модели через inline кнопки."""
    query = update.callback_query
    
    # Отвечаем на callback query, чтобы убрать индикатор загрузки
    await query.answer()
    
    # Извлекаем название модели из callback_data (формат: "model_qwen")
    if query.data and query.data.startswith("model_"):
        model = query.data.replace("model_", "")
        
        # Сохраняем выбранную модель в user_data
        context.user_data["selected_model"] = model
        
        # Маппинг названий моделей для отображения
        model_names = {
            "qwen": "Qwen",
            "yandexgpt": "YandexGPT",
            "chatgpt": "ChatGPT",
            "gemini": "Gemini",
        }
        
        display_name = model_names.get(model, model.capitalize())
        await query.edit_message_text(
            f"✅ Модель {display_name} выбрана и будет использоваться для генерации ответов.",
            reply_markup=None
        )
        logger.info(f"Пользователь {update.effective_user.username} выбрал модель: {model}")
    else:
        await query.edit_message_text("Ошибка при выборе модели.", reply_markup=None)


async def clear_history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик подтверждения очистки истории через inline кнопки."""
    query = update.callback_query
    
    # Отвечаем на callback query
    await query.answer()
    
    if query.data == "clear_history_yes":
        # Получаем клиент сервиса из контекста приложения
        generation_client: GenerationClient = context.bot_data.get("generation_client")
        
        if not generation_client:
            await query.edit_message_text(
                "Ошибка: сервис генерации недоступен. Пожалуйста, попробуйте позже.",
                reply_markup=None
            )
            logger.error("Generation client not found in bot_data")
            return
        
        # Формируем session_id
        user_id = update.effective_user.id
        session_id = f"tg:{user_id}"
        
        try:
            # Очищаем историю
            await generation_client.clear_session(session_id)
            await query.edit_message_text(
                "✅ История диалога успешно очищена.",
                reply_markup=None
            )
            logger.info(f"Пользователь {update.effective_user.username} очистил историю диалога")
        except Exception as e:
            logger.error(f"Ошибка при очистке истории: {e}", exc_info=True)
            await query.edit_message_text(
                f"Произошла ошибка при очистке истории: {str(e)}",
                reply_markup=None
            )
    
    elif query.data == "clear_history_no":
        await query.edit_message_text(
            "Очистка истории отменена.",
            reply_markup=None
        )
        logger.info(f"Пользователь {update.effective_user.username} отменил очистку истории")


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

    # Регистрируем обработчик для callback query (нажатие на inline кнопки)
    application.add_handler(CallbackQueryHandler(model_callback, pattern="^model_"))
    application.add_handler(CallbackQueryHandler(clear_history_callback, pattern="^clear_history_"))

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

    # Регистрируем обработчик для callback query (нажатие на inline кнопки)
    application.add_handler(CallbackQueryHandler(model_callback, pattern="^model_"))
    application.add_handler(CallbackQueryHandler(clear_history_callback, pattern="^clear_history_"))

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
