"""
Скрипт для ручной отправки расписания всем подписчикам
Используйте этот скрипт, если нужно отправить расписание вручную
"""

import asyncio
import logging
import sys
from aiogram import Bot
from aiogram.types import FSInputFile

from config import BOT_TOKEN
from database import db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def send_schedule_manually(image_path: str, caption: str = None):
    """
    Ручная отправка расписания всем подписчикам
    
    Args:
        image_path: Путь к файлу с расписанием
        caption: Подпись к изображению (опционально)
    """
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Получаем список пользователей
        users = db.get_all_users()
        
        if not users:
            print("❌ Нет подписанных пользователей")
            return
        
        print(f"📊 Найдено подписчиков: {len(users)}")
        print(f"📸 Файл для отправки: {image_path}")
        
        # Подтверждение
        confirm = input("\n⚠️  Отправить расписание всем пользователям? (yes/no): ")
        if confirm.lower() not in ['yes', 'y', 'да', 'д']:
            print("❌ Отправка отменена")
            return
        
        print("\n🚀 Начинаем рассылку...")
        
        # Создаем объект файла
        photo = FSInputFile(image_path)
        
        if not caption:
            caption = "📅 Расписание занятий"
        
        success_count = 0
        error_count = 0
        
        for user_id in users:
            try:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=caption
                )
                success_count += 1
                print(f"✅ Отправлено пользователю {user_id}")
                
                # Задержка между отправками
                await asyncio.sleep(0.05)
                
            except Exception as e:
                error_count += 1
                print(f"❌ Ошибка отправки пользователю {user_id}: {e}")
        
        print(f"\n📊 Результаты рассылки:")
        print(f"   ✅ Успешно: {success_count}")
        print(f"   ❌ Ошибок: {error_count}")
        
        await bot.session.close()
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)


async def main():
    """Главная функция"""
    print("=" * 60)
    print("Ручная отправка расписания подписчикам")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("❌ Использование: python manual_send.py <путь_к_изображению>")
        print()
        print("Примеры:")
        print("  python manual_send.py schedules/schedule_20240227_120000.jpg")
        print("  python manual_send.py my_schedule.png")
        return
    
    image_path = sys.argv[1]
    
    # Проверяем существование файла
    import os
    if not os.path.exists(image_path):
        print(f"❌ Файл не найден: {image_path}")
        return
    
    # Опциональная подпись
    caption = None
    if len(sys.argv) >= 3:
        caption = " ".join(sys.argv[2:])
    
    await send_schedule_manually(image_path, caption)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Отправка прервана пользователем")
