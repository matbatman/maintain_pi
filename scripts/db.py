import psycopg2
import os
from psycopg2.extras import RealDictCursor


def write_metrics(
    temperature: float,
    disk_percent: float,
    memory_percent: float,
    uptime_hours: float,
    voltage: float,
    throttled: str,
    internet_ok: bool,
    backup_ok: bool
):
    """
    Записывает одну строку метрик в таблицу metrics.daily.
    """

    conn_str = os.getenv("PG_CONN")
    if not conn_str:
        print("❌ PG_CONN не найден в переменных окружения")
        return

    try:
        # Автоматический commit/rollback
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO metrics.daily (
                        temperature,
                        disk_percent,
                        memory_percent,
                        uptime_hours,
                        voltage,
                        throttled,
                        internet_ok,
                        backup_ok
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        temperature,
                        disk_percent,
                        memory_percent,
                        uptime_hours,
                        voltage,
                        throttled,
                        internet_ok,
                        backup_ok
                    )
                )

        print("📊 Метрики успешно записаны в PostgreSQL")

    except Exception as e:
        print(f"❌ Ошибка записи метрик в PostgreSQL: {e}")
