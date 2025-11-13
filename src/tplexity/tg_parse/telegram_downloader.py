"""
Модуль для скачивания данных из Telegram каналов через API.

Использует Telethon для работы с Telegram API.
Позволяет скачивать сообщения, медиа и метаданные из публичных и приватных каналов.
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

import pandas as pd
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import Message


class TelegramDownloader:
    """Класс для скачивания данных из Telegram каналов."""
    
    @staticmethod
    def parse_channel_link(link: str) -> str:
        """
        Извлекает username канала из ссылки или возвращает как есть.
        
        Args:
            link: Ссылка на канал (t.me/channel, @channel или просто channel)
            
        Returns:
            Username канала без @
        """
        # Убираем пробелы
        link = link.strip()
        
        # Если это ссылка t.me/...
        if 't.me/' in link or 'telegram.me/' in link:
            # Извлекаем последнюю часть после /
            parts = link.rstrip('/').split('/')
            return parts[-1].lstrip('@')
        
        # Если начинается с @
        if link.startswith('@'):
            return link[1:]
        
        # Иначе возвращаем как есть
        return link

    def __init__(
        self,
        api_id: int,
        api_hash: str,
        session_name: str = "telegram_session",
        session_string: Optional[str] = None,
        download_path: str = "data/telegram"
    ):
        """
        Инициализация клиента Telegram.

        Args:
            api_id: ID приложения из https://my.telegram.org
            api_hash: Hash приложения из https://my.telegram.org
            session_name: Имя файла сессии (используется если session_string не указан)
            session_string: Строка сессии (если указана, используется вместо файла)
            download_path: Путь для сохранения данных
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.session_string = session_string
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        
        # Используем StringSession если передана строка, иначе файловую сессию
        if session_string:
            session = StringSession(session_string)
        else:
            session = session_name
        
        self.client = TelegramClient(session, api_id, api_hash)

    async def connect(self, max_retries: int = 3):
        """
        Подключение к Telegram с повторными попытками.
        
        Args:
            max_retries: Максимальное количество попыток подключения
        """
        for attempt in range(max_retries):
            try:
                await self.client.connect()
                if not await self.client.is_user_authorized():
                    print("❌ Ошибка: Сессия не авторизована")
                    print("Используйте generate_session.py для создания новой сессии")
                    return False
                print("✓ Подключено к Telegram")
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️  Попытка {attempt + 1} не удалась: {e}")
                    print(f"Повторная попытка через 2 секунды...")
                    await asyncio.sleep(2)
                else:
                    print(f"❌ Не удалось подключиться после {max_retries} попыток")
                    print(f"Ошибка: {e}")
                    print("\nВозможные причины:")
                    print("1. Проверьте API credentials (api_id, api_hash)")
                    print("2. Проверьте строку сессии")
                    print("3. Проверьте интернет-соединение")
                    print("4. Попробуйте создать новую сессию: python src/tplexity/generate_session.py")
                    return False

    async def disconnect(self):
        """Отключение от Telegram."""
        try:
            if self.client.is_connected():
                await self.client.disconnect()
                print("✓ Отключено от Telegram")
        except Exception as e:
            print(f"⚠️  Ошибка при отключении: {e}")

    async def get_channel_info(self, channel_username: str) -> Dict[str, Any]:
        """
        Получить информацию о канале.
        
        Args:
            channel_username: Username канала (без @) или ссылка

        Returns:
            Словарь с информацией о канале
        """
        channel = await self.client.get_entity(channel_username)
        
        info = {
            "id": channel.id,
            "title": getattr(channel, "title", None),
            "username": getattr(channel, "username", None),
            "participants_count": getattr(channel, "participants_count", None),
            "description": getattr(channel, "about", None),
        }
        
        return info

    async def download_messages(
        self,
        channel_username: str,
        limit: Optional[int] = None,
        offset_date: Optional[datetime] = None,
        min_id: int = 0,
        max_id: int = 0,
        reverse: bool = False,
        save_media: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Скачать сообщения из канала.

        Args:
            channel_username: Username канала (без @) или ссылка
            limit: Максимальное количество сообщений (None = все)
            offset_date: Дата, с которой начать скачивание
            min_id: Минимальный ID сообщения
            max_id: Максимальный ID сообщения
            reverse: Скачивать в обратном порядке (от старых к новым)
            save_media: Сохранять медиа файлы

        Returns:
            Список словарей с данными сообщений
        """
        print(f"Скачивание сообщений из канала: {channel_username}")
        
        channel = await self.client.get_entity(channel_username)
        messages_data = []
        
        # Создаем папку для канала
        channel_folder = self.download_path / self._sanitize_filename(channel_username)
        channel_folder.mkdir(exist_ok=True)
        
        if save_media:
            media_folder = channel_folder / "media"
            media_folder.mkdir(exist_ok=True)
        
        # Получаем сообщения
        count = 0
        async for message in self.client.iter_messages(
            channel,
            limit=limit,
            offset_date=offset_date,
            min_id=min_id,
            max_id=max_id,
            reverse=reverse,
        ):
            if not isinstance(message, Message):
                continue
            
            count += 1
            if limit and count % 10 == 0:
                print(f"  Скачано {count}/{limit} сообщений...")
            elif not limit and count % 100 == 0:
                print(f"  Скачано {count} сообщений...")
            
            message_dict = await self._message_to_dict(message, channel_username)
            
            # Скачивание медиа, если требуется
            if save_media and message.media:
                try:
                    media_path = await message.download_media(
                        file=str(media_folder / f"{message.id}")
                    )
                    message_dict["media_path"] = media_path
                except Exception as e:
                    print(f"Ошибка при скачивании медиа {message.id}: {e}")
                    message_dict["media_path"] = None
            
            messages_data.append(message_dict)
        
        print(f"✓ Скачано {len(messages_data)} сообщений")
        
        return messages_data

    async def _message_to_dict(self, message: Message, channel_username: str = None) -> Dict[str, Any]:
        """
        Преобразовать сообщение в словарь.

        Args:
            message: Объект сообщения Telethon
            channel_username: Username канала для формирования ссылки

        Returns:
            Словарь с данными сообщения
        """
        # Формируем ссылку на сообщение
        message_link = None
        if channel_username:
            # Убираем @ если есть
            clean_username = channel_username.lstrip('@')
            message_link = f"https://t.me/{clean_username}/{message.id}"
        
        return {
            "id": message.id,
            "link": message_link,
            "date": message.date.isoformat() if message.date else None,
            "text": message.text,
            "views": message.views,
            "forwards": message.forwards,
            "edit_date": message.edit_date.isoformat() if message.edit_date else None,
            "has_media": message.media is not None,
            "media_type": type(message.media).__name__ if message.media else None,
        }

    @staticmethod
    def filter_empty_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Фильтрует сообщения, удаляя те, у которых пустой текст.
        
        Args:
            messages: Список сообщений
            
        Returns:
            Отфильтрованный список сообщений
        """
        filtered = [msg for msg in messages if msg.get("text") and msg["text"].strip()]
        removed_count = len(messages) - len(filtered)
        if removed_count > 0:
            print(f"  Удалено {removed_count} сообщений с пустым текстом")
        return filtered

    def save_to_json(
        self,
        data: List[Dict[str, Any]],
        channel_username: str,
        filename: Optional[str] = None,
        filter_empty: bool = False,
    ):
        """
        Сохранить данные в JSON файл.

        Args:
            data: Список словарей с данными
            channel_username: Username канала
            filename: Имя файла (если None, будет сгенерировано автоматически)
            filter_empty: Удалять ли сообщения с пустым текстом
        """
        # Фильтруем пустые сообщения если нужно
        if filter_empty:
            data = self.filter_empty_messages(data)
        
        channel_folder = self.download_path / self._sanitize_filename(channel_username)
        channel_folder.mkdir(exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"messages_{timestamp}.json"
        
        filepath = channel_folder / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Данные сохранены в {filepath}")
        return filepath
    
    def append_to_json(
        self,
        new_data: List[Dict[str, Any]],
        filepath: Path,
    ):
        """
        Добавить новые данные к существующему JSON файлу.

        Args:
            new_data: Список новых сообщений
            filepath: Путь к существующему JSON файлу
        """
        # Читаем существующие данные
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        
        # Добавляем новые данные
        existing_data.extend(new_data)
        
        # Сохраняем обратно
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Добавлено {len(new_data)} новых сообщений в {filepath}")

    def save_to_csv(
        self,
        data: List[Dict[str, Any]],
        channel_username: str,
        filename: Optional[str] = None,
        filter_empty: bool = False,
    ):
        """
        Сохранить данные в CSV файл.

        Args:
            data: Список словарей с данными
            channel_username: Username канала
            filename: Имя файла (если None, будет сгенерировано автоматически)
            filter_empty: Удалять ли сообщения с пустым текстом
        """
        # Фильтруем пустые сообщения если нужно
        if filter_empty:
            data = self.filter_empty_messages(data)
        
        channel_folder = self.download_path / self._sanitize_filename(channel_username)
        channel_folder.mkdir(exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"messages_{timestamp}.csv"
        
        filepath = channel_folder / filename
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding="utf-8")
        
        print(f"✓ Данные сохранены в {filepath}")

    def save_to_parquet(
        self,
        data: List[Dict[str, Any]],
        channel_username: str,
        filename: Optional[str] = None,
        filter_empty: bool = False,
    ):
        """
        Сохранить данные в Parquet файл.

        Args:
            data: Список словарей с данными
            channel_username: Username канала
            filename: Имя файла (если None, будет сгенерировано автоматически)
            filter_empty: Удалять ли сообщения с пустым текстом
        """
        # Фильтруем пустые сообщения если нужно
        if filter_empty:
            data = self.filter_empty_messages(data)
        
        channel_folder = self.download_path / self._sanitize_filename(channel_username)
        channel_folder.mkdir(exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"messages_{timestamp}.parquet"
        
        filepath = channel_folder / filename
        
        df = pd.DataFrame(data)
        df.to_parquet(filepath, index=False)
        
        print(f"✓ Данные сохранены в {filepath}")

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Очистить имя файла от недопустимых символов.

        Args:
            filename: Исходное имя файла

        Returns:
            Очищенное имя файла
        """
        # Удаляем @ если есть
        filename = filename.lstrip("@")
        # Заменяем недопустимые символы
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")
        return filename

    async def download_multiple_channels(
        self,
        channel_usernames: List[str],
        limit: Optional[int] = None,
        save_format: str = "json",
        save_media: bool = False,
    ):
        """
        Скачать сообщения из нескольких каналов.

        Args:
            channel_usernames: Список username каналов
            limit: Максимальное количество сообщений из каждого канала
            save_format: Формат сохранения ('json', 'csv', 'parquet')
            save_media: Сохранять медиа файлы
        """
        for channel in channel_usernames:
            try:
                print(f"\n{'='*60}")
                print(f"Обработка канала: {channel}")
                print(f"{'='*60}")
                
                # Получаем информацию о канале
                info = await self.get_channel_info(channel)
                print(f"Канал: {info.get('title', channel)}")
                print(f"Подписчиков: {info.get('participants_count', 'N/A')}")
                
                # Скачиваем сообщения
                messages = await self.download_messages(
                    channel,
                    limit=limit,
                    save_media=save_media,
                )
                
                # Сохраняем в нужном формате
                if save_format == "json":
                    self.save_to_json(messages, channel)
                elif save_format == "csv":
                    self.save_to_csv(messages, channel)
                elif save_format == "parquet":
                    self.save_to_parquet(messages, channel)
                else:
                    raise ValueError(f"Неподдерживаемый формат: {save_format}")
                
            except Exception as e:
                print(f"✗ Ошибка при обработке канала {channel}: {e}")
                continue


async def main():
    """Пример использования."""
    # Получаем credentials из переменных окружения
    from dotenv import load_dotenv
    load_dotenv()
    
    api_id = int(os.getenv("TELEGRAM_API_ID", "0"))
    api_hash = os.getenv("TELEGRAM_API_HASH", "")
    
    if not api_id or not api_hash:
        print("Ошибка: Укажите TELEGRAM_API_ID и TELEGRAM_API_HASH в .env файле")
        print("Получить можно здесь: https://my.telegram.org")
        return
    
    # Создаем downloader
    downloader = TelegramDownloader(
        api_id=api_id,
        api_hash=api_hash,
        session_name="my_session",
        download_path="data/telegram"
    )
    
    try:
        # Подключаемся
        connected = await downloader.connect()
        if not connected:
            return
        
        # Пример: скачать последние 100 сообщений из одного канала
        messages = await downloader.download_messages(
            channel_username="durov",  # Замените на нужный канал
            limit=100,
            save_media=False,
        )
        
        # Сохраняем в разных форматах
        downloader.save_to_json(messages, "durov")
        downloader.save_to_csv(messages, "durov")
        
        # Пример: скачать из нескольких каналов
        # await downloader.download_multiple_channels(
        #     channel_usernames=["channel1", "channel2", "channel3"],
        #     limit=1000,
        #     save_format="parquet",
        #     save_media=False,
        # )
        
    finally:
        # Отключаемся
        await downloader.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

