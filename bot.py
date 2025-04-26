import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Вставь сюда свой токен бота
API_TOKEN = '7108172193:AAHiG9HxVytQS25FRCAScizjkVoOSEefamM'
YOUR_CHAT_ID = 363832515  # <-- Подставь сюда свой настоящий chat_id

# Включаем логирование
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# Список напоминаний
reminders = [
    {"time": "09:30", "message": "Время для занятия по английскому!"},
    {"time": "11:00", "message": "Пора выложить первый пост дня!"},
    {"time": "16:30", "message": "Не забывай про второе занятие по английскому!"},
    {"time": "17:00", "message": "Пора выложить второй пост дня!"},
    {"time": "21:00", "message": "Последнее занятие по английскому на сегодня!"},
    {"time": "21:30", "message": "Пора выложить третий пост дня!"}
]

# Функция отправки напоминаний
async def send_reminder(chat_id, message):
    await bot.send_message(chat_id, message)

# Планирование всех напоминаний
def schedule_reminders():
    scheduler.remove_all_jobs()
    for reminder in reminders:
        hour, minute = map(int, reminder["time"].split(":"))
        scheduler.add_job(
            send_reminder,
            CronTrigger(hour=hour, minute=minute),
            args=[YOUR_CHAT_ID, reminder["message"]]
        )

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я твой напоминатель.\n"
        "Команды:\n"
        "/list_reminders — Показать напоминания\n"
        "/add_reminder ЧЧ:ММ текст — Добавить напоминание\n"
        "/delete_reminder Номер — Удалить напоминание\n"
        "/get_id — Узнать свой chat_id"
    )

# Команда /get_id
@dp.message(Command("get_id"))
async def get_id(message: Message):
    await message.answer(f"Ваш chat_id: {message.chat.id}")

# Команда /list_reminders
@dp.message(Command("list_reminders"))
async def list_reminders(message: Message):
    if not reminders:
        await message.answer("Нет установленных напоминаний.")
    else:
        text = "\n".join([f"{i+1}. {r['time']} — {r['message']}" for i, r in enumerate(reminders)])
        await message.answer(f"Ваши напоминания:\n{text}")

# Команда /add_reminder
@dp.message(Command("add_reminder"))
async def add_reminder(message: Message):
    try:
        text = message.text.split(maxsplit=2)
        if len(text) < 3:
            raise ValueError
        time_part = text[1]
        msg_part = text[2]
        if ":" not in time_part:
            raise ValueError
        reminders.append({"time": time_part, "message": msg_part})
        schedule_reminders()
        await message.answer(f"Добавлено новое напоминание: {time_part} — {msg_part}")
    except Exception as e:
        await message.answer("Ошибка! Используй формат: /add_reminder ЧЧ:ММ Текст")

# Команда /delete_reminder
@dp.message(Command("delete_reminder"))
async def delete_reminder(message: Message):
    try:
        index = int(message.text.split()[1]) - 1
        if 0 <= index < len(reminders):
            removed = reminders.pop(index)
            schedule_reminders()
            await message.answer(f"Удалено напоминание: {removed['time']} — {removed['message']}")
        else:
            await message.answer("Неверный номер напоминания.")
    except Exception:
        await message.answer("Ошибка! Используй формат: /delete_reminder Номер")

# Запуск бота
async def main():
    schedule_reminders()
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())