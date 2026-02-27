"""
Скрипт для тестирования парсера расписания
Запустите этот файл, чтобы проверить работу парсера без запуска бота
"""

import asyncio
import logging
from parser import parser

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def test_parser():
    """Тестирование парсера"""
    print("=" * 50)
    print("Тестирование парсера расписания")
    print("=" * 50)
    print()
    
    print("1. Проверка доступности сайта...")
    html = await parser.fetch_page("https://lsxt.my1.ru/blog/")
    
    if html:
        print("✅ Сайт доступен")
        print(f"   Размер страницы: {len(html)} байт")
    else:
        print("❌ Сайт недоступен")
        return
    
    print()
    print("2. Парсинг изображений...")
    images = await parser.parse_schedule_images(html)
    
    if images:
        print(f"✅ Найдено изображений: {len(images)}")
        for i, img_url in enumerate(images, 1):
            print(f"   {i}. {img_url}")
    else:
        print("❌ Изображения не найдены")
        print("   Возможно, на сайте нет расписания или изменилась структура")
    
    print()
    print("3. Проверка обновлений...")
    has_update, schedule_path = await parser.check_for_updates()
    
    if has_update:
        print(f"✅ Найдено новое расписание!")
        print(f"   Сохранено в: {schedule_path}")
    else:
        print("ℹ️  Новых обновлений нет (или расписание уже было скачано)")
    
    print()
    print("4. Информация о последнем хэше...")
    last_hash = parser.get_last_hash()
    if last_hash:
        print(f"   Последний хэш: {last_hash}")
    else:
        print("   Хэш еще не сохранен")
    
    print()
    print("=" * 50)
    print("Тестирование завершено")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_parser())
