import asyncio
import logging
import sys
from pathlib import Path

# Определяем корень проекта (на 2 уровня выше от текущего файла)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

from tplexity.retriever.retriever_service import RetrieverService


async def main():
    """Главная асинхронная функция"""
    service = RetrieverService()
    
    count_result = await service.vector_search.client.count(
        collection_name=service.vector_search.collection_name
    )
    print(f"Количество документов в коллекции '{service.vector_search.collection_name}': {count_result.count}")


if __name__ == "__main__":
    asyncio.run(main())