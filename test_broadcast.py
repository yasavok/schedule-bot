"""
Тестовая рассылка расписания в 23:56
"""

import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot
from config import BOT_TOKEN
from scheduler import send_daily_schedule

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def wait_until_time(target_hour: int, target_minute: int):
    """Ожидание до указанного времени"""
    while True:
        now = datetime.now()
        target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        
        # Если время уже прошло сегодня, планируем на завтра
        if now >= target:
            target += timedelta(days=1)
        
        wait_seconds = (target - now).total_seconds()
        
        logger.info(f"Текущее время: {now.strftime('%H:%M:%S')}")
        logger.info(f"Тестовая рассылка запланирована на: {target.strftime('%H:%M:%S')}")
        logger.info(f"Ожидание: {wait_seconds:.0f} секунд ({wait_seconds/60:.1f} минут)")
        
        if wait_seconds <= 0:
            break
            
        await asyncio.sleep(wait_seconds)
        break


async def main():
    """Главная функция"""
    try:
        logger.info("=" * 60)
        logger.info("Запуск тестовой рассылки")
        logger.info("=" * 60)
        
        # Ждем до 23:56
        await wait_until_time(23, 56)
        
        logger.info("⏰ Время пришло! Начинаем рассылку...")
        
        # Создаем бота
        bot = Bot(token=BOT_TOKEN)
        
        # Отправляем расписание
        await send_daily_schedule(bot)
        
        logger.info("✅ Тестовая рассылка завершена!")
        
        await bot.session.close()
        
    except Exception as e:
        logger.error(f"Ошибка при тестовой рассылке: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Тестовая рассылка прервана пользователем")
