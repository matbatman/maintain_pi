import requests
from datetime import datetime, time
import os
import sys

# Добавляем путь к notify
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scripts.notify import send_alert

ALERT_DIR = str(os.getenv("ALERT_DIR"))


def log(msg):
    try:
        with open(os.path.join(ALERT_DIR, "monitor.log"), "a") as f:
            f.write(f"[{datetime.now()}] {msg}\n")
    except:
        pass


def normalize_code(code: str) -> str:
    if not code:
        return "unknown"
    return code.split("_")[0]


def icon_for(code: str) -> str:
    code = normalize_code(code)

    if code == "clearsky":
        return "☀️"
    if code == "fair":
        return "🌤"
    if code == "partlycloudy":
        return "⛅️"
    if code == "cloudy":
        return "☁️"
    if code == "fog":
        return "🌫"

    if code in ("rainshowers", "rain"):
        return "🌧"
    if code == "heavyrain":
        return "🌧🌧"

    if code in ("snow", "lightsnow", "heavysnow"):
        return "❄️"

    if code in ("sleet", "lightsleet", "heavysleet", "sleetshowers"):
        return "🌨"

    if code == "thunderstorm":
        return "⛈"

    return "🌡"


def pick_period(data, start_h, end_h):
    """Выбираем ближайший прогноз внутри диапазона часов"""
    for entry in data:
        t = datetime.fromisoformat(entry["time"].replace("Z", "+00:00")).time()
        if time(start_h) <= t <= time(end_h):
            details = entry["data"]
            temp = details["instant"]["details"]["air_temperature"]
            cond_code = (
                details.get("next_1_hours", {})
                       .get("summary", {})
                       .get("symbol_code", "")
            )
            cond = normalize_code(cond_code)
            emoji = icon_for(cond_code)
            return f"{emoji} {temp}°, {cond}"
    return "нет данных"


def get_weather(lat, lon, city_name):
    try:
        url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
        headers = {"User-Agent": "Mozilla/5.0 (Raspberry Pi Weather Script)"}

        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()

        timeseries = data["properties"]["timeseries"]

        # Текущая погода
        now = timeseries[0]["data"]
        temp_now = now["instant"]["details"]["air_temperature"]
        wind = now["instant"]["details"]["wind_speed"]
        humidity = now["instant"]["details"]["relative_humidity"]
        pressure = now["instant"]["details"]["air_pressure_at_sea_level"]

        cond_code = (
            now.get("next_1_hours", {})
               .get("summary", {})
               .get("symbol_code", "")
        )
        cond_now = normalize_code(cond_code)
        emoji_now = icon_for(cond_code)

        # Утро / День / Вечер
        morning = pick_period(timeseries, 6, 11)
        day = pick_period(timeseries, 12, 17)
        evening = pick_period(timeseries, 18, 23)

        return (
            f"{city_name} {emoji_now}\n"
            f"Сейчас: {temp_now}°, {cond_now}\n"
            f"Ветер: {wind} м/с\n"
            f"Давление: {pressure} мм\n"
            f"Влажность: {humidity}%\n\n"
            f"🌅 Утро: {morning}\n"
            f"🌞 День: {day}\n"
            f"🌆 Вечер: {evening}\n"
        )

    except Exception as e:
        return f"{city_name}\nОшибка: {e}\n"


def send_daily_weather(token):
    log("Запуск ежедневной сводки погоды (MET Norway)")

    cities = [
        (47.2221, 39.7203, "Rostov-on-Don"),
        (47.1383, 39.7447, "Bataysk"),
        (44.7872, 20.4573, "Belgrade"),
    ]

    result = "** Ежедневная сводка погоды: **\n\n"

    for lat, lon, name in cities:
        result += get_weather(lat, lon, name) + "\n"

    send_alert(token, result)

    log("Сводка отправлена")
