import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scripts.notify import send_alert

ALERT_DIR = "/home/davidmatyushin/Documents/pi/maintain_pi"

def log(msg):
    try:
        with open(os.path.join(ALERT_DIR, "monitor.log"), "a") as f:
            f.write(f"[{datetime.now()}] {msg}\n")
    except:
        pass

def get_weather_yandex(slug, city_name):
    url = f"https://yandex.ru/pogoda/{slug}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Температура сейчас
        temp_now = soup.select_one(".temp__value")
        temp_now = temp_now.text if temp_now else "?"

        # Описание сейчас
        cond_now = soup.select_one(".link__condition")
        cond_now = cond_now.text if cond_now else "?"

        # Прогноз на утро/день/вечер
        parts = soup.select(".forecast-briefly__day")

        summary = f"{city_name}\n"
        summary += f"Сейчас: {temp_now}°, {cond_now}\n"

        for p in parts[:3]:
            title = p.select_one(".forecast-briefly__name")
            temp = p.select_one(".temp__value")
            cond = p.select_one(".forecast-briefly__condition")

            if title and temp and cond:
                summary += f"{title.text}: {temp.text}°, {cond.text}\n"

        return summary + "\n"

    except Exception as e:
        return f"{city_name}\nОшибка парсинга: {e}\n"

def send_daily_weather(token, chat_id):
    log("Запуск ежедневной сводки погоды (Яндекс)")

    cities = [
        ("rostov-na-donu", "Rostov-on-Don"),
        ("bataysk", "Bataysk"),
        ("belgrade", "Belgrade")
    ]

    result = "Ежедневная сводка погоды:\n\n"

    for slug, name in cities:
        result += get_weather_yandex(slug, name)

    # Отправляем без Markdown, чтобы Telegram не ругался
    send_alert(token, chat_id, result)

    log("Сводка отправлена")
