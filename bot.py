import os
import time
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

from scripts.get_status import get_status_text
from scripts.check_rain import get_rain_status

# 🔐 Загружаем переменные окружения
load_dotenv("/home/davidmatyushin/Documents/pi/maintain_pi/config/secrets.env")

TOKEN = os.getenv("TOKEN")
LOG_PATH = "/home/davidmatyushin/Documents/pi/maintain_pi/logs/monitor.log"

# 📝 Логгер
def log(message, path=LOG_PATH, max_lines=1000):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"

    try:
        with open(path, "a") as f:
            f.write(entry)

        with open(path, "r") as f:
            lines = f.readlines()

        if len(lines) > max_lines:
            with open(path, "w") as f:
                f.writelines(lines[-max_lines:])
    except Exception as e:
        print(f"⚠️ Ошибка логгера: {e}")

# 🌦️ Команда /weather
async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cities = ["Rostov-on-Don", "Bataysk"]
    status_list = [get_rain_status(city) for city in cities]
    summary = "\n".join(status_list)
    log(f"🌦️ Прогноз по запросу из Telegram:\n{summary}")
    await update.message.reply_text(f"🌦️ Прогноз погоды:\n{summary}")

# 📡 Команда /status
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_summary = get_status_text()
    log(f"📦 Сводка по запросу из Telegram:\n{status_summary}")
    await update.message.reply_text(status_summary)


# 🚀 Запуск Telegram-бота
def run_bot():
    print("✅ Telegram-бот запущен и ждёт команды...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("weather", weather_command))
    app.run_polling()

if __name__ == "__main__":
    run_bot()

