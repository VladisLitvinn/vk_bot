from vkbottle import Bot, Keyboard, Text, KeyboardButtonColor, EMPTY_KEYBOARD
from vkbottle.bot import Message
from datetime import datetime, timedelta
import json
import os
import asyncio
import keyboards as kb
from dotenv import load_dotenv
from themes import THEMES

load_dotenv()
os.environ['NO_PROXY'] = 'api.vk.com,api.vk.ru'
os.environ['no_proxy'] = 'api.vk.com,api.vk.ru'

# === Настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
REMINDERS_FILE = "reminders.json"

bot = Bot(BOT_TOKEN)
user_states = {}  # user_id -> {"state": "waiting_time"/"waiting_theme", "subject": "...", "minutes": ...}

def load_reminders():
    if not os.path.exists(REMINDERS_FILE):
        return {}
    try:
        with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except Exception as e:
        print(f"Ошибка загрузки reminders.json: {e}")
        return {}

def save_reminders(reminders):
    try:
        with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(reminders, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения reminders.json: {e}")

# === ОБРАБОТЧИКИ КОМАНД ===

@bot.on.message(text=["/start", "start", "Начать", "начать", "🔄 Перезапуск"])
async def start_handler(message: Message):
    """Главное меню"""
    user_id = message.from_id
    if user_id in user_states:
        del user_states[user_id]
    
    await message.answer(
        "📚 Привет! Я помогу тебе не забыть повторить важные темы.\n\n"
        "Выбери действие из меню ниже:",
        keyboard=kb.get_main_keyboard()
    )

@bot.on.message(text="➕ Создать напоминание")
async def create_reminder_handler(message: Message):
    """Начало создания напоминания - выбор предмета"""
    user_id = message.from_id
    if user_id in user_states:
        del user_states[user_id]
    
    await message.answer(
        "📚 Выбери предмет для повторения:",
        keyboard=kb.get_subjects_keyboard()
    )

@bot.on.message(text=["Математика", "Физика", "Химия", "История", "Английский", "Программирование"])
async def choose_subject_handler(message: Message):
    """Выбор предмета из списка"""
    user_id = message.from_id
    subject = message.text
    
    # Сохраняем предмет и переходим в состояние ожидания времени
    user_states[user_id] = {
        "state": "waiting_time",
        "subject": subject
    }

    await message.answer(
        f"✅ Выбран предмет: {subject}\n\n"
        "Через сколько минут напомнить о повторении?\n\n"
        "Напиши число минут (например: 5, 60, 120, 1440):\n\n"
        "💡 Примеры:\n"
        "• 5 минут - через 5 минут\n"
        "• 60 минут - через 1 час\n"
        "• 120 минут - через 2 часа\n"
        "• 1440 минут - через 1 день",
        keyboard=kb.get_cancel_keyboard()
    )

@bot.on.message(text=["/my_reminders", "мои напоминания", "напоминания", "📋 Мои напоминания"])
async def my_reminders_handler(message: Message):
    """Показать активные напоминания"""
    try:
        user_id = message.from_id
        reminders = load_reminders().get(str(user_id), [])

        if not reminders:
            await message.answer(
                "📭 У тебя пока нет активных напоминаний.\n\n"
                "Хочешь поставить новое напоминание?",
                keyboard=kb.get_main_keyboard()
            )
            return

        text = "🔔 Твои активные напоминания:\n\n"
        for i, rem in enumerate(reminders, 1):
            if "remind_time" in rem:
                remind_time = datetime.strptime(rem["remind_time"], "%Y-%m-%d %H:%M:%S")
                time_display = format_time_display(rem["minutes"])
                theme_text = f" ({rem.get('theme', 'Без темы')})" if rem.get('theme') != "Без темы" else ""
                text += f"{i}. {rem['subject']}{theme_text} — {time_display} ({remind_time.strftime('%d.%m %H:%M')})\n"
            elif "remind_date" in rem:
                # Обработка старого формата (по дням)
                remind_date = datetime.strptime(rem["remind_date"], "%Y-%m-%d")
                days = rem.get("days", 0)
                text += f"{i}. {rem['subject']} — через {days} дней ({remind_date.strftime('%d.%m.%Y')})\n"

        await message.answer(text, keyboard=kb.get_main_keyboard())
    except Exception as e:
        await message.answer("❌ Произошла ошибка при загрузке напоминаний.", keyboard=kb.get_main_keyboard())
        print(f"Ошибка при загрузке напоминаний: {e}")

@bot.on.message(text=["/help", "помощь", "help", "❓ Помощь"])
async def help_handler(message: Message):
    """Показать справку"""
    help_text = """
🤖 **Помощь по боту-напоминанию**

📝 **Основные команды:**
➕ Создать напоминание - начать установку нового напоминания
📋 Мои напоминания - посмотреть все активные напоминания
🔄 Перезапуск - вернуться в главное меню
❓ Помощь - эта справка

🎯 **Как пользоваться:**
1. Нажми "➕ Создать напоминание"
2. Выбери предмет из списка
3. Укажи через сколько МИНУТ напомнить
4. Выбери тему для повторения
5. Получай напоминание в нужное время!

⏰ **Примеры времени:**
• 5 - через 5 минут
• 30 - через 30 минут
• 60 - через 1 час
• 120 - через 2 часа
• 1440 - через 1 день

📚 **Доступные предметы:**
• Математика
• Физика  
• Химия
• История
• Английский
• Программирование
"""
    await message.answer(help_text, keyboard=kb.get_main_keyboard())

@bot.on.message(text=["✖️ Отмена", "◀️ Назад", "Отмена"])
async def cancel_handler(message: Message):
    """Обработка отмены/назад"""
    user_id = message.from_id
    if user_id in user_states:
        del user_states[user_id]
    
    text = message.text
    if text == "✖️ Отмена":
        reply = "❌ Действие отменено."
    elif text == "◀️ Назад":
        reply = "⬅️ Возврат в предыдущее меню."
    else:
        reply = "❌ Отменено."
    
    await message.answer(reply, keyboard=kb.get_main_keyboard())

@bot.on.message(text="✖️ Скрыть")
async def hide_keyboard_handler(message: Message):
    """Скрыть клавиатуру"""
    user_id = message.from_id
    if user_id in user_states:
        del user_states[user_id]
    
    await message.answer(
        "✅ Клавиатура скрыта.\n\n"
        "Напишите /start чтобы вернуть меню.",
        keyboard=EMPTY_KEYBOARD
    )

# === ОСНОВНОЙ ОБРАБОТЧИК СООБЩЕНИЙ ===

@bot.on.message()
async def handle_all_messages(message: Message):
    """Обработчик всех сообщений"""
    user_id = message.from_id
    text = message.text.strip()

    # Проверяем состояния пользователя
    current_state = user_states.get(user_id, {}).get("state")
    
    # Обработка состояния ожидания времени
    if current_state == "waiting_time":
        await handle_time_input(message, user_id, text)
        return
    
    # Обработка состояния ожидания темы
    elif current_state == "waiting_theme":
        await handle_theme_input(message, user_id, text)
        return
    
    # Если это команда, которую мы не обработали ранее
    elif text.startswith("/") and text not in ["/start", "/my_reminders", "/help"]:
        await message.answer(
            "Неизвестная команда. Напиши /start, чтобы начать работу с ботом.",
            keyboard=kb.get_main_keyboard()
        )

async def handle_time_input(message: Message, user_id: int, text: str):
    """Обработка ввода времени (минут)"""
    try:
        minutes = int(text)
        if minutes <= 0:
            raise ValueError
    except ValueError:
        await message.answer(
            "❗ Введи положительное число минут (например: 5, 60, 120).",
            keyboard=kb.get_cancel_keyboard()
        )
        return

    # Сохраняем время и переходим к выбору темы
    subject = user_states[user_id]["subject"]
    user_states[user_id] = {
        "state": "waiting_theme",
        "subject": subject,
        "minutes": minutes
    }

    # Получаем темы для выбранного предмета
    themes = THEMES.get(subject, [])
    if not themes:
        await message.answer(
            f"❌ Для предмета '{subject}' пока нет тем. Напоминание сохранено без темы.",
            keyboard=kb.get_main_keyboard()
        )
        # Сохраняем напоминание без темы
        await save_reminder(user_id, subject, minutes, "Без темы")
        if user_id in user_states:
            del user_states[user_id]
        return

    # Показываем клавиатуру с темами
    await message.answer(
        f"⏱ Напоминание через {format_time_display(minutes)}.\n\n"
        f"📖 Теперь выбери тему по {subject}:",
        keyboard=kb.get_subject_themes_keyboard(subject)
    )

async def handle_theme_input(message: Message, user_id: int, text: str):
    """Обработка выбора темы"""
    subject = user_states[user_id]["subject"]
    minutes = user_states[user_id]["minutes"]
    
    themes = THEMES.get(subject, [])
    
    # Если тема не найдена в списке
    if text not in themes and text != "Без темы":
        await message.answer(
            f"❌ Пожалуйста, выбери тему из списка для предмета '{subject}':",
            keyboard=kb.get_subject_themes_keyboard(subject)
        )
        return
    
    # Сохраняем напоминание
    theme = text if text in themes else "Без темы"
    await save_reminder(user_id, subject, minutes, theme, message)
    
    # Очищаем состояние
    if user_id in user_states:
        del user_states[user_id]

async def save_reminder(user_id: int, subject: str, minutes: int, theme: str, message: Message):
    """Сохранение напоминания в файл и планирование"""
    remind_time = datetime.now() + timedelta(minutes=minutes)
    remind_time_str = remind_time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        reminders = load_reminders()
        str_user_id = str(user_id)
        if str_user_id not in reminders:
            reminders[str_user_id] = []

        reminder_data = {
            "subject": subject,
            "theme": theme,
            "minutes": minutes,
            "remind_time": remind_time_str,
            "set_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        reminders[str_user_id].append(reminder_data)
        save_reminders(reminders)

        # Форматируем время для красивого отображения
        time_display = format_time_display(minutes)
        
        await message.answer(
            f"✅ Отлично! Я напомню тебе повторить:\n"
            f"📚 Предмет: {subject}\n"
            f"📖 Тема: {theme}\n"
            f"⏰ Через: {time_display}\n"
            f"🕐 Время напоминания: {remind_time.strftime('%d.%m %H:%M')}\n\n"
            "Ты можешь поставить ещё напоминания или посмотреть свои — нажми 📋 Мои напоминания",
            keyboard=kb.get_main_keyboard()
        )
        
        # Запускаем отдельную задачу для этого напоминания
        asyncio.create_task(schedule_reminder(user_id, subject, theme, minutes))
        
    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка при сохранении напоминания. Попробуй еще раз.",
            keyboard=kb.get_main_keyboard()
        )
        print(f"Ошибка при сохранении напоминания: {e}")

def format_time_display(minutes):
    """Форматирует время для красивого отображения"""
    if minutes < 60:
        return f"через {minutes} минут"
    elif minutes < 1440:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"через {hours} час" + ("а" if 2 <= hours <= 4 else "ов" if hours >= 5 else "")
        else:
            return f"через {hours} час {remaining_minutes} мин"
    else:
        days = minutes // 1440
        hours = (minutes % 1440) // 60
        if hours == 0:
            return f"через {days} день" + ("я" if 2 <= days <= 4 else "ей" if days >= 5 else "")
        else:
            return f"через {days} день {hours} час"

def load_conspects(filename="conspects.json"):
    """Загрузка конспектов из JSON файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки конспектов: {e}")
        return {}
    
async def schedule_reminder(user_id, subject, theme, minutes):
    """Запускает отдельную задачу для напоминания"""
    await asyncio.sleep(minutes * 60)  # Конвертируем минуты в секунды
    
    try:
        await bot.api.messages.send(
            user_id=user_id,
            message=(
                f"🔔 Напоминание!\n\n"
                f"Пора повторить: {subject}\n"
                f"Тема: {theme}\n\n"
                f"Удачи в учёбе! 💪"
            ),
            random_id=0
        )
        conspects = load_conspects()
        # Проверяем, есть ли конспект для этой темы
        if (subject in conspects and 
            theme in conspects[subject] and 
            conspects[subject][theme]):
            
            conspect = conspects[subject][theme]
            
            # Ждем 2 секунды перед отправкой конспекта
            await asyncio.sleep(2)
            
            # Отправляем конспект
            await bot.api.messages.send(
                user_id=user_id,
                message=f"📚 **Конспект:**\n\n{conspect['title']}\n\n{conspect['content']}",
                random_id=0
            )
        print(f"Отправлено напоминание пользователю {user_id}: {subject} - {theme}")
        
        # Удаляем напоминание из файла после отправки
        reminders = load_reminders()
        str_user_id = str(user_id)
        if str_user_id in reminders:
            current_time = datetime.now()
            reminders[str_user_id] = [
                rem for rem in reminders[str_user_id]
                if not (rem.get("subject") == subject and 
                       rem.get("theme") == theme and
                       rem.get("minutes") == minutes and
                       datetime.strptime(rem.get("remind_time"), "%Y-%m-%d %H:%M:%S") <= current_time)
            ]
            
            if not reminders[str_user_id]:
                del reminders[str_user_id]
                
            save_reminders(reminders)
            
    except Exception as e:
        print(f"Ошибка при отправке напоминания {user_id}: {e}")

# === ЗАПУСК БОТА ===

if __name__ == "__main__":
    print("✅ Бот запущен и готов к работе...")
    print("✅ Напиши боту в ВК: /start")
    
    # Проверяем и создаем файл reminders.json если его нет
    if not os.path.exists(REMINDERS_FILE):
        save_reminders({})
        print("✅ Создан файл reminders.json")
    
    bot.run_forever()