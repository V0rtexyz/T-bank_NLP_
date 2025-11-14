"""
Микросервис для мониторинга Telegram каналов, чанкирования постов и отправки данных.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import httpx
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# Импорты из нашего проекта
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tplexity.tg_parse.monitor import ChannelMonitor
from tplexity.tg_parse.chunker import PostChunker
from tplexity.tg_parse.telegram_downloader import TelegramDownloader


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Pydantic модели
class ServiceConfig(BaseModel):
    """Конфигурация микросервиса."""
    channels: List[str] = Field(default_factory=list)
    check_interval: int = 60
    initial_messages_limit: int = 100
    webhook_url: Optional[str] = None
    api_id: Optional[int] = None
    api_hash: Optional[str] = None
    phone: Optional[str] = None
    session_name: str = "my_session"
    data_dir: str = "data"


# Глобальное состояние
app = FastAPI(title="Telegram Monitor & Chunker", version="1.0.0")
config: Optional[ServiceConfig] = None
monitoring_task: Optional[asyncio.Task] = None
is_monitoring = False


class TelegramMonitorService:
    """Сервис для мониторинга Telegram и чанкирования постов."""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        # Определяем корень проекта (3 уровня выше от app.py)
        self.project_root = Path(__file__).parent.parent.parent.parent
        # Все пути относительно корня проекта
        self.data_dir = self.project_root / config.data_dir
        self.telegram_dir = self.data_dir / 'telegram'
        self.downloader: Optional[TelegramDownloader] = None
        self.monitor: Optional[ChannelMonitor] = None
        self.chunkers: Dict[str, PostChunker] = {}
        self.is_running = False
        
    async def initialize(self):
        """Инициализация: загрузка существующих данных."""
        logger.info("Инициализация сервиса...")
        logger.info(f"Корень проекта: {self.project_root}")
        logger.info(f"Директория данных: {self.data_dir}")
        
        # Создаем директории если нужно
        self.telegram_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем TelegramDownloader
        # Путь к файлу сессии относительно корня проекта
        session_path = self.project_root / self.config.session_name
        
        self.downloader = TelegramDownloader(
            api_id=self.config.api_id,
            api_hash=self.config.api_hash,
            session_name=str(session_path),
            download_path=str(self.telegram_dir)
        )
        
        # Подключаемся к Telegram
        await self.downloader.client.connect()
        if not await self.downloader.client.is_user_authorized():
            logger.warning("Telegram клиент не авторизован")
        else:
            logger.info("Telegram клиент успешно подключен")
        
        # Создаем ChannelMonitor
        self.monitor = ChannelMonitor(downloader=self.downloader)
        logger.info("Создан монитор для Telegram каналов")
        
        # Инициализируем чанкеры для каждого канала
        for channel in self.config.channels:
            self.chunkers[channel] = PostChunker(source_name=channel)
            logger.info(f"Инициализирован чанкер для канала: {channel}")
        
        # Загружаем и чанкируем существующие данные
        await self._load_and_chunk_existing_data()
        
        logger.info("Инициализация завершена")
    
    async def _load_and_chunk_existing_data(self):
        """Загружает и чанкирует существующие данные при старте."""
        logger.info("Загрузка существующих данных...")
        
        for channel in self.config.channels:
            channel_dir = self.telegram_dir / channel
            messages_file = channel_dir / 'messages_monitor.json'
            chunks_file = channel_dir / 'messages_chunked.json'
            
            if not messages_file.exists():
                logger.warning(f"Файл {messages_file} не найден, пропускаем")
                continue
            
            # Загружаем посты
            with open(messages_file, 'r', encoding='utf-8') as f:
                posts = json.load(f)
            
            # Фильтруем посты с пустым текстом
            posts_with_text = [p for p in posts if p.get('text', '').strip()]
            
            logger.info(f"Канал {channel}: найдено {len(posts)} постов ({len(posts_with_text)} с текстом)")
            
            # Чанкируем все посты
            all_chunks = []
            for post in posts_with_text:
                chunks = self.chunkers[channel].chunk_post(post)
                for chunk in chunks:
                    chunk['channel_name'] = channel
                all_chunks.extend(chunks)
            
            # Сохраняем чанки
            with open(chunks_file, 'w', encoding='utf-8') as f:
                json.dump(all_chunks, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Канал {channel}: создано {len(all_chunks)} чанков")
    
    async def start_monitoring(self):
        """Запускает асинхронный мониторинг каналов."""
        if self.is_running:
            logger.warning("Мониторинг уже запущен")
            return
        
        self.is_running = True
        logger.info("Запуск мониторинга каналов...")
        
        # Запускаем цикл мониторинга
        while self.is_running:
            try:
                await self._check_new_messages()
                await asyncio.sleep(self.config.check_interval)
            except Exception as e:
                logger.error(f"Ошибка в цикле мониторинга: {e}", exc_info=True)
                await asyncio.sleep(5)
    
    async def _check_new_messages(self):
        """Проверяет новые сообщения во всех каналах."""
        logger.info("Проверка новых сообщений...")
        
        for channel in self.config.channels:
            try:
                # Проверяем новые сообщения
                new_messages = await self.monitor.check_new_messages(channel)
                
                if new_messages:
                    # Фильтруем сообщения с пустым текстом
                    messages_with_text = [m for m in new_messages if m.get('text', '').strip()]
                    
                    logger.info(f"Канал {channel}: найдено {len(new_messages)} новых сообщений ({len(messages_with_text)} с текстом)")
                    
                    # Чанкируем новые сообщения
                    new_chunks = []
                    for message in messages_with_text:
                        chunks = self.chunkers[channel].chunk_post(message)
                        for chunk in chunks:
                            chunk['channel_name'] = channel
                        new_chunks.extend(chunks)
                    
                    logger.info(f"Канал {channel}: создано {len(new_chunks)} новых чанков")
                    
                    # Сохраняем чанки
                    if new_chunks:
                        await self._save_chunks(channel, new_chunks)
                        
                        # Отправляем в другой сервис
                        if self.config.webhook_url:
                            await self._send_to_webhook(new_chunks)
                
            except Exception as e:
                logger.error(f"Ошибка при проверке канала {channel}: {e}", exc_info=True)
    
    async def _save_chunks(self, channel: str, new_chunks: List[Dict[str, Any]]):
        """Сохраняет новые чанки в файл."""
        chunks_file = self.telegram_dir / channel / 'messages_chunked.json'
        
        # Загружаем существующие чанки
        existing_chunks = []
        if chunks_file.exists():
            with open(chunks_file, 'r', encoding='utf-8') as f:
                existing_chunks = json.load(f)
        
        # Добавляем новые чанки
        all_chunks = existing_chunks + new_chunks
        
        # Сохраняем
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Чанки сохранены в {chunks_file}")
    
    async def _send_to_webhook(self, chunks: List[Dict[str, Any]]):
        """Отправляет чанки в другой сервис через webhook."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.config.webhook_url,
                    json={'chunks': chunks},
                    timeout=30.0
                )
                response.raise_for_status()
                logger.info(f"Отправлено {len(chunks)} чанков в {self.config.webhook_url}")
        except Exception as e:
            logger.error(f"Ошибка при отправке в webhook: {e}", exc_info=True)
    
    async def download_initial_messages(self) -> Dict[str, Any]:
        """
        Скачивает последние n сообщений из каждого канала.
        Удаляет пустые сообщения и сохраняет результаты.
        
        Returns:
            Статистика по скачанным сообщениям
        """
        logger.info(f"Скачивание последних {self.config.initial_messages_limit} сообщений из каждого канала...")
        
        results = {
            "total_downloaded": 0,
            "total_saved": 0,
            "channels": {}
        }
        
        for channel in self.config.channels:
            try:
                logger.info(f"Скачивание из канала: {channel}")
                
                # Скачиваем сообщения
                messages = await self.downloader.download_messages(
                    channel_username=channel,
                    limit=self.config.initial_messages_limit
                )
                
                downloaded_count = len(messages)
                
                # Фильтруем пустые сообщения
                messages_with_text = [msg for msg in messages if msg.get('text', '').strip()]
                saved_count = len(messages_with_text)
                
                logger.info(f"Канал {channel}: скачано {downloaded_count}, с текстом {saved_count}")
                
                # Сохраняем в JSON
                if messages_with_text:
                    channel_dir = self.telegram_dir / channel
                    channel_dir.mkdir(parents=True, exist_ok=True)
                    
                    messages_file = channel_dir / 'messages_monitor.json'
                    with open(messages_file, 'w', encoding='utf-8') as f:
                        json.dump(messages_with_text, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"Сохранено в {messages_file}")
                    
                    # Обновляем состояние монитора
                    if messages_with_text:
                        last_id = max(msg["id"] for msg in messages_with_text)
                        self.monitor.channel_states[channel] = (last_id, str(messages_file))
                
                results["channels"][channel] = {
                    "downloaded": downloaded_count,
                    "saved": saved_count,
                    "filtered_out": downloaded_count - saved_count
                }
                results["total_downloaded"] += downloaded_count
                results["total_saved"] += saved_count
                
            except Exception as e:
                logger.error(f"Ошибка при скачивании из {channel}: {e}", exc_info=True)
                results["channels"][channel] = {
                    "error": str(e)
                }
        
        logger.info(f"Скачивание завершено. Всего скачано: {results['total_downloaded']}, сохранено: {results['total_saved']}")
        return results
    
    async def stop_monitoring(self):
        """Останавливает мониторинг."""
        logger.info("Остановка мониторинга...")
        self.is_running = False
        
        # Закрываем Telegram соединение
        if self.downloader and self.downloader.client:
            try:
                await self.downloader.client.disconnect()
                logger.info("Telegram клиент отключен")
            except Exception as e:
                logger.error(f"Ошибка при отключении клиента: {e}")
        
        logger.info("Мониторинг остановлен")


