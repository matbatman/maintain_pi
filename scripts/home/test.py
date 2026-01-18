import os
from yandex_lights import YandexSmartHome
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("HOME_TOKEN")
y = YandexSmartHome(token)

devices = y.get_devices()
for d in devices:
    print(d["id"], d["name"], d["type"])
