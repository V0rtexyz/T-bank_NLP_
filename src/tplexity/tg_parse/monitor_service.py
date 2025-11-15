"""
Сервис для мониторинга Telegram каналов и чанкирования постов.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import httpx

from tplexity.tg_parse.chunker import PostChunker
from tplexity.tg_parse.monitor import ChannelMonitor
from tplexity.tg_parse.telegram_downloader import TelegramDownloader

logger = logging.getLogger(__name__)


class TelegramMonitorService:
    """Сервис для мониторинга Telegram и чанкирования постов."""

    def __init__(
        self,
        api_id: int,
        api_hash: str,
        channels: list[str],
        session_name: str = "my_session",
        data_dir: str = "data",
        check_interval: int = 60,
        initial_messages_limit: int = 100,
        webhook_url: str | None = None,
    ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.channels = channels
        self.check_interval = check_interval
        self.initial_messages_limit = initial_messages_limit
        self.webhook_url = webhook_url

        # Определяем корень проекта (4 уровня выше от monitor_service.py)
        self.project_root = Path(__file__).parent.parent.parent.parent
        # Все пути относительно корня проекта
        self.data_dir = self.project_root / data_dir
        self.telegram_dir = self.data_dir / "telegram"

        self.downloader: TelegramDownloader | None = None
        self.monitor: ChannelMonitor | None = None
        self.chunkers: dict[str, PostChunker] = {}
        self.is_running = False
        self.session_name = session_name

    async def initialize(self):
        """Инициализация: загрузка существующих данных."""
        logger.info("🔧 [monitor_service] Инициализация сервиса...")
        logger.info(f"📁 [monitor_service] Корень проекта: {self.project_root}")
        logger.info(f"📁 [monitor_service] Директория данных: {self.data_dir}")

        # Создаем директории если нужно
        self.telegram_dir.mkdir(parents=True, exist_ok=True)

        # Создаем TelegramDownloader
        # Путь к файлу сессии относительно корня проекта
        session_path = self.project_root / self.session_name

        self.downloader = TelegramDownloader(
            api_id=self.api_id,
            api_hash=self.api_hash,
            session_name=str(session_path),
            download_path=str(self.telegram_dir),
        )

        # Подключаемся к Telegram
        await self.downloader.client.connect()
        if not await self.downloader.client.is_user_authorized():
            logger.warning("⚠️ [monitor_service] Telegram клиент не авторизован")
            raise ValueError("Telegram клиент не авторизован. Требуется авторизация.")
        else:
            logger.info("✅ [monitor_service] Telegram клиент успешно подключен")

        # Создаем ChannelMonitor
        self.monitor = ChannelMonitor(downloader=self.downloader)
        logger.info("✅ [monitor_service] Создан монитор для Telegram каналов")

        # Инициализируем чанкеры для каждого канала
        for channel in self.channels:
            self.chunkers[channel] = PostChunker(source_name=channel)
            logger.info(f"✅ [monitor_service] Инициализирован чанкер для канала: {channel}")

        # Загружаем и чанкируем существующие данные
        await self._load_and_chunk_existing_data()

        logger.info("✅ [monitor_service] Инициализация завершена")

    async def _load_and_chunk_existing_data(self):
        """Загружает и чанкирует существующие данные при старте."""
        logger.info("📥 [monitor_service] Загрузка существующих данных...")

        for channel in self.channels:
            channel_dir = self.telegram_dir / channel
            messages_file = channel_dir / "messages_monitor.json"
            chunks_file = channel_dir / "messages_chunked.json"

            if not messages_file.exists():
                logger.warning(f"⚠️ [monitor_service] Файл {messages_file} не найден, пропускаем")
                continue

            # Загружаем посты
            with open(messages_file, encoding="utf-8") as f:
                posts = json.load(f)

            # Фильтруем посты с пустым текстом
            posts_with_text = [p for p in posts if p.get("text", "").strip()]

            logger.info(
                f"📊 [monitor_service] Канал {channel}: найдено {len(posts)} постов ({len(posts_with_text)} с текстом)"
            )

            # Чанкируем все посты
            all_chunks = []
            for post in posts_with_text:
                chunks = self.chunkers[channel].chunk_post(post)
                for chunk in chunks:
                    chunk["channel_name"] = channel
                all_chunks.extend(chunks)

            # Сохраняем чанки
            with open(chunks_file, "w", encoding="utf-8") as f:
                json.dump(all_chunks, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ [monitor_service] Канал {channel}: создано {len(all_chunks)} чанков")

    async def start_monitoring(self):
        """Запускает асинхронный мониторинг каналов."""
        if self.is_running:
            logger.warning("⚠️ [monitor_service] Мониторинг уже запущен")
            return

        self.is_running = True
        logger.info("🚀 [monitor_service] Запуск мониторинга каналов...")

        # Запускаем цикл мониторинга
        while self.is_running:
            try:
                await self._check_new_messages()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ [monitor_service] Ошибка в цикле мониторинга: {e}", exc_info=True)
                await asyncio.sleep(5)

    async def _check_new_messages(self):
        """Проверяет новые сообщения во всех каналах."""
        logger.info("🔍 [monitor_service] Проверка новых сообщений...")

        for channel in self.channels:
            try:
                # Проверяем новые сообщения
                new_messages = await self.monitor.check_new_messages(channel)

                if new_messages:
                    # Фильтруем сообщения с пустым текстом
                    messages_with_text = [m for m in new_messages if m.get("text", "").strip()]

                    logger.info(
                        f"📨 [monitor_service] Канал {channel}: найдено {len(new_messages)} новых сообщений "
                        f"({len(messages_with_text)} с текстом)"
                    )

                    # Чанкируем новые сообщения
                    new_chunks = []
                    for message in messages_with_text:
                        chunks = self.chunkers[channel].chunk_post(message)
                        for chunk in chunks:
                            chunk["channel_name"] = channel
                        new_chunks.extend(chunks)

                    logger.info(f"📦 [monitor_service] Канал {channel}: создано {len(new_chunks)} новых чанков")

                    # Сохраняем чанки
                    if new_chunks:
                        await self._save_chunks(channel, new_chunks)

                        # Отправляем в другой сервис
                        if self.webhook_url:
                            await self._send_to_webhook(new_chunks)

            except Exception as e:
                logger.error(f"❌ [monitor_service] Ошибка при проверке канала {channel}: {e}", exc_info=True)

    async def _save_chunks(self, channel: str, new_chunks: list[dict[str, Any]]):
        """Сохраняет новые чанки в файл."""
        chunks_file = self.telegram_dir / channel / "messages_chunked.json"

        # Загружаем существующие чанки
        existing_chunks = []
        if chunks_file.exists():
            with open(chunks_file, encoding="utf-8") as f:
                existing_chunks = json.load(f)

        # Добавляем новые чанки
        all_chunks = existing_chunks + new_chunks

        # Сохраняем
        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, ensure_ascii=False, indent=2)

        logger.info(f"💾 [monitor_service] Чанки сохранены в {chunks_file}")

    async def _send_to_webhook(self, chunks: list[dict[str, Any]]):
        """Отправляет чанки в Retriever API для сохранения в БД."""
        try:
            # Преобразуем чанки в формат, ожидаемый Retriever API
            # Retriever ожидает: {"documents": [{"text": "...", "metadata": {...}}]}
            documents = []
            for chunk in chunks:
                # Извлекаем текст чанка
                text = chunk.get("text", "")
                if not text:
                    continue

                # Формируем метаданные (все остальные поля кроме text)
                metadata = {k: v for k, v in chunk.items() if k != "text"}

                documents.append({"text": text, "metadata": metadata})

            if not documents:
                logger.warning("⚠️ [monitor_service] Нет документов для отправки в Retriever")
                return

            # Отправляем в Retriever API
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json={"documents": documents}, timeout=30.0)
                response.raise_for_status()
                logger.info(f"📤 [monitor_service] Отправлено {len(documents)} документов в {self.webhook_url}")
        except Exception as e:
            logger.error(f"❌ [monitor_service] Ошибка при отправке в Retriever API: {e}", exc_info=True)

    async def download_initial_messages(self) -> dict[str, Any]:
        """
        Скачивает последние n сообщений из каждого канала.
        Удаляет пустые сообщения и сохраняет результаты.

        Returns:
            Статистика по скачанным сообщениям
        """
        logger.info(
            f"📥 [monitor_service] Скачивание последних {self.initial_messages_limit} сообщений из каждого канала..."
        )

        results: dict[str, Any] = {"total_downloaded": 0, "total_saved": 0, "channels": {}}

        for channel in self.channels:
            try:
                logger.info(f"📥 [monitor_service] Скачивание из канала: {channel}")

                # Скачиваем сообщения
                messages = await self.downloader.download_messages(
                    channel_username=channel, limit=self.initial_messages_limit
                )

                downloaded_count = len(messages)

                # Фильтруем пустые сообщения
                messages_with_text = [msg for msg in messages if msg.get("text", "").strip()]
                saved_count = len(messages_with_text)

                logger.info(
                    f"📊 [monitor_service] Канал {channel}: скачано {downloaded_count}, с текстом {saved_count}"
                )

                # Сохраняем в JSON
                if messages_with_text:
                    channel_dir = self.telegram_dir / channel
                    channel_dir.mkdir(parents=True, exist_ok=True)

                    messages_file = channel_dir / "messages_monitor.json"
                    with open(messages_file, "w", encoding="utf-8") as f:
                        json.dump(messages_with_text, f, ensure_ascii=False, indent=2)

                    logger.info(f"💾 [monitor_service] Сохранено в {messages_file}")

                    # Обновляем состояние монитора
                    if messages_with_text:
                        last_id = max(msg["id"] for msg in messages_with_text)
                        self.monitor.channel_states[channel] = (last_id, str(messages_file))

                results["channels"][channel] = {
                    "downloaded": downloaded_count,
                    "saved": saved_count,
                    "filtered_out": downloaded_count - saved_count,
                }
                results["total_downloaded"] += downloaded_count
                results["total_saved"] += saved_count

            except Exception as e:
                logger.error(f"❌ [monitor_service] Ошибка при скачивании из {channel}: {e}", exc_info=True)
                results["channels"][channel] = {"error": str(e)}

        logger.info(
            f"✅ [monitor_service] Скачивание завершено. "
            f"Всего скачано: {results['total_downloaded']}, сохранено: {results['total_saved']}"
        )
        return results

    async def stop_monitoring(self):
        """Останавливает мониторинг."""
        logger.info("🛑 [monitor_service] Остановка мониторинга...")
        self.is_running = False

        # Закрываем Telegram соединение
        if self.downloader and self.downloader.client:
            try:
                await self.downloader.client.disconnect()
                logger.info("✅ [monitor_service] Telegram клиент отключен")
            except Exception as e:
                logger.error(f"❌ [monitor_service] Ошибка при отключении клиента: {e}")

        logger.info("✅ [monitor_service] Мониторинг остановлен")
