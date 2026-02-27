"""
Модуль с обработчиками команд и сообщений бота
"""

import logging
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import FSInputFile

from database import db
from keyboards import get_main_keyboard, get_inline_subscribe_keyboard

logger = logging.getLogger(__name__)


async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Проверяем, подписан ли пользователь
    is_subscribed = db.is_subscribed(user_id)
    
    welcome_text = (
        f"👋 Привет, {first_name}!\n\n"
        f"Я бот для рассылки расписания Лукояновского Губернского колледжа.\n\n"
        f"🔔 Я автоматически отправляю расписание на завтра каждый день в 18:00 МСК.\n"
        f"� Вы тможете выбрать любую дату и получить расписание на неё.\n\n"
        f"{'✅ Вы уже подписаны на рассылку!' if is_subscribed else '❌ Вы пока не подписаны.'}\n\n"
        f"Используйте кнопки ниже для управления."
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(is_subscribed)
    )
    
    logger.info(f"Пользователь {user_id} ({username}) запустил бота")


async def cmd_subscribe(message: Message):
    """Обработчик команды /subscribe"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    if db.is_subscribed(user_id):
        await message.answer(
            "✅ Вы уже подписаны на рассылку расписания!",
            reply_markup=get_main_keyboard(True)
        )
    else:
        success = db.add_user(user_id, username, first_name)
        if success:
            await message.answer(
                "🎉 Отлично! Вы подписались на рассылку расписания.\n"
                "Теперь вы будете получать уведомления о новом расписании автоматически!",
                reply_markup=get_main_keyboard(True)
            )
            logger.info(f"Пользователь {user_id} подписался")
        else:
            await message.answer(
                "❌ Произошла ошибка при подписке. Попробуйте позже.",
                reply_markup=get_main_keyboard(False)
            )


async def cmd_unsubscribe(message: Message):
    """Обработчик команды /unsubscribe"""
    user_id = message.from_user.id
    
    if not db.is_subscribed(user_id):
        await message.answer(
            "❌ Вы не подписаны на рассылку.",
            reply_markup=get_main_keyboard(False)
        )
    else:
        success = db.remove_user(user_id)
        if success:
            await message.answer(
                "😢 Вы отписались от рассылки расписания.\n"
                "Чтобы снова подписаться, нажмите кнопку 'Подписаться'.",
                reply_markup=get_main_keyboard(False)
            )
            logger.info(f"Пользователь {user_id} отписался")
        else:
            await message.answer(
                "❌ Произошла ошибка при отписке. Попробуйте позже.",
                reply_markup=get_main_keyboard(True)
            )


async def cmd_info(message: Message):
    """Обработчик команды /info"""
    info_text = (
        "ℹ️ Информация о боте:\n\n"
        "🤖 Я автоматически отправляю расписание на завтра каждый день в 18:00 МСК\n"
        "📸 Расписание берется с сайта колледжа\n"
        "🔔 Вы получите уведомление в 18:00 каждый день\n"
        "� Вы мо жете выбрать любую дату и получить расписание на неё\n\n"
        "📌 Сайт колледжа: https://lsxt.my1.ru/blog/\n\n"
        "Команды:\n"
        "/start - Главное меню\n"
        "/subscribe - Подписаться на рассылку\n"
        "/unsubscribe - Отписаться от рассылки\n"
        "/info - Информация о боте"
    )
    
    await message.answer(info_text)


async def cmd_stats(message: Message):
    """Обработчик команды /stats"""
    users_count = db.get_users_count()
    
    stats_text = (
        f"📊 Статистика бота:\n\n"
        f"👥 Всего подписчиков: {users_count}\n"
        f"🔄 Проверка обновлений: каждые 6 часов"
    )
    
    await message.answer(stats_text)


async def handle_subscribe_button(message: Message):
    """Обработчик кнопки 'Подписаться'"""
    await cmd_subscribe(message)


async def handle_unsubscribe_button(message: Message):
    """Обработчик кнопки 'Отписаться'"""
    await cmd_unsubscribe(message)


async def handle_info_button(message: Message):
    """Обработчик кнопки 'Информация'"""
    await cmd_info(message)


async def handle_get_schedule_button(message: Message):
    """Обработчик кнопки 'Расписание на завтра'"""
    import os
    from datetime import datetime, timedelta
    from parser import parser
    
    # Отправляем сообщение о загрузке
    loading_msg = await message.answer("⏳ Загружаю расписание на завтра...")
    
    try:
        # Получаем расписание на завтра
        tomorrow = datetime.now() + timedelta(days=1)
        schedule_path = await parser.get_schedule_for_date(tomorrow)
        
        if not schedule_path:
            await loading_msg.edit_text(
                f"❌ Расписание на {tomorrow.strftime('%d.%m.%Y')} пока не опубликовано.\n"
                "Попробуйте позже."
            )
            return
        
        # Редактируем сообщение
        await loading_msg.edit_text("✅ Расписание уже отправляется!")
        
        # Отправляем расписание
        photo = FSInputFile(schedule_path)
        await message.answer_photo(
            photo=photo,
            caption=f"📅 Расписание на {tomorrow.strftime('%d.%m.%Y')}"
        )
        logger.info(f"Пользователь {message.from_user.id} запросил расписание на завтра")
        
    except Exception as e:
        logger.error(f"Ошибка при отправке расписания пользователю {message.from_user.id}: {e}")
        await loading_msg.edit_text(
            "❌ Произошла ошибка при загрузке расписания.\n"
            "Попробуйте позже."
        )


async def handle_select_date_button(message: Message):
    """Обработчик кнопки 'Выбрать дату'"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from datetime import datetime, timedelta
    import calendar
    
    # Получаем текущую дату
    today = datetime.now()
    current_month = today.month
    current_year = today.year
    
    # Создаем inline клавиатуру с датами текущего месяца
    keyboard = []
    
    # Получаем количество дней в текущем месяце
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    
    # Названия месяцев на русском
    months_ru = {
        1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
        5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
        9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
    }
    
    # Дни недели
    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    
    # Добавляем даты начиная с сегодняшнего дня до конца месяца
    for day in range(today.day, days_in_month + 1):
        date = datetime(current_year, current_month, day)
        date_str = date.strftime('%d.%m.%Y')
        weekday = weekdays[date.weekday()]
        
        button_text = f"{day} {months_ru[current_month]} ({weekday})"
        callback_data = f"date_{date.strftime('%Y%m%d')}"
        
        keyboard.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
    
    # Если остались дни до конца месяца меньше 5, добавляем дни следующего месяца
    remaining_days = days_in_month - today.day + 1
    if remaining_days < 10:
        # Добавляем дни следующего месяца
        next_month = current_month + 1 if current_month < 12 else 1
        next_year = current_year if current_month < 12 else current_year + 1
        
        for day in range(1, 11):  # Добавляем 10 дней следующего месяца
            date = datetime(next_year, next_month, day)
            date_str = date.strftime('%d.%m.%Y')
            weekday = weekdays[date.weekday()]
            
            button_text = f"{day} {months_ru[next_month]} ({weekday})"
            callback_data = f"date_{date.strftime('%Y%m%d')}"
            
            keyboard.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
    
    inline_kb = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(
        "📆 Выберите дату для получения расписания:",
        reply_markup=inline_kb
    )


