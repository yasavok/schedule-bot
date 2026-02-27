"""
Модуль для работы с базой данных SQLite
Хранит информацию о пользователях бота
"""

import sqlite3
import logging
from typing import List
from config import DATABASE_PATH

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с базой данных пользователей"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """Инициализация подключения к БД"""
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Создание таблицы пользователей, если её нет"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                logger.info("База данных инициализирована")
        except sqlite3.Error as e:
            logger.error(f"Ошибка при инициализации БД: {e}")
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None) -> bool:
        """
        Добавление пользователя в базу данных
        
        Args:
            user_id: ID пользователя Telegram
            username: Username пользователя
            first_name: Имя пользователя
            
        Returns:
            True если пользователь добавлен, False если уже существует
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
                    (user_id, username, first_name)
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Пользователь {user_id} добавлен в БД")
                    return True
                else:
                    logger.info(f"Пользователь {user_id} уже существует в БД")
                    return False
        except sqlite3.Error as e:
            logger.error(f"Ошибка при добавлении пользователя {user_id}: {e}")
            return False
    
    def remove_user(self, user_id: int) -> bool:
        """
        Удаление пользователя из базы данных
        
        Args:
            user_id: ID пользователя Telegram
            
        Returns:
            True если пользователь удален, False если не найден
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Пользователь {user_id} удален из БД")
                    return True
                else:
                    logger.info(f"Пользователь {user_id} не найден в БД")
                    return False
        except sqlite3.Error as e:
            logger.error(f"Ошибка при удалении пользователя {user_id}: {e}")
            return False
    
    def is_subscribed(self, user_id: int) -> bool:
        """
        Проверка, подписан ли пользователь
        
        Args:
            user_id: ID пользователя Telegram
            
        Returns:
            True если подписан, False если нет
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logger.error(f"Ошибка при проверке подписки {user_id}: {e}")
            return False
    
    def get_all_users(self) -> List[int]:
        """
        Получение списка всех подписанных пользователей
        
        Returns:
            Список ID пользователей
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users")
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении списка пользователей: {e}")
            return []
    
    def get_users_count(self) -> int:
        """
        Получение количества подписанных пользователей
        
        Returns:
            Количество пользователей
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Ошибка при подсчете пользователей: {e}")
            return 0


# Создание глобального экземпляра базы данных
db = Database()
