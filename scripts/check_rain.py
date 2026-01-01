from datetime import datetime, timedelta
import os
import requests
from scripts.notify import send_alert

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
RAIN_ALERT_INTERVAL_HOURS = 6
ALERT_DIR = "/home/davidmatyushin/Documents/pi/maintain_pi"

def log(message):
    try:
        with open(os.path.join(ALERT_DIR, "monitor.log"), "a") as f:
            f.write(f"[{datetime.now()}] {message}\n")
    except Exception as e:
        print(f"Ошибка логирования: {e}")

def check_rain_forecast_multiple(cities, token, chat_id):
    for city in cities:
        try:
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={city},RU&appid={WEATHER_API_KEY}&units=metric&lang=ru"
            response = requests.get(url).json()

            rain_expected = any("Rain" in f["weather"][0]["main"] for f in response.get("list", [])[:8])
            now = datetime.now()
            flag_path = os.path.join(ALERT_DIR, f"rain_alert_{city}.txt")

            if rain_expected:
                if os.path.exists(flag_path):
                    try:
                        with open(flag_path, "r") as f:
                            last_alert_time = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")
                        if now - last_alert_time < timedelta(hours=RAIN_ALERT_INTERVAL_HOURS):
                            log(f"🌧️ [{city}] Уже предупрежден ({last_alert_time}) — пропускаем")
                            continue
                    except Exception as e:
                        log(f"⚠️ [{city}] Ошибка чтения таймштампа: {e}")

                log(f"🌧️ [{city}] Ожидается дождь — отправляем уведомление")
                send_alert(token, chat_id, f"🌧️ [{city}] Ожидается дождь! Не забудь зонт ☂️")
                with open(flag_path, "w") as f:
                    f.write(now.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                log(f"☀️ [{city}] Дождя не ожидается")
        except Exception as e:
            log(f"⚠️ [{city}] Ошибка прогноза погоды: {e}")

def get_rain_status(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city},RU&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(url).json()
        rain_expected = any("Rain" in f["weather"][0]["main"] for f in response.get("list", [])[:8])
        return f"🌧️ В {city} {'ожидается дождь' if rain_expected else 'дождя не ожидается'}"
    except Exception as e:
        return f"⚠️ Ошибка прогноза для {city}: {e}"
