import asyncio
import os
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy.future import select
from bot.Database.db import session_maker
from bot.Database.db import Customer
from rec_bot import generate_recommendations
from rec_bot import get_customer_info
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('token')
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния для FSM (машины состояний)
class ProfileState(StatesGroup):
    waiting_for_username = State()
    waiting_for_telegram_name = State()

# Планировщик задач
scheduler = AsyncIOScheduler()
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot_errors.log"),  # Логи записываются в файл
        logging.StreamHandler()  # Логи выводятся в консоль
    ]
)
# Команда /start
@dp.message(Command('start'))
async def start_command(message: types.Message):
    await message.answer("Привет! Я бот Baggins Coffee! Я буду присылать тебе скидки и предложения, специально для тебя!🎁")
    await message.answer("Для того, чтобы начать получать бонусы, нужно всего лишь ввести id, который ты можешь узнать в любимой кофейне!☕️")
    start_button = InlineKeyboardButton(text="⌨️Ввести id", callback_data="get_id")

    feedback_button = InlineKeyboardButton(text="💬Оставить отзыв", callback_data="feedback")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [start_button],
        [feedback_button]])

    await message.answer("У тебя всегда есть выбор с чем пить кофе 🥐", reply_markup=keyboard)




class IdState(StatesGroup):
    waiting_for_id = State()

# Обработчик нажатия "Мой профиль"
@dp.callback_query(F.data == 'get_id')
async def profile(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    async with session_maker() as session:  # Используем асинхронную сессию
        try:
            # Использование SQLAlchemy для получения пользователя
            result = await session.execute(select(Customer).filter(Customer.tg_id == user_id))
            user = result.scalars().first()  # Получаем пользователя

            if user:
                await callback_query.message.answer(
                'Мы уже получили ваш id, ждите наших акций!'
                )
            else:
                # Если профиля нет, предлагаем его создать
                await callback_query.message.answer(
                    "Похоже, вы еще не сообщили нам ваш id. Давайте создадим его!\nВведите ваш id:"
                )
                await state.set_state(ProfileState.waiting_for_username)
        except Exception as e:
            await callback_query.message.answer(f"Произошла ошибка: {str(e)}")
# Обработчик ввода username
@dp.message(ProfileState.waiting_for_username)
async def process_username(message: types.Message, state: FSMContext):
    await message.answer("Введите ваш id")
    user_id = message.from_user.id
    CS_id = message.text
    async with session_maker() as session:
        try:
            # Сохраняем профиль в базу данных
            customer = Customer(customer_id=CS_id, tg_id=user_id)
            session.add(customer)
            await session.commit()

            await message.answer(
                f"Ваш профиль создан!\n"
                f"Спасибо, покажите на кассе промокод NewBagginsUser! и получите скидку 10% на первый кофе ☕️"
                f"Ваш id: {CS_id}\n"
            )
        except Exception as e:
            await message.answer(f"Произошла ошибка: {str(e)}")

    await state.clear()






# Функция для записи отзыва в файл
def save_feedback_to_file(feedback_text, user_id):
    # Убедимся, что директория для файла существует
    folder = 'feedbacks'  # Папка для хранения отзывов
    if not os.path.exists(folder):
        os.makedirs(folder)  # Если папка не существует, создаем её
        # Путь к файлу
    file_path = os.path.join(folder, 'feedbacks.txt')
    # Открываем файл для добавления нового отзыва
    with open(file_path, 'a', encoding='utf-8') as file:
        # Записываем отзыв в файл
        file.write(f"Отзыв от пользователя {user_id}:\n{feedback_text}\n\n")

@dp.callback_query(F.data == 'feedback')
async def handle_feedback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Пожалуйста, оставьте свой отзыв:")
    await state.set_state(FeedbackState.waiting_for_feedback)

class FeedbackState(StatesGroup):
    waiting_for_feedback = State()


@dp.message(FeedbackState.waiting_for_feedback)
async def save_feedback(message: types.Message, state: FSMContext):
    feedback_text = message.text
    user_id = message.from_user.id  # Получаем id пользователя
    try:
        # Сохраняем отзыв в файл
        save_feedback_to_file(feedback_text, user_id)

        await message.answer("Спасибо за ваш отзыв!")
    except Exception as e:
        await message.answer(f"Произошла ошибка при сохранении отзыва: {str(e)}")
    finally:
        await state.clear()  # Очистка состояния


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
    scheduler.add_job(send_weekly_recommendations, 'interval', minutes = 1, start_date=datetime.now())
    scheduler.start()

async def main():
    print('Бот запущен')
    setup_scheduler()
    await dp.start_polling(bot)
# Запуск бота
if __name__ == '__main__':
    asyncio.run(main())
