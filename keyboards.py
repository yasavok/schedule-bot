"""
Модуль с клавиатурами для бота
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard(is_subscribed: bool = False) -> ReplyKeyboardMarkup:
    """
    Создание главной клавиатуры с кнопками
    
    Args:
        is_subscribed: Подписан ли пользователь
        
    Returns:
        Клавиатура с кнопками
    """
    keyboard = [
        [
            KeyboardButton(text="✅ Подписаться" if not is_subscribed else "❌ Отписаться")
        ],
        [
            KeyboardButton(text="📅 Расписание на завтра"),
            KeyboardButton(text="📆 Выбрать дату")
        ],
        [
            KeyboardButton(text="ℹ️ Информация")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )


def get_inline_subscribe_keyboard() -> InlineKeyboardMarkup:
    """
    Создание inline клавиатуры для подписки
    
    Returns:
        Inline клавиатура
    """
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Подписаться", callback_data="subscribe"),
            InlineKeyboardButton(text="❌ Отписаться", callback_data="unsubscribe")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
