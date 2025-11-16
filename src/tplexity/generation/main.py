"""
Точка входа для запуска Generation микросервиса
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "tplexity.generation.app:app",
        host="0.0.0.0",
        port=8012,
        reload=True,
        log_level="info",
    )
