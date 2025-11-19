"""
Модуль для разбиения постов из Telegram на тематические чанки.
Использует LangChain RecursiveCharacterTextSplitter для умного разбиения текста.
"""

import json
import re
from pathlib import Path
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter


class PostChunker:
    """
    Класс для разбиения постов на тематические чанки с использованием LangChain.
    """

    # Основные маркеры, которые обычно разделяют разные новости
    MAIN_SEPARATORS = [
        "\n\n🔹 ",  # Основной маркер для новостей
        "\n\n🟢 ",  # Альтернативный маркер
        "\n\n🔴 ",  # Альтернативный маркер
        "\n\n",  # Двойной перенос строки
    ]

    def __init__(self, source_name: str = None, chunk_size: int = 1000, chunk_overlap: int = 100):
        """
        Инициализация чанкера.

        Args:
            source_name: Название источника (для специфичной настройки)
            chunk_size: Максимальный размер чанка в символах
            chunk_overlap: Перекрытие между чанками
        """
        self.source_name = source_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Создаем text_splitter с настроенными разделителями
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=self.MAIN_SEPARATORS + ["\n", " ", ""],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def chunk_post(self, post: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Разбивает пост на тематические чанки.

        Args:
            post: Словарь с данными поста

        Returns:
            Список чанков с метаданными
        """
        text = post.get("text", "").strip()

        # Если текст пустой или очень короткий, пропускаем
        if not text or len(text) < 50:
            return []

        # Предобработка текста
        cleaned_text = self._preprocess_text(text)

        # Проверяем, нужно ли разбивать пост
        if self._is_single_topic(cleaned_text):
            # Пост об одной теме - не разбиваем
            chunks_texts = [cleaned_text]
        else:
            # Разбиваем с помощью LangChain
            chunks_texts = self.text_splitter.split_text(cleaned_text)

        # Добавляем метаданные к каждому чанку
        result = []
        chunk_idx = 0

        for chunk_text in chunks_texts:
            chunk_text = chunk_text.strip()

            # Фильтруем слишком короткие чанки
            if len(chunk_text) < 50:
                continue

            # Пост-обработка чанка
            chunk_text = self._postprocess_chunk(chunk_text)

            if len(chunk_text) < 50:
                continue

            chunk = {
                "original_id": post.get("id"),
                "original_link": post.get("link"),
                "original_date": post.get("date"),
                "chunk_index": chunk_idx,
                "chunk_text": chunk_text,
                "chunk_length": len(chunk_text),
                "views": post.get("views"),
                "forwards": post.get("forwards"),
                "has_media": post.get("has_media"),
                "media_type": post.get("media_type"),
            }
            result.append(chunk)
            chunk_idx += 1

        return result

    def _preprocess_text(self, text: str) -> str:
        """Предобработка текста перед разбиением."""
        # Убираем заголовки типа "Доброе утро", "Итоги дня"
        headers = [
            r"\*\*⏰\*\*\*\* Доброе утро:.*?\*\*\n*",
            r"\*\*Доброе утро:.*?\*\*\n*",
            r"🏁\*\* Итоги дня:.*?\*\*\n*",
            r"\*\*💡\*\*\*\*.*?\*\*\n*",
            r"\*\*☕\*\*\*\* Мысли с утра.*?\n*",
        ]

        for pattern in headers:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        # Нормализуем переносы строк
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def _postprocess_chunk(self, chunk: str) -> str:
        """Пост-обработка чанка после разбиения."""
        # Убираем хештеги в конце
        chunk = re.sub(r"\n*#\w+\s*$", "", chunk)

        # Убираем тикеры акций в конце
        chunk = re.sub(r"\n*\$[A-Z]+(?:\s+\$[A-Z]+)*\s*$", "", chunk)

        # Убираем упоминания каналов в конце
        chunk = re.sub(r"\n*@\w+\s*$", "", chunk)

        # Убираем лишние пробелы и переносы
        chunk = re.sub(r"\n{3,}", "\n\n", chunk)
        chunk = re.sub(r" {2,}", " ", chunk)

        return chunk.strip()

    def _is_single_topic(self, text: str) -> bool:
        """
        Определяет, является ли пост одной темой с деталями.

        Returns:
            True если это одна тема, False если дайджест
        """
        # Подсчитываем основные маркеры
        main_markers = ["🔹", "🟢", "🔴"]
        nested_markers = ["🟡", "🔵", "⚪️", "•", "▪️"]

        main_count = sum(text.count(marker) for marker in main_markers)
        nested_count = sum(text.count(marker) for marker in nested_markers)

        # Если только вложенные маркеры (2-8) и есть вводный текст
        if nested_count > 0 and main_count == 0:
            marker_positions = [text.find(m) for m in nested_markers if m in text]
            first_marker_pos = min(marker_positions) if marker_positions else -1

            # Если есть вводный текст перед маркерами
            if 2 <= nested_count <= 8 and first_marker_pos > 50 and len(text) < 2500:
                return True

        # Если один основной маркер и есть вложенные - это одна тема
        if main_count == 1 and nested_count > 0:
            return True

        # Если текст короткий и нет основных маркеров - одна тема
        if len(text) < 800 and main_count == 0:
            return True

        return False


def process_channel(channel_path: Path, output_path: Path = None):
    """
    Обрабатывает канал и создает файл с чанками.

    Args:
        channel_path: Путь к папке канала
        output_path: Путь для сохранения файла с чанками (опционально)
    """
    source_name = channel_path.name
    messages_file = channel_path / "messages_monitor.json"

    if not messages_file.exists():
        print(f"Файл {messages_file} не найден")
        return

    # Загружаем посты
    with open(messages_file, encoding="utf-8") as f:
        posts = json.load(f)

    print(f"\nОбработка {source_name}: {len(posts)} постов")

    # Создаем чанкер
    chunker = PostChunker(source_name=source_name)

    # Обрабатываем каждый пост
    all_chunks = []
    total_posts_with_chunks = 0

    for post in posts:
        chunks = chunker.chunk_post(post)
        if chunks:
            all_chunks.extend(chunks)
            total_posts_with_chunks += 1

    print(f"  Постов с текстом: {total_posts_with_chunks}")
    print(f"  Всего чанков: {len(all_chunks)}")

    if all_chunks:
        avg_chunks_per_post = len(all_chunks) / total_posts_with_chunks
        print(f"  Среднее чанков на пост: {avg_chunks_per_post:.2f}")

    # Сохраняем результат
    if output_path is None:
        output_path = channel_path / "messages_chunked.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"  Сохранено в {output_path}")

    return all_chunks


def process_all_channels(data_dir: Path):
    """
    Обрабатывает все каналы в директории data/telegram.

    Args:
        data_dir: Путь к директории data
    """
    telegram_dir = data_dir / "telegram"

    if not telegram_dir.exists():
        print(f"Директория {telegram_dir} не найдена")
        return

    # Получаем все поддиректории
    channels = [d for d in telegram_dir.iterdir() if d.is_dir()]

    print(f"Найдено каналов: {len(channels)}")
    print("=" * 60)

    # Обрабатываем каждый канал
    for channel_path in channels:
        try:
            process_channel(channel_path)
        except Exception as e:
            print(f"Ошибка при обработке {channel_path.name}: {e}")

    print("\n" + "=" * 60)
    print("Обработка завершена!")


if __name__ == "__main__":
    # Определяем путь к данным
    data_dir = Path(__file__).parent.parent.parent.parent / "data"

    print("Запуск чанкирования постов с использованием LangChain...")
    print(f"Директория с данными: {data_dir}")

    process_all_channels(data_dir)
