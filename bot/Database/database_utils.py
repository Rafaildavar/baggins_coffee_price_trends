import logging
import asyncio
from db import Base, engine

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для создания таблиц в базе данных
async def initialize_database():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы успешно созданы в базе данных.")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        raise

# Функция для удаления таблиц из базы данных
async def clear_database():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Таблицы успешно удалены из базы данных.")
    except Exception as e:
        logger.error(f"Ошибка при удалении таблиц: {e}")
        raise

# # Функция для корректного завершения работы с базой данных
# async def shutdown():
#     await engine.dispose()
#     logger.info("Подключение к базе данных закрыто.")
#
# # Главная функция, которая вызывает инициализацию базы данных и затем завершает работу
# async def main():
#     try:
#         await initialize_database()
#     finally:
#         await shutdown()
#
#      # Запуск программы
# if __name__ == "__main__":
#     asyncio.run(main())