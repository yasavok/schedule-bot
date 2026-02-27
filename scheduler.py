"""
Модуль для фоновой проверки обновлений расписания
"""

import asyncio
import logging
from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from parser import parser
from database import db

logger = logging.getLogger(__name__)


async def send_schedule_to_users(bot: Bot, schedule_path: str, caption: str = "📅 Новое расписание!"):
    """
    Отправка расписания всем подписанным пользователям
    
    Args:
        bot: Экземпляр бота
        schedule_path: Путь к файлу с расписанием
        caption: Подпись к изображению
    """
    users = db.get_all_users()
    
    if not users:
        logger.info("Нет подписанных пользователей для рассылки")
        return
    
    logger.info(f"Начинаем рассылку расписания {len(users)} пользователям")
    
    success_count = 0
    error_count = 0
    blocked_count = 0
    
    # Создаем объект файла для отправки
    photo = FSInputFile(schedule_path)
    
    for user_id in users:
        try:
            await bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=caption
            )
            success_count += 1
            logger.info(f"Расписание отправлено пользователю {user_id}")
            
            # Небольшая задержка между отправками, чтобы не превысить лимиты Telegram
            await asyncio.sleep(0.05)
            
        except TelegramForbiddenError:
            # Пользователь заблокировал бота
            logger.warning(f"Пользователь {user_id} заблокировал бота, удаляем из БД")
            db.remove_user(user_id)
            blocked_count += 1
            
        except TelegramBadRequest as e:
            logger.error(f"Ошибка отправки пользователю {user_id}: {e}")
            error_count += 1
            
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке пользователю {user_id}: {e}")
            error_count += 1
    
    logger.info(
        f"Рассылка завершена. Успешно: {success_count}, "
        f"Ошибок: {error_count}, Заблокировали: {blocked_count}"
    )


async def check_schedule_updates(bot: Bot):
    """
    Проверка обновлений расписания и рассылка при наличии
    
    Args:
        bot: Экземпляр бота
    """
    try:
        logger.info("Запуск проверки обновлений расписания")
        
        # Проверяем наличие обновлений
        has_update, schedule_path = await parser.check_for_updates()
        
        if has_update and schedule_path:
            logger.info(f"Найдено новое расписание: {schedule_path}")
            
            # Отправляем расписание всем подписчикам
            await send_schedule_to_users(bot, schedule_path)
        else:
            logger.info("Обновлений расписания не обнаружено")
            
    except Exception as e:
        logger.error(f"Ошибка при проверке обновлений: {e}", exc_info=True)


async def start_schedule_checker(bot: Bot, interval: int):
    """
    Запуск фонового процесса проверки расписания
    Отправляет расписание каждый день в 18:00 МСК
    
    Args:
        bot: Экземпляр бота
        interval: Интервал проверки в секундах (не используется, оставлен для совместимости)
    """
    from datetime import datetime, time, timedelta
    import pytz
    
    logger.info("Запуск планировщика ежедневной отправки расписания в 18:00 МСК")
    
    # Часовой пояс Москвы
    moscow_tz = pytz.timezone('Europe/Moscow')
    
    # Первая проверка сразу при запуске
    await check_schedule_updates(bot)
    
    while True:
        try:
            # Получаем текущее время в Москве
            now_moscow = datetime.now(moscow_tz)
            
            # Целевое время - 18:00 сегодня
            target_time = now_moscow.replace(hour=18, minute=0, second=0, microsecond=0)
            
            # Если 18:00 уже прошло сегодня, планируем на завтра
            if now_moscow >= target_time:
                target_time += timedelta(days=1)
            
            # Вычисляем время ожидания
            wait_seconds = (target_time - now_moscow).total_seconds()
            
            logger.info(f"Следующая отправка расписания: {target_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            logger.info(f"Ожидание: {wait_seconds / 3600:.1f} часов")
            
            # Ждем до 18:00
            await asyncio.sleep(wait_seconds)
            
            # Отправляем расписание в 18:00
            logger.info("Время 18:00 МСК - отправка расписания")
            await send_daily_schedule(bot)
            
        except asyncio.CancelledError:
            logger.info("Планировщик остановлен")
            break
        except Exception as e:
            logger.error(f"Критическая ошибка в планировщике: {e}", exc_info=True)
            # Ждем час перед следующей попыткой
            await asyncio.sleep(3600)


async def send_daily_schedule(bot: Bot):
    """
    Отправка расписания на завтра всем подписчикам
    
    Args:
        bot: Экземпляр бота
    """
    from datetime import datetime, timedelta
    from parser import parser
    
    try:
        logger.info("Начинаем ежедневную рассылку расписания на завтра")
        
        # Получаем расписание на завтра
        tomorrow = datetime.now() + timedelta(days=1)
        schedule_path = await parser.get_schedule_for_date(tomorrow)
        
        if not schedule_path:
            logger.warning(f"Расписание на {tomorrow.strftime('%d.%m.%Y')} не найдено")
            return
        
        logger.info(f"Отправка расписания на {tomorrow.strftime('%d.%m.%Y')}: {schedule_path}")
        
        # Отправляем всем подписчикам
        await send_schedule_to_users(bot, schedule_path, f"📅 Расписание на {tomorrow.strftime('%d.%m.%Y')}")
        
    except Exception as e:
        logger.error(f"Ошибка при ежедневной отправке расписания: {e}", exc_info=True)
