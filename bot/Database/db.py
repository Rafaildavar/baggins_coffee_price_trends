from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
from sqlalchemy import Column, Integer, BigInteger, String, Text, DECIMAL, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey
from datetime import datetime
import logging



# Создание базового класса путем наследования от declarative_base
Base = declarative_base()
load_dotenv()
database_url = os.getenv('DATABASE_URL')
# Создание асинхронного движка для подключения к базе данных
engine = create_async_engine(database_url, echo=True)

# Создание асинхронной сессии
session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

logger = logging.getLogger(__name__)
# Модель для таблицы учета id customer
class Customer(Base):
    __tablename__ = 'customer_id'

    C_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(BigInteger, nullable=False, unique=True)
    tg_id: Mapped[str] = mapped_column(BigInteger, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
