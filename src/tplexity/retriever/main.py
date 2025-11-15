"""
Точка входа для запуска Retriever микросервиса
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "tplexity.retriever.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
