import subprocess

def get_voltage():
    try:
        output = subprocess.check_output(["vcgencmd", "measure_volts"], text=True)
        return output.strip()
    except Exception:
        return "⚠️ Не удалось получить напряжение"

def get_throttled_status():
    try:
        output = subprocess.check_output(["vcgencmd", "get_throttled"], text=True)
        hex_value = output.strip().split('=')[1]
        flags = int(hex_value, 16)

        messages = []
        if flags == 0:
            messages.append("✅ Питание стабильное")
        else:
            if flags & 0x1:
                messages.append("⚠️ Было недопитание")
            if flags & 0x2:
                messages.append("⚠️ Был перегрев")
            if flags & 0x4:
                messages.append("⚠️ Сейчас недопитание")
            if flags & 0x8:
                messages.append("⚠️ Сейчас перегрев")
            if flags & 0x10000:
                messages.append("⚠️ Было ограничение по питанию")
            if flags & 0x20000:
                messages.append("⚠️ Было ограничение по температуре")
            if flags & 0x40000:
                messages.append("⚠️ Сейчас ограничение по питанию")
            if flags & 0x80000:
                messages.append("⚠️ Сейчас ограничение по температуре")

        return "\n".join(messages)

    except Exception:
        return "⚠️ Не удалось получить статус питания"
