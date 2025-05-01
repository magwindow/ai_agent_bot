import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

from handlers.users import router_users

# Загрузка переменных окружения
load_dotenv(find_dotenv())

# Создание бота
bot: Bot = Bot(
    token=os.getenv('BOT_TOKEN'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)


async def startup(dispatcher: Dispatcher):
    print('Bot is started!')


async def shutdown(dispatcher: Dispatcher):
    print('Bot is shutting down...')


async def main():
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(router_users)

    # Подключаем события старта/остановки
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    # Запуск бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
