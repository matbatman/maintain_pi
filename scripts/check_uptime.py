import psutil
import time

def get_uptime():
    seconds = time.time() - psutil.boot_time()
    hours = int(seconds // 3600)
    return hours