# Глобальный экземпляр сервиса
service: Optional[TelegramMonitorService] = None


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Инициализация при старте приложения."""
    logger.info("Запуск микросервиса...")
    
    # Загружаем конфигурацию (config.json находится в той же директории что и app.py)
    config_file = Path(__file__).parent / "config.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        global config
        config = ServiceConfig(**config_data)
        logger.info(f"Загружена конфигурация: {config.channels}")
    else:
        logger.warning(f"Файл config.json не найден: {config_file}")
        config = ServiceConfig()


@app.post("/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    """Запускает мониторинг Telegram каналов."""
    global service, is_monitoring
    
    if is_monitoring:
        return {"status": "already_running"}
    
    if not config or not config.channels:
        raise HTTPException(400, "Конфигурация не загружена")
    
    try:
        service = TelegramMonitorService(config)
        await service.initialize()
        background_tasks.add_task(service.start_monitoring)
        is_monitoring = True
        
        return {
            "status": "started",
            "channels": config.channels,
            "check_interval": config.check_interval
        }
    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
        raise HTTPException(500, str(e))


@app.post("/stop")
async def stop_monitoring():
    """Останавливает мониторинг."""
    global service, is_monitoring
    
    if not is_monitoring or not service:
        return {"status": "not_running"}
    
    await service.stop_monitoring()
    is_monitoring = False
    service = None
    
    return {"status": "stopped"}


@app.post("/download")
async def download_messages():
    """
    Скачивает последние n сообщений из каждого канала.
    
    - Количество сообщений (n) настраивается в config.json (параметр initial_messages_limit)
    - Автоматически удаляет пустые сообщения (где поле text пустое)
    - Сохраняет результаты в data/telegram/[канал]/messages_monitor.json
    
    Returns:
        Статистика по скачанным и сохраненным сообщениям
    """
    global service
    
    if not config or not config.channels:
        raise HTTPException(400, "Конфигурация не загружена")
    
    try:
        # Если сервис не инициализирован, создаем его
        if not service:
            service = TelegramMonitorService(config)
            await service.initialize()
        
        # Скачиваем сообщения
        results = await service.download_initial_messages()
        
        return {
            "status": "success",
            "limit_per_channel": config.initial_messages_limit,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Ошибка при скачивании: {e}", exc_info=True)
        raise HTTPException(500, str(e))


@app.get("/status")
async def get_status():
    """Статус сервиса."""
    return {
        "status": "running" if is_monitoring else "stopped",
        "config": config.dict() if config else None,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Информация о сервисе."""
    return {
        "service": "Telegram Monitor & Chunker",
        "version": "1.0.0",
        "endpoints": {
            "download": "POST /download - Скачать последние n сообщений из каналов",
            "start": "POST /start - Запустить мониторинг",
            "stop": "POST /stop - Остановить мониторинг",
            "status": "GET /status - Статус сервиса",
            "health": "GET /health - Health check",
            "docs": "GET /docs - Swagger UI"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

