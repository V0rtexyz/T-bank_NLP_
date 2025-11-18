"""
Модуль для определения актуальности поста через LLM
"""

import logging
from datetime import datetime, timedelta

from tplexity.llm_client import get_llm

logger = logging.getLogger(__name__)

# Примерные значения актуальности для разных топиков (в днях)
RELEVANCE_EXAMPLES = {
    "новости": 7,
    "макроданные": 30,
    "отчет о доходах": 90,
    "анализ": 60,
    "прогноз": 180,
    "мнение": 14,
}

RELEVANCE_PROMPT = """Ты - эксперт по анализу финансовых новостей и постов. Твоя задача - определить, как долго будет актуальна информация в данном посте.

Примерные значения актуальности для разных типов контента (в днях):
- новости: 7
- макроданные: 30
- отчет о доходах: 90
- анализ: 60
- прогноз: 180
- мнение: 14

ВАЖНО: Эти значения даны только для примерного понимания. Ты должен учитывать контекст самого поста и определить актуальность на основе его содержания. Например:
- Новость о конкретном событии может быть актуальна 3-7 дней
- Макроэкономические данные могут быть актуальны 30-60 дней
- Отчеты о доходах могут быть актуальны 90-180 дней
- Мнение эксперта может быть актуально 7-14 дней

Проанализируй пост и верни ТОЛЬКО число - количество дней актуальности (целое число от 1 до 10000). Не давай никаких пояснений, только число.

Пост:
{post_text}

Количество дней актуальности:"""


async def determine_relevance_days(post_text: str, llm_provider: str = "qwen") -> tuple[int, str]:
    """
    Определяет количество дней актуальности поста через LLM
    
    Args:
        post_text: Текст поста для анализа
        llm_provider: Провайдер LLM (по умолчанию "qwen")
    
    Returns:
        tuple[int, str]: (Количество дней актуальности (от 1 до 10000), сырой ответ LLM)
    """
    try:
        llm_client = get_llm(llm_provider)
        
        messages = [
            {
                "role": "user",
                "content": RELEVANCE_PROMPT.format(post_text=post_text),
            }
        ]
        
        raw_response = await llm_client.generate(
            messages=messages,
            temperature=0.0,
            max_tokens=50,
        )
        
        # Извлекаем число из ответа
        response = raw_response.strip()
        # Удаляем все нецифровые символы, кроме минуса в начале
        digits = ""
        for char in response:
            if char.isdigit():
                digits += char
            elif digits:  # Если уже начали собирать цифры, останавливаемся
                break
        
        if not digits:
            logger.warning(f"⚠️ [relevance_analyzer] Не удалось извлечь число из ответа LLM: {response}, используем значение по умолчанию 30")
            return 30, raw_response
        
        relevance_days = int(digits)
        
        # Ограничиваем диапазон от 1 до 10000
        relevance_days = max(1, min(10000, relevance_days))
        
        logger.info(f"✅ [relevance_analyzer] Определена актуальность: {relevance_days} дней для поста (длина: {len(post_text)} символов)")
        return relevance_days, raw_response
        
    except Exception as e:
        logger.error(f"❌ [relevance_analyzer] Ошибка при определении актуальности: {e}", exc_info=True)
        # В случае ошибки возвращаем значение по умолчанию
        return 30, f"ERROR: {str(e)}"


def calculate_delete_date(relevance_days: int) -> str:
    """
    Вычисляет дату удаления поста (сегодня + relevance_days + 3 дня)
    
    Args:
        relevance_days: Количество дней актуальности
    
    Returns:
        str: Дата удаления в формате ISO (YYYY-MM-DD)
    """
    today = datetime.now()
    delete_date = today + timedelta(days=relevance_days + 3)
    return delete_date.strftime("%Y-%m-%d")

