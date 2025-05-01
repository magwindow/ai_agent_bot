from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅ Назад"), KeyboardButton(text="➡ Дальше")],
        [KeyboardButton(text="❓ Задать вопрос")]
    ],
    resize_keyboard=True)
