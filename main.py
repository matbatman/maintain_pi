import os
import time
from dotenv import load_dotenv
from scripts.check_temp import check_temperature
from scripts.check_disk import check_disk_usage
from scripts.check_memory import check_memory_usage
from scripts.check_internet import check_internet
from scripts.check_uptime import get_uptime
from scripts.check_power import get_voltage, get_throttled_status
from scripts.notify import send_alert

# Загружаем переменные окружения
load_dotenv("/home/davidmatyushin/Documents/pi/maintain_pi/config/secrets.env")

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TEMP_LIMIT = float(os.getenv("TEMP_LIMIT", 70.0))
DISK_LIMIT = int(os.getenv("DISK_LIMIT", 90))
MEMORY_LIMIT = int(os.getenv("MEMORY_LIMIT", 85))  # можно добавить в .env
LOG_PATH = "/home/davidmatyushin/Documents/pi/maintain_pi/logs/monitor.log"

def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def main():
    # Температура
    temp = check_temperature()
    if temp > TEMP_LIMIT:
        send_alert(f"🌡️ Температура {temp}°C превышает лимит {TEMP_LIMIT}°C")
    log(f"🌡️ Температура: {temp}°C")

    # Диск
    disk_alert, disk_percent = check_disk_usage(DISK_LIMIT)
    if disk_alert:
        send_alert(f"💾 Диск заполнен на {disk_percent}%")
    log(f"💾 Диск: {disk_percent}%")

    # Память
    mem_alert, mem_percent = check_memory_usage(MEMORY_LIMIT)
    if mem_alert:
        send_alert(f"🧠 Память занята на {mem_percent}%")
    log(f"🧠 Память: {mem_percent}%")

    # Интернет
    if not check_internet():
        send_alert("📡 Нет подключения к интернету")
    else:
        log("📡 Интернет подключен")

    # Аптайм
    uptime_hours = get_uptime()
    log(f"🕒 Аптайм: {uptime_hours} ч")

    # Питание
    voltage = get_voltage()
    throttled = get_throttled_status()
    log(f"🔋 Напряжение: {voltage}")
    log(f"⚡️ Статус питания:\n{throttled}")
    if "⚠️" in throttled:
        send_alert(f"🚨 Проблемы с питанием:\n{throttled}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"❌ Ошибка: {e}")
