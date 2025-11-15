"""
Точка входа для запуска Telegram Monitor микросервиса
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "tplexity.tg_parse.app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
