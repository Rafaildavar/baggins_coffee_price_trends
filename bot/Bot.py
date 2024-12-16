import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from sqlalchemy.future import select
from bot.Database.db import session_maker
from bot.Database.db import Customer
from rec_bot import generate_recommendations
from rec_bot import get_customer_info
TOKEN = '7278593611:AAHnok5stRNTA0-7hwrgb2bV9ObZ2ui-sb4'  # Замените на ваш реальный токен
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Планировщик задач
scheduler = AsyncIOScheduler()



# Еженедельная отправка рекомендаций
async def send_weekly_recommendations():
    async with session_maker() as session:
        try:
            # Получаем всех клиентов из базы
            result = await session.execute(select(Customer))
            customers = result.scalars().all()

            for customer in customers:
                # Генерация рекомендаций
                customer_data = get_customer_info(customer.customer_id)
                recommendations = generate_recommendations(customer_data)

                # Отправляем сообщения пользователю
                for key, value in recommendations.items():
                    await bot.send_message(chat_id=customer.tg_id, text=value)
            print(f"[{datetime.now()}] Рекомендации успешно отправлены всем пользователям.")
        except Exception as e:
            print(f"Ошибка при отправке рекомендаций: {e}")

# Настройка планировщика
def setup_scheduler():
    # Задача на еженедельное выполнение
    scheduler.add_job(send_weekly_recommendations, 'interval', weeks=1, start_date=datetime.now())
    scheduler.start()

# Старт бота
async def main():
    print("Бот запущен...")
    setup_scheduler()
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())