from vkbottle import Keyboard, Text, KeyboardButtonColor
from themes import THEMES

def get_main_keyboard():
    """Основная клавиатура с главным меню"""
    keyboard = Keyboard(one_time=True)
    
    # Первый ряд - создание напоминания
    keyboard.add(Text("➕ Создать напоминание"), color=KeyboardButtonColor.POSITIVE)
    keyboard.row()
    
    # Второй ряд - просмотр напоминаний и помощь
    keyboard.add(Text("📋 Мои напоминания"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("❓ Помощь"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    
    # Третий ряд - перезапуск и скрытие
    keyboard.add(Text("🔄 Перезапуск"), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Text("✖️ Скрыть"), color=KeyboardButtonColor.NEGATIVE)
    
    return keyboard

def get_subjects_keyboard():
    """Клавиатура для выбора предмета"""
    keyboard = Keyboard(one_time=True)
    
    # Первый ряд
    keyboard.add(Text("Математика"))
    keyboard.add(Text("Физика"))
    keyboard.row()
    
    # Второй ряд
    keyboard.add(Text("Химия"))
    keyboard.add(Text("История"))
    keyboard.row()
    
    # Третий ряд
    keyboard.add(Text("Английский"))
    keyboard.add(Text("Программирование"))
    keyboard.row()
    
    # Навигация
    keyboard.add(Text("◀️ Назад"), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Text("✖️ Отмена"), color=KeyboardButtonColor.NEGATIVE)
    
    return keyboard

def get_cancel_keyboard():
    """Простая клавиатура только с отменой"""
    keyboard = Keyboard(one_time=True)
    keyboard.add(Text("✖️ Отмена"), color=KeyboardButtonColor.NEGATIVE)
    return keyboard

def get_subject_themes_keyboard(subject: str):
    """Клавиатура с темами для конкретного предмета"""
    keyboard = Keyboard(one_time=True)
    
    # Получаем темы для предмета
    themes = THEMES.get(subject, [])
    
    # Добавляем темы (по 2 в ряд)
    for i in range(0, len(themes), 2):
        if i + 1 < len(themes):
            keyboard.add(Text(themes[i]))
            keyboard.add(Text(themes[i + 1]))
        else:
            keyboard.add(Text(themes[i]))
        
        if i + 2 < len(themes):
            keyboard.row()
    
    # Кнопка "Без темы" и навигация
    keyboard.row()
    keyboard.add(Text("Без темы"), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    keyboard.add(Text("◀️ Назад"), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Text("✖️ Отмена"), color=KeyboardButtonColor.NEGATIVE)
    
    return keyboard