async def handle_stats_button(message: Message):
    """Обработчик кнопки 'Статистика'"""
    await cmd_stats(message)


async def callback_subscribe(callback: CallbackQuery):
    """Обработчик inline кнопки подписки"""
    user_id = callback.from_user.id
    username = callback.from_user.username
    first_name = callback.from_user.first_name
    
    if db.is_subscribed(user_id):
        await callback.answer("Вы уже подписаны!", show_alert=True)
    else:
        success = db.add_user(user_id, username, first_name)
        if success:
            await callback.answer("✅ Вы подписались!", show_alert=True)
            await callback.message.edit_reply_markup(reply_markup=None)
        else:
            await callback.answer("❌ Ошибка подписки", show_alert=True)


async def callback_unsubscribe(callback: CallbackQuery):
    """Обработчик inline кнопки отписки"""
    user_id = callback.from_user.id
    
    if not db.is_subscribed(user_id):
        await callback.answer("Вы не подписаны!", show_alert=True)
    else:
        success = db.remove_user(user_id)
        if success:
            await callback.answer("❌ Вы отписались!", show_alert=True)
            await callback.message.edit_reply_markup(reply_markup=None)
        else:
            await callback.answer("❌ Ошибка отписки", show_alert=True)


async def callback_date_selected(callback: CallbackQuery):
    """Обработчик выбора даты из inline клавиатуры"""
    from datetime import datetime
    from parser import parser
    
    try:
        # Извлекаем дату из callback_data (формат: date_YYYYMMDD)
        date_str = callback.data.replace('date_', '')
        selected_date = datetime.strptime(date_str, '%Y%m%d')
        
        # Отвечаем на callback
        await callback.answer(f"Загружаю расписание на {selected_date.strftime('%d.%m.%Y')}...")
        
        # Редактируем сообщение
        loading_msg = await callback.message.edit_text("⏳ Загружаю расписание...")
        
        # Получаем расписание на выбранную дату
        schedule_path = await parser.get_schedule_for_date(selected_date)
        
        if not schedule_path:
            await loading_msg.edit_text(
                f"❌ Расписание на {selected_date.strftime('%d.%m.%Y')} пока не опубликовано.\n"
                "Попробуйте выбрать другую дату."
            )
            return
        
        # Редактируем сообщение
        await loading_msg.edit_text("✅ Расписание уже отправляется!")
        
        # Отправляем расписание
        photo = FSInputFile(schedule_path)
        await callback.message.answer_photo(
            photo=photo,
            caption=f"📅 Расписание на {selected_date.strftime('%d.%m.%Y')}"
        )
        logger.info(f"Пользователь {callback.from_user.id} запросил расписание на {selected_date.strftime('%d.%m.%Y')}")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке выбора даты: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка", show_alert=True)


def register_handlers(dp: Dispatcher):
    """
    Регистрация всех обработчиков
    
    Args:
        dp: Диспетчер aiogram
    """
    # Команды
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_subscribe, Command("subscribe"))
    dp.message.register(cmd_unsubscribe, Command("unsubscribe"))
    dp.message.register(cmd_info, Command("info"))
    dp.message.register(cmd_stats, Command("stats"))
    
    # Кнопки
    dp.message.register(handle_subscribe_button, F.text == "✅ Подписаться")
    dp.message.register(handle_unsubscribe_button, F.text == "❌ Отписаться")
    dp.message.register(handle_info_button, F.text == "ℹ️ Информация")
    dp.message.register(handle_select_date_button, F.text == "� Выбрать дату")
    
    # Inline кнопки
    dp.callback_query.register(callback_subscribe, F.data == "subscribe")
    dp.callback_query.register(callback_unsubscribe, F.data == "unsubscribe")
    dp.callback_query.register(callback_date_selected, F.data.startswith("date_"))
    
    logger.info("Обработчики зарегистрированы")
