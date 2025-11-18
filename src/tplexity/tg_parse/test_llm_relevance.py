"""
Скрипт для тестирования LLM на определении актуальности постов

Использование:
    poetry run python src/tplexity/tg_parse/test_llm_relevance.py
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tplexity.tg_parse.config import Settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def test_llm_on_posts():
    """Тестирует LLM на определении актуальности постов"""
    logger.info("=" * 80)
    logger.info("🧪 [test_llm_relevance] Начало тестирования LLM на постах")
    logger.info("=" * 80)

    # Загружаем конфигурацию
    config = Settings()
    
    # Определяем путь к данным
    data_dir = project_root / config.data_dir
    telegram_dir = data_dir / "telegram"
    
    logger.info(f"📁 [test_llm_relevance] Поиск файлов с постами в: {telegram_dir}")
    
    # Ищем все файлы messages_monitor.json
    messages_files = list(telegram_dir.glob("*/messages_monitor.json"))
    
    if not messages_files:
        logger.error(f"❌ [test_llm_relevance] Не найдено файлов messages_monitor.json в {telegram_dir}")
        logger.error("   Убедитесь, что посты были скачаны через tg_parse")
        return False
    
    logger.info(f"✅ [test_llm_relevance] Найдено {len(messages_files)} файлов с постами")
    
    # Получаем список активных каналов из конфига
    active_channels = config.get_channels_list()
    logger.info(f"📋 [test_llm_relevance] Активные каналы из конфига: {active_channels}")
    
    # Собираем посты только из активных каналов, группируя по каналам
    posts_by_channel = {}
    for messages_file in messages_files:
        channel_name = messages_file.parent.name
        
        # Фильтруем только активные каналы
        if active_channels and channel_name not in active_channels:
            logger.debug(f"   Пропущен канал {channel_name} (не в списке активных)")
            continue
        
        try:
            with open(messages_file, encoding="utf-8") as f:
                posts = json.load(f)
                for post in posts:
                    post["source_channel"] = channel_name
                    post["source_file"] = str(messages_file)
                posts_by_channel[channel_name] = posts
                logger.info(f"   Загружено {len(posts)} постов из {channel_name}")
        except Exception as e:
            logger.error(f"❌ [test_llm_relevance] Ошибка при загрузке {messages_file}: {e}")
    
    if not posts_by_channel:
        logger.error("❌ [test_llm_relevance] Не найдено постов из активных каналов для тестирования")
        logger.error("   Проверьте, что в конфиге указаны правильные каналы и что для них есть файлы messages_monitor.json")
        return False
    
    # Сортируем каналы по имени для стабильности
    sorted_channels = sorted(posts_by_channel.keys())
    logger.info(f"📊 [test_llm_relevance] Найдено активных каналов с постами: {len(sorted_channels)}")
    for i, channel in enumerate(sorted_channels, 1):
        logger.info(f"   {i}. {channel}: {len(posts_by_channel[channel])} постов")
    
    # Берем посты из второго канала
    if len(sorted_channels) < 2:
        logger.warning(f"⚠️ [test_llm_relevance] Найдено только {len(sorted_channels)} активных каналов, будет использован первый канал")
        selected_channel = sorted_channels[0]
    else:
        selected_channel = sorted_channels[1]  # Второй канал (индекс 1)
    
    logger.info(f"📝 [test_llm_relevance] Выбран канал: {selected_channel}")
    
    # Берем первые 5 постов с текстом из выбранного канала
    posts_with_text = [
        post for post in posts_by_channel[selected_channel]
        if post.get("text") and post.get("text").strip()
    ]
    
    if len(posts_with_text) < 5:
        logger.warning(f"⚠️ [test_llm_relevance] В канале {selected_channel} найдено только {len(posts_with_text)} постов с текстом, будет использовано {len(posts_with_text)}")
        selected_posts = posts_with_text
    else:
        selected_posts = posts_with_text[:5]
    
    logger.info(f"📝 [test_llm_relevance] Выбрано {len(selected_posts)} постов для тестирования")
    
    # Результаты
    results = []
    
    # Прогоняем каждый пост через LLM
    for i, post in enumerate(selected_posts, 1):
        post_text = post.get("text", "").strip()
        post_id = post.get("id", f"unknown_{i}")
        channel = post.get("source_channel", "unknown")
        
        logger.info("=" * 80)
        logger.info(f"📊 [test_llm_relevance] Пост {i}/{len(selected_posts)}")
        logger.info(f"   ID: {post_id}")
        logger.info(f"   Канал: {channel}")
        logger.info(f"   Длина текста: {len(post_text)} символов")
        logger.info(f"   Текст (первые 200 символов): {post_text[:200]}...")
        logger.info("=" * 80)
        
        try:
            # Получаем полный ответ LLM напрямую
            from tplexity.llm_client import get_llm
            from tplexity.tg_parse.relevance_analyzer import RELEVANCE_PROMPT
            
            llm_client = get_llm(config.llm_provider)
            messages = [
                {
                    "role": "user",
                    "content": RELEVANCE_PROMPT.format(post_text=post_text),
                }
            ]
            
            raw_llm_response = await llm_client.generate(
                messages=messages,
                temperature=0.0,
                max_tokens=50,
            )
            
            result = {
                "post_number": i,
                "post_id": post_id,
                "channel": channel,
                "post_text": post_text,
                "llm_response": raw_llm_response.strip(),
            }
            
            results.append(result)
            
            logger.info(f"✅ [test_llm_relevance] Пост {i} обработан:")
            logger.info(f"   Ответ LLM: {raw_llm_response.strip()}")
            
        except Exception as e:
            logger.error(f"❌ [test_llm_relevance] Ошибка при обработке поста {i}: {e}", exc_info=True)
            result = {
                "post_number": i,
                "post_id": post_id,
                "channel": channel,
                "post_text": post_text,
                "llm_response": f"ERROR: {str(e)}",
                "relevance_days": None,
            }
            results.append(result)
    
    # Сохраняем результаты в JSON файл
    output_file = project_root / "llm_relevance_test_results.json"
    
    logger.info("=" * 80)
    logger.info(f"💾 [test_llm_relevance] Сохранение результатов в {output_file}")
    logger.info("=" * 80)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ [test_llm_relevance] Результаты сохранены в {output_file}")
    logger.info(f"   Обработано постов: {len(results)}")
    
    # Выводим краткую статистику
    successful = [r for r in results if r.get("llm_response") and not r.get("llm_response", "").startswith("ERROR")]
    logger.info(f"   Успешно обработано: {len(successful)}")
    logger.info(f"   Ошибок: {len(results) - len(successful)}")
    
    logger.info("=" * 80)
    logger.info("✅ [test_llm_relevance] ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    logger.info("=" * 80)
    
    return True


async def main():
    """Главная функция"""
    success = await test_llm_on_posts()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

