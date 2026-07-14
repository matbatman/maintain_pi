import os
import time
from pathlib import Path
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

from scripts.check_temp import check_temperature
from scripts.check_disk import check_disk_usage
from scripts.check_memory import check_memory_usage
from scripts.check_internet import check_internet
from scripts.check_uptime import get_uptime
from scripts.check_power import get_voltage, get_throttled_status
from scripts.notify import send_alert
from scripts.get_status import get_status_text
from scripts.db import write_metrics


# === ПУТИ ПРОЕКТА ===
BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(exist_ok=True)

LOG_PATH = LOG_DIR / "monitor.log"


# === ЗАГРУЗКА СЕКРЕТОВ ===
load_dotenv(CONFIG_DIR / "secrets.env")

TOKEN = os.getenv("TOKEN")
TEMP_LIMIT = float(os.getenv("TEMP_LIMIT", 70.0))
DISK_LIMIT = int(os.getenv("DISK_LIMIT", 90))
MEMORY_LIMIT = int(os.getenv("MEMORY_LIMIT", 85))


# === ЛОГГЕР ===
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


# === ОСНОВНОЙ МОНИТОРИНГ ===
def main():
    # 🌡️ Температура
    temp = check_temperature()
    log(f"🌡️ Температура: {temp}°C")
    if temp > TEMP_LIMIT:
        send_alert(TOKEN, f"🌡️ Температура {temp}°C превышает лимит {TEMP_LIMIT}°C")

    # 💾 Диск
    disk_alert, disk_percent = check_disk_usage(DISK_LIMIT)
    log(f"💾 Диск: {disk_percent}%")
    if disk_alert:
        send_alert(TOKEN, f"💾 Диск заполнен на {disk_percent}%")

    # 🧠 Память
    mem_alert, mem_percent = check_memory_usage(MEMORY_LIMIT)
    log(f"🧠 Память: {mem_percent}%")
    if mem_alert:
        send_alert(TOKEN, f"🧠 Память занята на {mem_percent}%")

    # 📡 Интернет
    internet_ok = check_internet()
    if internet_ok:
        log("📡 Интернет подключен")
    else:
        send_alert(TOKEN, "📡 Нет подключения к интернету")

    # 🕒 Аптайм
    uptime_hours = get_uptime()
    log(f"🕒 Аптайм: {uptime_hours} ч")

    # 🔋 Питание
    voltage = get_voltage()
    throttled = get_throttled_status()
    log(f"🔋 Напряжение: {voltage}")
    log(f"⚡️ Статус питания:\n{throttled}")
    if "⚠️" in throttled:
        send_alert(TOKEN, f"🚨 Проблемы с питанием:\n{throttled}")

    # 📊 Общая сводка
    status_summary = get_status_text()
    log(f"📦 Сводка состояния:\n{status_summary}")

    # === ЗАПИСЬ МЕТРИК В POSTGRES ===
    try:
        write_metrics(
            temperature=temp,
            disk_percent=disk_percent,
            memory_percent=mem_percent,
            uptime_hours=uptime_hours,
            voltage=voltage,
            throttled=throttled,
            internet_ok=internet_ok,
            backup_ok=("Ошибка" not in status_summary)
        )
    except Exception as e:
        log(f"❌ Ошибка записи метрик в БД: {e}")


# === ЗАЩИТА ОТ ПАДЕНИЯ ===
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"❌ Ошибка: {e}")
        send_alert(TOKEN, f"❌ Ошибка мониторинга:\n{e}")
