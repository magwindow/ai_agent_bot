import os
import httpx
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from content import cards
from data_storage import user_states, awaiting_question
from keyboards.reply_keyboard import keyboard

load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')

router_users = Router()


@router_users.message(CommandStart())
async def start(message: Message):
    user_states[message.chat.id] = 0
    await message.answer("Привет! 👋\nЯ — ваш тренер по сварке от Академии СВАРГО.\nДля начала, пожалуйста, введите:\n"
                         "1. Ваше имя и фамилию\n2. Контактный телефон или email")


@router_users.message(lambda msg: user_states.get(msg.chat.id, None) == 0)
async def save_user_info(message: Message):
    # Тут можно сохранить в файл или БД
    user_states[message.chat.id] = 1
    await message.answer("Спасибо! Начнём обучение 🔧", reply_markup=keyboard)
    await message.answer(cards[0])


@router_users.message(F.text == "➡ Дальше")
async def next_card(message: Message):
    idx = user_states.get(message.chat.id, 1)
    if idx < len(cards):
        await message.answer(cards[idx], reply_markup=keyboard)
        user_states[message.chat.id] = idx + 1
    else:
        await message.answer("✅ Вы прошли все карточки!")


@router_users.message(F.text == "⬅ Назад")
async def prev_card(message: Message):
    idx = user_states.get(message.chat.id, 1)
    if idx > 1:
        user_states[message.chat.id] = idx - 1
        await message.answer(cards[idx - 2], reply_markup=keyboard)
    else:
        await message.answer("Это первая карточка.")


@router_users.message(F.text == "❓ Задать вопрос")
async def ask_question(message: Message):
    awaiting_question.add(message.chat.id)
    await message.answer("Напиши свой вопрос, и мы обязательно ответим!")


@router_users.message(lambda msg: msg.chat.id in awaiting_question)
async def handle_question(message: Message):
    chat_id = message.chat.id
    awaiting_question.remove(chat_id)
    idx = user_states.get(chat_id, 1)

    context = cards[max(0, idx - 1)]
    user_question = message.text

    prompt = (
        f"Ты виртуальный тренер по сварке. Пользователь изучает урок:\n\"{context}\"\n\n"
        f"Он задал вопрос: \"{user_question}\"\n\n"
        f"Ответь простым и понятным языком:"
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-8b-8192",  # llama3-8b-8192, llama3-70b-8192, gemma-7b-it
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            # print("Groq response:", response.text)

        answer = response.json()["choices"][0]["message"]["content"]
        await message.answer(answer)
    except Exception as e:
        await message.answer("❌ Ошибка при запросе к Groq API.")
        print(f"Groq API error: {e}")
