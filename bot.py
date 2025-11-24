import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.handlers import router
from app.database.models import init_db
import config

logging.basicConfig(level=logging.INFO)

async def main():
    # create DB
    await init_db()
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот зупинено")
