import os

from scripts.check_temp import check_temperature
from scripts.check_disk import check_disk_usage
from scripts.check_memory import check_memory_usage
from scripts.check_internet import check_internet
from scripts.check_uptime import get_uptime
from scripts.check_power import get_voltage, get_throttled_status

# Лимиты
TEMP_LIMIT = float(os.getenv("TEMP_LIMIT", 70.0))
DISK_LIMIT = int(os.getenv("DISK_LIMIT", 90))
MEMORY_LIMIT = int(os.getenv("MEMORY_LIMIT", 85))

def get_status_text():
    temp = check_temperature()
    disk_alert, disk = check_disk_usage(DISK_LIMIT)
    mem_alert, mem = check_memory_usage(MEMORY_LIMIT)
    internet = check_internet()
    uptime = get_uptime()
    voltage = get_voltage()
    throttled = get_throttled_status()

    return (
        f"🌡️ Температура: {temp}°C {'⚠️' if temp > TEMP_LIMIT else '✅'}\n"
        f"💾 Диск: {disk}% {'⚠️' if disk_alert else '✅'}\n"
        f"🧠 Память: {mem}% {'⚠️' if mem_alert else '✅'}\n"
        f"📡 Интернет: {'Подключен' if internet else '❌ Нет'}\n"
        f"🕒 Аптайм: {uptime} ч\n"
        f"🔋 Напряжение: {voltage}\n"
        f"⚡️ Статус питания:\n{throttled}"
    )
