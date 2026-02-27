"""
Модуль для парсинга расписания с сайта колледжа
"""

import aiohttp
import hashlib
import logging
import os
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import Optional, Tuple, List
from config import COLLEGE_URL, SCHEDULE_FOLDER

logger = logging.getLogger(__name__)


class ScheduleParser:
    """Класс для парсинга и отслеживания обновлений расписания"""
    
    def __init__(self):
        self.last_hash_file = "last_schedule_hash.txt"
        self.last_schedule_path = None
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Загрузка HTML страницы
        
        Args:
            url: URL страницы для загрузки
            
        Returns:
            HTML контент или None при ошибке
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.error(f"Ошибка загрузки страницы: статус {response.status}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети при загрузке страницы: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при загрузке страницы: {e}")
            return None
    
    async def download_image(self, image_url: str, save_path: str) -> bool:
        """
        Скачивание изображения
        
        Args:
            image_url: URL изображения
            save_path: Путь для сохранения
            
        Returns:
            True если успешно, False при ошибке
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(save_path, 'wb') as f:
                            f.write(content)
                        logger.info(f"Изображение сохранено: {save_path}")
                        return True
                    else:
                        logger.error(f"Ошибка загрузки изображения: статус {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Ошибка при скачивании изображения: {e}")
            return False
    
    def calculate_hash(self, data: bytes) -> str:
        """
        Вычисление хэша данных для отслеживания изменений
        
        Args:
            data: Данные для хэширования
            
        Returns:
            MD5 хэш в виде строки
        """
        return hashlib.md5(data).hexdigest()
    
    def get_last_hash(self) -> Optional[str]:
        """
        Получение последнего сохраненного хэша
        
        Returns:
            Хэш или None если файл не существует
        """
        try:
            if os.path.exists(self.last_hash_file):
                with open(self.last_hash_file, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            logger.error(f"Ошибка чтения хэша: {e}")
        return None
    
    def save_hash(self, hash_value: str):
        """
        Сохранение хэша в файл
        
        Args:
            hash_value: Хэш для сохранения
        """
        try:
            with open(self.last_hash_file, 'w') as f:
                f.write(hash_value)
        except Exception as e:
            logger.error(f"Ошибка сохранения хэша: {e}")
    
    async def parse_schedule_images(self, html: str) -> list:
        """
        Парсинг изображений расписания из HTML
        
        Args:
            html: HTML контент страницы
            
        Returns:
            Список URL изображений
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Поиск изображений расписания
            images = []
            
            # Ищем изображения в папке /R7/ (там хранится расписание)
            for img in soup.find_all('img'):
                src = img.get('src', '')
                
                # Фильтруем только изображения из папки /R7/ (расписание)
                if src and '/R7/' in src:
                    # Формируем полный URL
                    if src.startswith('http'):
                        images.append(src)
                    else:
                        # Убираем /blog/ из базового URL и добавляем путь к изображению
                        base_url = "https://lsxt.my1.ru"
                        full_url = f"{base_url}{src}" if src.startswith('/') else f"{base_url}/{src}"
                        images.append(full_url)
                        logger.info(f"Найдено расписание: {full_url}")
            
            # Если не нашли в /R7/, ищем по другим признакам
            if not images:
                logger.warning("Изображения в /R7/ не найдены, ищем по другим признакам...")
                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    # Ищем изображения с расписанием в названии или большие изображения
                    if src and any(keyword in src.lower() for keyword in ['raspisanie', 'schedule', 'rasp']):
                        if src.startswith('http'):
                            images.append(src)
                        else:
                            base_url = "https://lsxt.my1.ru"
                            full_url = f"{base_url}{src}" if src.startswith('/') else f"{base_url}/{src}"
                            images.append(full_url)
            
            logger.info(f"Найдено изображений расписания: {len(images)}")
            return images
            
        except Exception as e:
            logger.error(f"Ошибка парсинга HTML: {e}")
            return []
    
    async def find_schedule_by_date(self, target_date: datetime) -> Optional[str]:
        """
        Поиск расписания на конкретную дату
        
        Args:
            target_date: Дата для поиска расписания
            
        Returns:
            URL изображения расписания или None
        """
        try:
            # Формируем URL страницы с расписанием на нужную дату
            # Формат: https://lsxt.my1.ru/blog/YYYY-MM-DD
            date_str = target_date.strftime('%Y-%m-%d')
            page_url = f"https://lsxt.my1.ru/blog/{date_str}"
            
            logger.info(f"Загружаем страницу: {page_url}")
            
            # Загружаем страницу с расписанием
            html = await self.fetch_page(page_url)
            if not html:
                logger.warning(f"Не удалось загрузить страницу для {date_str}")
                return None
            
            # Ищем изображение расписания на странице
            images = await self.parse_schedule_images(html)
            if images:
                logger.info(f"Найдено расписание на {date_str}: {images[0]}")
                return images[0]
            
            logger.warning(f"Расписание на {date_str} не найдено")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при поиске расписания по дате: {e}", exc_info=True)
            return None

    async def check_for_updates(self) -> Tuple[bool, Optional[str]]:
        """
        Проверка наличия нового расписания на завтра
        
        Returns:
            Кортеж (есть_обновление, путь_к_файлу)
        """
        try:
            logger.info("Проверка обновлений расписания...")
            
            # Ищем расписание на завтра
            tomorrow = datetime.now() + timedelta(days=1)
            image_url = await self.find_schedule_by_date(tomorrow)
            
            if not image_url:
                logger.warning("Расписание на завтра не найдено")
                return False, None
            
            logger.info(f"Найдено изображение: {image_url}")
            
            # Скачиваем изображение во временный файл для проверки
            temp_path = os.path.join(SCHEDULE_FOLDER, "temp_schedule.jpg")
            if not await self.download_image(image_url, temp_path):
                return False, None
            
            # Вычисляем хэш нового изображения
            with open(temp_path, 'rb') as f:
                new_hash = self.calculate_hash(f.read())
            
            # Сравниваем с предыдущим хэшем
            last_hash = self.get_last_hash()
            
            if last_hash != new_hash:
                # Новое расписание найдено!
                logger.info("Обнаружено новое расписание!")
                
                # Сохраняем с уникальным именем
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                final_path = os.path.join(SCHEDULE_FOLDER, f"schedule_{timestamp}.jpg")
                os.rename(temp_path, final_path)
                
                # Сохраняем новый хэш
                self.save_hash(new_hash)
                self.last_schedule_path = final_path
                
                return True, final_path
            else:
                logger.info("Расписание не изменилось")
                # Удаляем временный файл
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return False, None
                
        except Exception as e:
            logger.error(f"Ошибка при проверке обновлений: {e}", exc_info=True)
            return False, None
    
    async def get_schedule_for_date(self, target_date: datetime) -> Optional[str]:
        """
        Получение расписания на конкретную дату
        
        Args:
            target_date: Дата для получения расписания
            
        Returns:
            Путь к сохраненному файлу или None
        """
        try:
            logger.info(f"Получение расписания на {target_date.strftime('%d.%m.%Y')}")
            
            # Ищем расписание на указанную дату
            image_url = await self.find_schedule_by_date(target_date)
            
            if not image_url:
                logger.warning(f"Расписание на {target_date.strftime('%d.%m.%Y')} не найдено")
                return None
            
            # Скачиваем изображение
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(SCHEDULE_FOLDER, f"schedule_{timestamp}.jpg")
            
            if await self.download_image(image_url, file_path):
                logger.info(f"Расписание сохранено: {file_path}")
                return file_path
            else:
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при получении расписания: {e}", exc_info=True)
            return None


# Создание глобального экземпляра парсера
parser = ScheduleParser()
