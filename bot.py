import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os
from aiogram import Bot, Dispatcher
from app.handlers import router
from app.database.models import init_db, seed_systems
import config

# Налаштування логування
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Формат логів
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Логування в файл з ротацією (максимум 5 файлів по 5MB)
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'bot.log'),
    maxBytes=5*1024*1024,  # 5MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(log_format)

# Логування в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)

# Налаштування root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("========================================")
        logger.info("Запуск Telegram бота...")
        logger.info(f"Токен бота: {config.BOT_TOKEN[:10]}...")
        
        # Ініціалізація БД
        logger.info("Ініціалізація бази даних...")
        await init_db()
        logger.info("База даних ініціалізована")
        
        # Додавання початкових даних
        logger.info("Додавання початкових даних...")
        await seed_systems()
        logger.info("Початкові дані додані")
        
        # Створення бота та диспетчера
        bot = Bot(token=config.BOT_TOKEN)
        dp = Dispatcher()
        dp.include_router(router)
        
        logger.info("Бот успішно запущено! Очікування повідомлень...")
        logger.info("========================================")
        
        try:
            await dp.start_polling(bot)
        finally:
            await bot.session.close()
            logger.info("Бот зупинено, з'єднання закрито")
            
    except Exception as e:
        logger.error(f"Критична помилка при запуску бота: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот зупинено користувачем (Ctrl+C)")
        print("\n👋 Бот зупинено")
    except Exception as e:
        logger.error(f"Неочікувана помилка: {e}", exc_info=True)
        print(f"\n❌ Помилка: {e}")