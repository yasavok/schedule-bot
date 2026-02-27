"""
Главный файл Telegram-бота для рассылки расписания колледжа
Использует aiogram 3.x
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, CHECK_INTERVAL
from handlers import register_handlers
from scheduler import start_schedule_checker

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска бота"""
    try:
        # Инициализация бота и диспетчера
        bot = Bot(token=BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Регистрация обработчиков команд
        register_handlers(dp)
        
        logger.info("Бот запущен")
        
        # Запуск фонового процесса проверки расписания
        asyncio.create_task(start_schedule_checker(bot, CHECK_INTERVAL))
        
        # Запуск polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
