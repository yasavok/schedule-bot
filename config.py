"""
Конфигурационный файл с настройками бота
"""

import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Токен бота (получить у @BotFather)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# URL сайта колледжа для парсинга
COLLEGE_URL = "https://lsxt.my1.ru/blog/"

# Интервал проверки обновлений (в секундах)
# 6 часов = 21600 секунд, 1 день = 86400 секунд
CHECK_INTERVAL = 21600  # 6 часов

# Путь к файлу базы данных
DATABASE_PATH = "database.db"

# Путь к папке для сохранения фото расписания
SCHEDULE_FOLDER = "schedules"

# Создание папки для расписаний, если её нет
os.makedirs(SCHEDULE_FOLDER, exist_ok=True)
