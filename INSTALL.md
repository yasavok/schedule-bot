# Инструкция по установке и запуску

## Быстрый старт

### Шаг 1: Установка Python

Убедитесь, что у вас установлен Python 3.8 или выше:

```bash
python --version
```

Если Python не установлен, скачайте его с [python.org](https://www.python.org/downloads/)

### Шаг 2: Создание виртуального окружения (рекомендуется)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 4: Создание бота в Telegram

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Введите имя бота (например: "Расписание ЛГКТ")
4. Введите username бота (должен заканчиваться на "bot", например: "lsxt_schedule_bot")
5. Скопируйте полученный токен

### Шаг 5: Настройка конфигурации

Создайте файл `.env` в корне проекта:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Откройте `.env` в текстовом редакторе и вставьте токен:

```
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Шаг 6: Запуск бота

```bash
python bot.py
```

Вы должны увидеть сообщение:

```
INFO - Бот запущен
INFO - Обработчики зарегистрированы
INFO - Запуск планировщика проверки расписания
```

### Шаг 7: Тестирование

1. Найдите вашего бота в Telegram по username
2. Отправьте команду `/start`
3. Нажмите кнопку "✅ Подписаться"
4. Бот добавит вас в базу подписчиков

## Настройка интервала проверки

По умолчанию бот проверяет обновления каждые 6 часов. Чтобы изменить это:

1. Откройте файл `config.py`
2. Найдите строку `CHECK_INTERVAL = 21600`
3. Измените значение:
   - 1 час = 3600
   - 6 часов = 21600
   - 12 часов = 43200
   - 1 день = 86400

Пример для проверки каждый час:

```python
CHECK_INTERVAL = 3600  # 1 час
```

## Запуск в фоновом режиме

### Windows

Используйте планировщик задач или запустите в отдельном окне PowerShell.

### Linux (systemd)

Создайте файл `/etc/systemd/system/schedule-bot.service`:

```ini
[Unit]
Description=Schedule Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/bot
ExecStart=/path/to/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Запустите сервис:

```bash
sudo systemctl enable schedule-bot
sudo systemctl start schedule-bot
sudo systemctl status schedule-bot
```

### Linux (screen/tmux)

```bash
# Используя screen
screen -S schedule-bot
python bot.py
# Нажмите Ctrl+A, затем D для отсоединения

# Используя tmux
tmux new -s schedule-bot
python bot.py
# Нажмите Ctrl+B, затем D для отсоединения
```

## Проверка логов

Логи сохраняются в файл `bot.log`:

```bash
# Просмотр последних строк
tail -f bot.log

# Windows
type bot.log
```

## Устранение проблем

### Бот не запускается

1. Проверьте токен в `.env`
2. Убедитесь, что установлены все зависимости: `pip install -r requirements.txt`
3. Проверьте версию Python: `python --version` (должна быть 3.8+)

### Бот не находит расписание

1. Проверьте доступность сайта: https://lsxt.my1.ru/blog/
2. Посмотрите логи в `bot.log`
3. Возможно, структура сайта изменилась - нужно обновить парсер

### Ошибка "Invalid token"

Токен в `.env` неверный. Получите новый токен у @BotFather.

### База данных не создается

Проверьте права на запись в текущей директории.

## Обновление бота

```bash
# Остановите бота (Ctrl+C)
git pull  # если используете git
pip install -r requirements.txt --upgrade
python bot.py
```

## Резервное копирование

Важные файлы для резервного копирования:

- `database.db` - база данных пользователей
- `.env` - конфигурация
- `schedules/` - сохраненные расписания
- `last_schedule_hash.txt` - хэш последнего расписания

```bash
# Создание резервной копии
tar -czf backup_$(date +%Y%m%d).tar.gz database.db .env schedules/ last_schedule_hash.txt
```

## Контакты

При возникновении проблем создайте issue в репозитории проекта.
