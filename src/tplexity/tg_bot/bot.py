import asyncio
import logging
import re
from datetime import datetime

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
    """Создает клавиатуру с кнопкой 'Очистить историю'."""
    keyboard = [
        [KeyboardButton("🗑️ Очистить историю")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def get_clear_history_confirmation_keyboard():
    """Создает inline клавиатуру для подтверждения очистки истории."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, очистить", callback_data="clear_history_yes"),
            InlineKeyboardButton("❌ Отмена", callback_data="clear_history_no"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def escape_html(text: str) -> str:
    """
    Экранирует HTML символы в тексте для безопасного использования в Telegram HTML.

    Args:
        text: Текст для экранирования

    Returns:
        str: Экранированный текст
    """
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def markdown_to_html(text: str) -> str:
    """
    Преобразует Markdown форматирование в HTML для Telegram.

    Преобразования:
    - **текст** → <b>текст</b> (жирный)
    - *текст* → <i>текст</i> (курсив, если не внутри **)
    - `текст` → <code>текст</code> (код)

    Args:
        text: Текст с Markdown форматированием

    Returns:
        str: Текст с HTML форматированием
    """
    if not text:
        return text

    # Сначала обрабатываем код (обратные кавычки) - самый специфичный формат
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # Затем обрабатываем жирный текст **текст**
    # Используем non-greedy match для корректной обработки нескольких вхождений
    text = re.sub(r"\*\*([^*]+?)\*\*", r"<b>\1</b>", text)

    # Обрабатываем курсив *текст* (только если это не часть **)
    # Проверяем, что перед * нет другого * и после тоже
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", text)

    return text


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


def extract_source_link(source: dict, idx: int) -> tuple[str | None, str | None]:
    """
    Извлекает ссылку и название канала из источника.

    Args:
        source: Словарь с источником (содержит metadata)
        idx: Порядковый номер источника (для логирования)

    Returns:
        tuple[str | None, str | None]: (ссылка, название_канала) или (None, None) если не удалось извлечь
    """
    metadata = source.get("metadata") or {}

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
            logger.debug(
                f"📋 [tg_bot][bot] extract_source_link: источник {idx} сформирован из channel_id и message_id: {link}"
            )
        else:
            # Пробуем старый формат (для обратной совместимости)
            channel_name = metadata.get("channel_name")
            original_id = metadata.get("original_id")
            original_link = metadata.get("original_link")

            if original_link:
                link = original_link
                logger.debug(f"📋 [tg_bot][bot] extract_source_link: источник {idx} использует original_link: {link}")
            elif channel_name and original_id:
                clean_channel = channel_name.lstrip("@")
                link = f"https://t.me/{clean_channel}/{original_id}"
                logger.debug(f"📋 [tg_bot][bot] extract_source_link: источник {idx} сформирован из channel_name: {link}")

    if not link:
        logger.warning(f"⚠️ [tg_bot][bot] Недостаточно данных для источника {idx}: metadata={metadata}")
        return None, None

    # Извлекаем название канала из ссылки
    channel_name = extract_channel_name_from_link(link)
    return link, channel_name


def extract_citation_numbers(text: str) -> set[int]:
    """
    Извлекает все номера цитат из текста.

    Args:
        text: Текст с цитатами в формате [1], [2], [5][6] и т.д.

    Returns:
        set[int]: Множество номеров цитат, найденных в тексте
    """
    pattern = r"\[(\d+)\]"
    matches = re.findall(pattern, text)
    return {int(match) for match in matches}


def build_citation_map(sources: list[dict], cited_numbers: set[int] | None = None) -> dict[int, str]:
    """
    Создает маппинг номеров цитат к ссылкам источников.

    Args:
        sources: Список источников с метаданными
        cited_numbers: Множество номеров источников, на которые есть ссылки в тексте.
                       Если None, создает маппинг для всех источников.

    Returns:
        dict[int, str]: Словарь {номер_источника: ссылка}
    """
    citation_map = {}
    
    # Если указаны конкретные номера, создаем маппинг только для них
    if cited_numbers:
        for idx in cited_numbers:
            # Номера цитат начинаются с 1, индексы в списке - с 0
            source_idx = idx - 1
            if 0 <= source_idx < len(sources):
                source = sources[source_idx]
                link, _ = extract_source_link(source, idx)
                if link:
                    citation_map[idx] = link
    else:
        # Если номера не указаны, создаем маппинг для всех источников
        for idx, source in enumerate(sources, 1):
            link, _ = extract_source_link(source, idx)
            if link:
                citation_map[idx] = link

    return citation_map


def make_citations_clickable(text: str, citation_map: dict[int, str]) -> str:
    """
    Заменяет цитаты [1], [2], [1][3] в тексте на кликабельные HTML ссылки.
    Каждая цитата становится отдельной ссылкой на соответствующий источник.

    Args:
        text: Текст с цитатами
        citation_map: Словарь {номер_источника: ссылка}

    Returns:
        str: Текст с кликабельными HTML ссылками вместо цитат
    """
    if not citation_map:
        return text

    # Паттерн для поиска отдельных цитат: [1], [2], [3] и т.д.
    # Обрабатываем каждую цитату отдельно, чтобы [1][2] стало двумя отдельными ссылками
    pattern = r"\[(\d+)\]"

    def replace_citation(match):
        citation_text = match.group(0)  # [1]
        number = int(match.group(1))  # 1

        # Проверяем, есть ли ссылка для этого номера
        link = citation_map.get(number)

        if link:
            # Экранируем текст цитаты для HTML
            citation_text_escaped = citation_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            # Экранируем ссылку для безопасности
            link_escaped = link.replace("&", "&amp;")
            return f'<a href="{link_escaped}">{citation_text_escaped}</a>'
        else:
            # Если ссылки нет, оставляем как есть
            return citation_text

    return re.sub(pattern, replace_citation, text)


def format_sources(sources: list[dict], cited_numbers: set[int] | None = None) -> str:
    """
    Форматирует источники для красивого отображения в Telegram.

    Args:
        sources: Список источников с метаданными
        cited_numbers: Множество номеров источников, на которые есть ссылки в тексте.
                       Если None, выводит все источники.

    Returns:
        str: Отформатированная строка с источниками в формате HTML
    """
    if not sources:
        logger.warning("⚠️ [tg_bot][bot] format_sources: sources пуст")
        return ""

    # Если указаны конкретные номера, выводим только их
    if cited_numbers:
        # Сортируем номера для правильного порядка вывода
        sorted_numbers = sorted(cited_numbers)
        logger.info(f"📋 [tg_bot][bot] format_sources: обрабатываем {len(sorted_numbers)} источников из {len(sources)} доступных")
    else:
        # Если номера не указаны, выводим все источники
        sorted_numbers = list(range(1, len(sources) + 1))
        logger.info(f"📋 [tg_bot][bot] format_sources: обрабатываем все {len(sources)} источников")

    # Формируем список источников
    source_items = []
    for idx in sorted_numbers:
        # Номера цитат начинаются с 1, индексы в списке - с 0
        source_idx = idx - 1
        if source_idx < 0 or source_idx >= len(sources):
            logger.warning(f"⚠️ [tg_bot][bot] format_sources: источник с номером {idx} не найден (всего источников: {len(sources)})")
            continue

        source = sources[source_idx]
        link, channel_name = extract_source_link(source, idx)
        if not link:
            continue

        # Извлекаем метаданные
        metadata = source.get("metadata") or {}
        
        # Получаем название канала (приоритет: channel_title, затем channel_name)
        channel_title = metadata.get("channel_title") or channel_name
        channel_title_escaped = escape_html(channel_title)
        
        # Извлекаем и форматируем дату
        date_str = None
        date_value = metadata.get("date")
        if date_value:
            try:
                # Обрабатываем ISO формат даты
                if isinstance(date_value, str):
                    # Обрабатываем Z как UTC
                    if date_value.endswith("Z"):
                        date_value = date_value.replace("Z", "+00:00")
                    
                    # Парсим ISO формат
                    if "T" in date_value:
                        post_date = datetime.fromisoformat(date_value)
                    else:
                        # Только дата, добавляем время 00:00:00
                        post_date = datetime.fromisoformat(f"{date_value}T00:00:00")
                    
                    # Форматируем дату в читаемый формат: ДД.ММ.ГГГГ
                    date_str = post_date.strftime("%d.%m.%Y")
                elif isinstance(date_value, datetime):
                    date_str = date_value.strftime("%d.%m.%Y")
            except (ValueError, AttributeError) as e:
                logger.debug(f"⚠️ [tg_bot][bot] format_sources: не удалось распарсить дату для источника {idx}: {date_value}, ошибка: {e}")
        
        # Экранируем ссылку (в основном для символа &)
        link_escaped = link.replace("&", "&amp;")
        
        # Форматируем в формате: [Номер]: Название канала (Дата поста)
        # Название канала - гиперссылка на пост
        if date_str:
            source_items.append(f'[{idx}]: <a href="{link_escaped}">{channel_title_escaped}</a> ({date_str})')
        else:
            source_items.append(f'[{idx}]: <a href="{link_escaped}">{channel_title_escaped}</a>')

    if not source_items:
        logger.warning("⚠️ [tg_bot][bot] format_sources: не удалось сформировать ни одной ссылки")
        return ""

    # Формируем итоговую строку со списком источников
    sources_text = "\n".join(source_items)
    logger.info(f"📋 [tg_bot][bot] format_sources: сформирован текст с {len(source_items)} источниками")
    return sources_text


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    welcome_message = """
🟨 <b>Добро пожаловать в T-Plexity!</b>

<b>Интеллектуальная система для работы с инвестиционными новостями</b>

Я отслеживаю в реальном времени публикации из проверенных инвестиционных Telegram-каналов и даю точные, контекстные ответы на ваши вопросы о рынках и новостях.

<b>⚡ Что я умею:</b>
• Отвечать на вопросы о финансовых рынках и новостях
• Работать на самых актуальных данных (минимальная задержка)
• Показывать источники — каждый ответ с ссылками на конкретные сообщения из каналов
• Давать точные ответы с рыночным контекстом

<b>📝 Как пользоваться:</b>
Просто напишите ваш вопрос о рынках или новостях, и я найду актуальную информацию!

Используйте кнопки меню для управления настройками.
    """
    await update.message.reply_text(welcome_message, reply_markup=get_keyboard(), parse_mode="HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    help_text = """
<b>ℹ️ Справка по использованию T-Plexity</b>

<b>📊 О системе:</b>
T-Plexity — интеллектуальная система, которая в реальном времени отслеживает и агрегирует свежие публикации из проверенных инвестиционных Telegram-каналов. Система работает на самых актуальных данных с минимальной задержкой.

<b>📚 Источники информации:</b>
• Только инвестиционные Telegram-каналы, отобранные по качеству и надежности
• Каждый ответ сопровождается ссылками на первоисточники (конкретные сообщения из каналов)

<b>💡 Как использовать:</b>
Просто напишите вопрос о рынках или новостях — я найду актуальную информацию и дам точный ответ с рыночным контекстом.

<b>⚙️ Доступные команды:</b>
/start — Перезапустить бота
/help — Показать эту справку

<b>🔘 Кнопки меню:</b>
🗑️ Очистить историю — удалить контекст диалога

<b>✨ Особенности:</b>
• Источники отображаются под каждым ответом с прямыми ссылками
• История диалога сохраняется для контекста
• Актуальность данных — минимальная задержка между публикацией и возможностью ответить
    """
    await update.message.reply_text(help_text, reply_markup=get_keyboard(), parse_mode="HTML")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает текстовые сообщения от пользователя."""
    user_message = update.message.text
    logger.info(f"Получено сообщение от {update.effective_user.username}: {user_message}")

    # Если пользователь нажал кнопку "Очистить историю"
    if user_message == "🗑️ Очистить историю" or user_message == "Удалить историю из памяти":
        await update.message.reply_text(
            "⚠️ <b>Вы уверены, что хотите очистить историю диалога?</b>\n\n"
            "Все контекстные данные будут удалены, и диалог начнется заново.",
            reply_markup=get_clear_history_confirmation_keyboard(),
            parse_mode="HTML",
        )
        return


    # Получаем клиент сервиса из контекста приложения
    generation_client: GenerationClient = context.bot_data.get("generation_client")

    if not generation_client:
        await update.message.reply_text(
            "❌ <b>Ошибка:</b> Сервис генерации недоступен.\n\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору.",
            reply_markup=get_keyboard(),
            parse_mode="HTML",
        )
        logger.error("Generation client not found in bot_data")
        return

    # Используем qwen как модель по умолчанию
    selected_model = "qwen"
    logger.info(f"📌 [tg_bot][bot] Использование модели: {selected_model}")

    # Показываем индикатор печати
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Формируем session_id на основе user_id (один чат на пользователя)
        user_id = update.effective_user.id
        session_id = f"tg:{user_id}"

        # Отправляем запрос в Generation API с выбранной моделью и session_id
        answer, _, sources, search_time, generation_time, total_time = await generation_client.send_message(
            user_message, llm_provider=selected_model, session_id=session_id
        )

        # Логируем полученные источники для отладки
        logger.info(f"📋 [tg_bot][bot] Получено источников: {len(sources)}")
        if sources:
            logger.debug(f"📋 [tg_bot][bot] Первый источник: {sources[0] if sources else 'нет'}")

        # Преобразуем Markdown в HTML (если LLM вернул Markdown)
        answer_html = markdown_to_html(answer)

        # Извлекаем все номера цитат из текста ответа
        cited_numbers = extract_citation_numbers(answer_html)
        logger.info(f"📋 [tg_bot][bot] Найдено цитат в тексте: {cited_numbers}")

        # Создаем маппинг цитат для кликабельных ссылок (только для тех, на которые есть ссылки)
        citation_map = build_citation_map(sources, cited_numbers)

        # Делаем цитаты кликабельными в ответе
        answer_with_citations = make_citations_clickable(answer_html, citation_map)

        # Форматируем источники (только те, на которые есть ссылки в тексте)
        sources_text = format_sources(sources, cited_numbers)

        logger.info(
            f"📋 [tg_bot][bot] Отформатированный текст источников: {sources_text[:100] if sources_text else 'пусто'}..."
        )

        # Формируем полный ответ с источниками
        if sources_text:
            response_text = f"{answer_with_citations}\n\n{sources_text}"
        else:
            response_text = answer_with_citations

        # Определяем, использовался ли RAG (если есть sources, значит использовался)
        used_rag = len(sources) > 0

        # Создаем клавиатуру с кнопкой "Краткий ответ" только если использовался RAG
        reply_markup = None
        if used_rag:
            keyboard = [[InlineKeyboardButton("📝 Краткий ответ", callback_data=f"short_answer:{update.message.message_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            # Сохраняем детальный ответ и источники в chat_data для последующего использования
            message_key = f"detailed_answer_{update.message.message_id}"
            context.chat_data[message_key] = {
                "detailed_answer": answer_with_citations,
                "sources_text": sources_text,
                "sources": sources,
                "citation_map": citation_map,
            }

        # Отправляем полный ответ
        sent_message = await update.message.reply_text(
            response_text, disable_web_page_preview=True, parse_mode="HTML", reply_markup=reply_markup
        )
        
        # Сохраняем ID отправленного сообщения для последующего редактирования
        if used_rag:
            context.chat_data[f"sent_message_id_{update.message.message_id}"] = sent_message.message_id

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ <b>Произошла ошибка</b>\n\n"
            f"Не удалось обработать ваше сообщение.\n\n"
            f"<i>Детали: {escape_html(str(e))}</i>\n\n"
            f"Пожалуйста, попробуйте еще раз или обратитесь к администратору.",
            reply_markup=get_keyboard(),
            parse_mode="HTML",
        )


async def short_answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатия на кнопки 'Краткий ответ' и 'Подробный ответ'."""
    query = update.callback_query

    # Отвечаем на callback query
    await query.answer()

    # Парсим callback_data: "short_answer:message_id" или "detailed_answer:message_id"
    if query.data.startswith("short_answer:"):
        # Пользователь хочет краткий ответ
        original_message_id = int(query.data.split(":")[1])
        message_key = f"detailed_answer_{original_message_id}"
        sent_message_key = f"sent_message_id_{original_message_id}"

        # Получаем сохраненные данные
        saved_data = context.chat_data.get(message_key)
        sent_message_id = context.chat_data.get(sent_message_key)

        if not saved_data:
            await query.edit_message_text(
                "❌ <b>Ошибка</b>\n\nНе удалось найти детальный ответ. Попробуйте задать вопрос снова.",
                parse_mode="HTML",
            )
            logger.error(f"Не найдены сохраненные данные для message_id={original_message_id}")
            return

        # Получаем клиент сервиса
        generation_client: GenerationClient = context.bot_data.get("generation_client")
        if not generation_client:
            await query.edit_message_text(
                "❌ <b>Ошибка</b>\n\nСервис генерации недоступен.",
                parse_mode="HTML",
            )
            logger.error("Generation client not found in bot_data")
            return

        # Показываем индикатор печати
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        try:
            # Используем qwen как модель по умолчанию
            selected_model = "qwen"

            # Генерируем краткий ответ
            detailed_answer = saved_data["detailed_answer"]
            short_answer = await generation_client.generate_short_answer(
                detailed_answer=detailed_answer, llm_provider=selected_model
            )

            # Преобразуем Markdown в HTML (если LLM вернул Markdown)
            short_answer_html = markdown_to_html(short_answer)

            # Делаем цитаты кликабельными в кратком ответе
            citation_map = saved_data.get("citation_map", {})
            short_answer_with_citations = make_citations_clickable(short_answer_html, citation_map)

            # Формируем краткий ответ с источниками
            sources_text = saved_data.get("sources_text", "")
            if sources_text:
                response_text = f"{short_answer_with_citations}\n\n{sources_text}"
            else:
                response_text = short_answer_with_citations

            # Создаем кнопку "Подробный ответ"
            keyboard = [[InlineKeyboardButton("📄 Подробный ответ", callback_data=f"detailed_answer:{original_message_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Редактируем сообщение
            if sent_message_id:
                # Редактируем отправленное сообщение
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=sent_message_id,
                    text=response_text,
                    disable_web_page_preview=True,
                    parse_mode="HTML",
                    reply_markup=reply_markup,
                )
            else:
                # Если не нашли ID отправленного сообщения, редактируем сообщение с кнопкой
                await query.edit_message_text(
                    response_text,
                    disable_web_page_preview=True,
                    parse_mode="HTML",
                    reply_markup=reply_markup,
                )

        except Exception as e:
            logger.error(f"Ошибка при генерации краткого ответа: {e}", exc_info=True)
            await query.edit_message_text(
                f"❌ <b>Произошла ошибка</b>\n\nНе удалось сгенерировать краткий ответ.\n\n<i>Детали: {escape_html(str(e))}</i>",
                parse_mode="HTML",
            )

    elif query.data.startswith("detailed_answer:"):
        # Пользователь хочет вернуться к детальному ответу
        original_message_id = int(query.data.split(":")[1])
        message_key = f"detailed_answer_{original_message_id}"
        sent_message_key = f"sent_message_id_{original_message_id}"

        # Получаем сохраненные данные
        saved_data = context.chat_data.get(message_key)
        sent_message_id = context.chat_data.get(sent_message_key)

        if not saved_data:
            await query.edit_message_text(
                "❌ <b>Ошибка</b>\n\nНе удалось найти детальный ответ. Попробуйте задать вопрос снова.",
                parse_mode="HTML",
            )
            logger.error(f"Не найдены сохраненные данные для message_id={original_message_id}")
            return

        # Восстанавливаем детальный ответ
        detailed_answer = saved_data["detailed_answer"]
        sources_text = saved_data.get("sources_text", "")
        if sources_text:
            response_text = f"{detailed_answer}\n\n{sources_text}"
        else:
            response_text = detailed_answer

        # Создаем кнопку "Краткий ответ"
        keyboard = [[InlineKeyboardButton("📝 Краткий ответ", callback_data=f"short_answer:{original_message_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Редактируем сообщение
        if sent_message_id:
            # Редактируем отправленное сообщение
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=sent_message_id,
                text=response_text,
                disable_web_page_preview=True,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
        else:
            # Если не нашли ID отправленного сообщения, редактируем сообщение с кнопкой
            await query.edit_message_text(
                response_text,
                disable_web_page_preview=True,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )


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
                "❌ <b>Ошибка</b>\n\nСервис генерации недоступен. Пожалуйста, попробуйте позже.",
                reply_markup=None,
                parse_mode="HTML",
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
                "✅ <b>История очищена!</b>\n\n" "Все данные диалога удалены. Вы можете начать новый диалог.",
                reply_markup=None,
                parse_mode="HTML",
            )
            logger.info(f"Пользователь {update.effective_user.username} очистил историю диалога")
        except Exception as e:
            logger.error(f"Ошибка при очистке истории: {e}", exc_info=True)
            await query.edit_message_text(
                f"❌ <b>Ошибка при очистке истории</b>\n\n<i>{str(e)}</i>", reply_markup=None, parse_mode="HTML"
            )

    elif query.data == "clear_history_no":
        await query.edit_message_text(
            "✅ <b>Очистка отменена</b>\n\nИстория диалога сохранена.", reply_markup=None, parse_mode="HTML"
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

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Регистрируем обработчик для callback query (нажатие на inline кнопки)
    application.add_handler(CallbackQueryHandler(clear_history_callback, pattern="^clear_history_"))
    application.add_handler(CallbackQueryHandler(short_answer_callback, pattern="^(short_answer|detailed_answer):"))

    # Регистрируем обработчик для всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота
    logger.info("🤖 Бот запущен...")
    try:
        async with application:
            await application.initialize()
            await application.start()

            # Устанавливаем команды меню
            commands = [
                BotCommand("start", "🟨 Запустить бота"),
                BotCommand("help", "ℹ️ Справка"),
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
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Регистрируем обработчик для callback query (нажатие на inline кнопки)
    application.add_handler(CallbackQueryHandler(clear_history_callback, pattern="^clear_history_"))
    application.add_handler(CallbackQueryHandler(short_answer_callback, pattern="^(short_answer|detailed_answer):"))

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
            BotCommand("start", "🟨 Запустить бота"),
            BotCommand("help", "ℹ️ Справка"),
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
