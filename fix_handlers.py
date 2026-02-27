with open('handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Заменяем неправильную регистрацию
content = content.replace(
    'dp.message.register(handle_select_date_button, F.text == "? Выбсрать дату")',
    'dp.message.register(handle_get_schedule_button, F.text == "📅 Расписание на завтра")\n    dp.message.register(handle_select_date_button, F.text == "📆 Выбрать дату")'
)

with open('handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Файл исправлен!")
