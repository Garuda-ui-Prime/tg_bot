import asyncio
import logging
import os
import sqlite3
from datetime import date

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Не найден BOT_TOKEN в файле .env")


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

connection = sqlite3.connect("users.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    height REAL,
    weight REAL,
    calories INTEGER DEFAULT 0,
    calories_date TEXT
)
""")

connection.commit()


def get_user(user_id: int):
    cursor.execute(
        "SELECT user_id, height, weight, calories, calories_date "
        "FROM users WHERE user_id = ?",
        (user_id,)
    )
    return cursor.fetchone()


def create_user(user_id: int):
    today = str(date.today())

    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, height, weight, calories, calories_date)
        VALUES (?, NULL, NULL, 0, ?)
        """,
        (user_id, today)
    )

    connection.commit()


def calculate_bmi(height: float, weight: float) -> float:
    height_meters = height / 100
    return weight / (height_meters ** 2)


def bmi_status(bmi: float) -> str:
    if bmi < 18.5:
        return "Ниже нормы"
    elif bmi < 25:
        return "Норма"
    elif bmi < 30:
        return "Избыточный вес"
    else:
        return "Ожирение"


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    create_user(message.from_user.id)

    text = (
        "Привет! Я бот-помощник для контроля веса.\n\n"
        "Доступные команды:\n"
        "/set рост вес — сохранить параметры\n"
        "/bmi — рассчитать ИМТ\n"
        "/log количество — записать калории\n"
        "/today — показать калории за сегодня\n"
        "/tips — получить советы\n"
        "/help — помощь\n\n"
        "Пример:\n"
        "/set 175 80\n"
        "/log 500"
    )

    await message.answer(text)


@dp.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer(
        "Команды бота:\n\n"
    )