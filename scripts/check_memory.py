import psutil

def check_memory_usage(limit_percent=90):
    mem = psutil.virtual_memory()
    return mem.percent > limit_percent, mem.percent
