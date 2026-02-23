import os
import time
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# -----------------------------
# Загрузка окружения
# -----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "config", "secrets.env")

load_dotenv(ENV_PATH)

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

LOG_PATH = os.path.join(BASE_DIR, "logs", "monitor.log")

# -----------------------------
# Логгер
# -----------------------------

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

# -----------------------------
# Импорт твоих функций
# -----------------------------

from scripts.get_status import get_status_text
from scripts.check_weather import send_daily_weather

# -----------------------------
# Команды Telegram
# -----------------------------

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /weather — отправляет прогноз погоды."""
    send_daily_weather(TOKEN, CHAT_ID)
    await update.message.reply_text("Погода отправлена в личку")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status — сводка состояния системы."""
    status_summary = get_status_text()
    log(f"📦 Сводка по запросу из Telegram:\n{status_summary}")
    await update.message.reply_text(status_summary)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен и готов работать")

# -----------------------------
# Запуск бота
# -----------------------------

def run_bot():
    if not TOKEN:
        raise RuntimeError("❌ TOKEN не найден в окружении")

    print("✅ Telegram-бот запущен и ждёт команды...")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("weather", weather_command))

    app.run_polling()

if __name__ == "__main__":
    run_bot()
