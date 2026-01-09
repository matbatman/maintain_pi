import adafruit_dht
import board
import time

dht = adafruit_dht.DHT22(board.D4)

try:
    while True:
        try:
            temp = dht.temperature
            hum = dht.humidity
            print(f"Температура: {temp}°C, Влажность: {hum}%")
        except Exception as e:
            print("Ошибка чтения:", e)
        time.sleep(2)
finally:
    dht.exit()
