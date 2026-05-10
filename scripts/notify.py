import requests

def send_alert(token, chat_id, message):
    try:
        url = f"https://api.day.app/{token}/${message}"

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Ошибка Telegram: {response.status_code} — {response.text}")
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")
