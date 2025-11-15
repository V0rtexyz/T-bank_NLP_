"""
Точка входа для запуска Telegram Bot
"""

import asyncio

if __name__ == "__main__":
    from tplexity.tg_bot.bot import main
    
    asyncio.run(main())

