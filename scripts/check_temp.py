import subprocess

def check_temperature():
    try:
        result = subprocess.run(
            ["vcgencmd", "measure_temp"],
            capture_output=True,
            text=True
        )
        output = result.stdout.strip()  # Пример: temp=52.3'C
        temp_str = output.replace("temp=", "").replace("'C", "")
        return float(temp_str)
    except Exception as e:
        print(f"Ошибка при получении температуры: {e}")
        return -1
