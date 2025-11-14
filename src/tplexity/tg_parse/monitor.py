"""
Асинхронный мониторинг Telegram каналов.
Скачивает начальное количество сообщений, затем проверяет новые каждую минуту.
"""

import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv
from telegram_downloader import TelegramDownloader

# ═══════════════════════════════════════════════════════════════════
# НАСТРОЙКА: Укажите здесь ссылки на каналы для мониторинга
# ═══════════════════════════════════════════════════════════════════

CHANNEL_LINKS = [
    "https://t.me/alfa_investments",
    "https://t.me/tb_invest_official",
    "https://t.me/SberInvestments",
    "https://t.me/omyinvestments",
    "https://t.me/centralbank_russia",
    "https://t.me/selfinvestor",
]


class ChannelMonitor:
    """Мониторинг каналов на новые сообщения."""

    def __init__(self, downloader: TelegramDownloader):
        self.downloader = downloader
        # Словарь: канал -> (последний ID, путь к JSON файлу)
        self.channel_states: dict[str, tuple] = {}

    async def initial_download(self, channels: list[str], limit: int):
        """
        Начальное скачивание сообщений из каналов.

        Args:
            channels: Список каналов
            limit: Количество сообщений для скачивания
        """
        print("=" * 60)
        print("НАЧАЛЬНОЕ СКАЧИВАНИЕ")
        print("=" * 60)

        for i, channel in enumerate(channels, 1):
            print(f"\n[{i}/{len(channels)}] Канал: {channel}")

            try:
                messages = await self.downloader.download_messages(
                    channel_username=channel,
                    limit=limit,
                )

                if messages:
                    # Сохраняем
                    filename = "messages_monitor.json"
                    filepath = self.downloader.save_to_json(messages, channel, filename=filename)

                    # Запоминаем последний ID
                    last_id = max(msg["id"] for msg in messages)
                    self.channel_states[channel] = (last_id, filepath)

                    print(f"✓ Скачано {len(messages)} сообщений. Последний ID: {last_id}")
                else:
                    print(f"⚠️  Не удалось скачать сообщения из {channel}")

            except Exception as e:
                print(f"❌ Ошибка при обработке канала {channel}: {e}")
                continue

        print(f"\n{'='*60}")
        print("✅ Начальное скачивание завершено")
        print(f"{'='*60}\n")

    async def check_new_messages(self, channel: str):
        """
        Проверяет новые сообщения в канале.

        Args:
            channel: Username канала
        """
        if channel not in self.channel_states:
            return

        last_id, json_filepath = self.channel_states[channel]

        try:
            # Скачиваем только новые сообщения (min_id = последний известный ID)
            new_messages = await self.downloader.download_messages(
                channel_username=channel,
                min_id=last_id,
                limit=None,  # Все новые
            )

            # Фильтруем - оставляем только те, что действительно новее
            new_messages = [msg for msg in new_messages if msg["id"] > last_id]

            if new_messages:
                # Добавляем в JSON
                self.downloader.append_to_json(new_messages, json_filepath)

                # Обновляем последний ID
                new_last_id = max(msg["id"] for msg in new_messages)
                self.channel_states[channel] = (new_last_id, json_filepath)

                print(f"  ✓ {channel}: +{len(new_messages)} новых сообщений (до ID {new_last_id})")
                return len(new_messages)
            else:
                print(f"  • {channel}: нет новых сообщений")
                return 0

        except Exception as e:
            print(f"  ❌ {channel}: ошибка - {e}")
            return 0

    async def monitor_loop(self, check_interval: int = 60):
        """
        Бесконечный цикл мониторинга.

        Args:
            check_interval: Интервал проверки в секундах (по умолчанию 60 = 1 минута)
        """
        print("=" * 60)
        print("ЗАПУЩЕН МОНИТОРИНГ НОВЫХ СООБЩЕНИЙ")
        print(f"Проверка каждые {check_interval} секунд")
        print("Нажмите Ctrl+C для остановки")
        print("=" * 60)

        while True:
            try:
                await asyncio.sleep(check_interval)

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{current_time}] Проверка новых сообщений...")

                total_new = 0
                for channel in self.channel_states.keys():
                    new_count = await self.check_new_messages(channel)
                    total_new += new_count

                if total_new > 0:
                    print(f"✅ Всего новых сообщений: {total_new}")
                else:
                    print("• Новых сообщений нет")

            except asyncio.CancelledError:
                print("\n⚠️  Мониторинг остановлен")
                break
            except Exception as e:
                print(f"\n❌ Ошибка в цикле мониторинга: {e}")
                # Продолжаем работу даже после ошибки
                continue


async def main():
    """Главная функция."""
    load_dotenv()

    print("=" * 60)
    print("АСИНХРОННЫЙ МОНИТОРИНГ TELEGRAM КАНАЛОВ")
    print("=" * 60)

    # Показываем список каналов
    print("\nКаналы для мониторинга:")
    channels = [TelegramDownloader.parse_channel_link(link) for link in CHANNEL_LINKS]
    for i, channel in enumerate(channels, 1):
        print(f"  {i}. {channel}")

    # Запрашиваем количество для начального скачивания
    print("\nСколько последних сообщений скачать для начала?")
    limit_input = input("Количество: ").strip()

    try:
        limit = int(limit_input)
        if limit <= 0:
            print("❌ Количество должно быть больше 0")
            return
    except ValueError:
        print("❌ Введите число")
        return

    # Запрашиваем интервал проверки
    print("\nКак часто проверять новые сообщения? (в секундах)")
    interval_input = input("Интервал [60]: ").strip()

    try:
        interval = int(interval_input) if interval_input else 60
        if interval < 10:
            print("⚠️  Минимальный интервал: 10 секунд")
            interval = 10
    except ValueError:
        interval = 60

    # Создаем downloader
    session_string = os.getenv("TELEGRAM_SESSION_STRING")

    downloader = TelegramDownloader(
        api_id=int(os.getenv("TELEGRAM_API_ID")),
        api_hash=os.getenv("TELEGRAM_API_HASH"),
        session_string=session_string if session_string != "your_session_string_here" else None,
        session_name="my_session",
    )

    try:
        print("\n🔌 Подключение к Telegram...")
        connected = await downloader.connect()
        if not connected:
            return

        # Создаем монитор
        monitor = ChannelMonitor(downloader)

        # Начальное скачивание
        await monitor.initial_download(channels, limit)

        # Запускаем мониторинг
        await monitor.monitor_loop(check_interval=interval)

    except KeyboardInterrupt:
        print("\n\n⚠️  Остановка по Ctrl+C")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await downloader.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
