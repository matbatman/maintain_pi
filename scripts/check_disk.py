import shutil

def check_disk_usage(limit_percent=90, path="/"):
    try:
        total, used, free = shutil.disk_usage(path)
        percent_used = used / total * 100
        alert = percent_used > limit_percent
        return alert, round(percent_used, 2)
    except Exception as e:
        return False, f"Ошибка при проверке диска: {e}"
