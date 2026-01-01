#!/usr/bin/env python3
import subprocess
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
import shutil

# === НАСТРОЙКИ ===

BACKUP_DIR = Path("/home/davidmatyushin/Documents/pi/backups")

NEXTCLOUD_CONTAINER = "nextcloud-app"
DB_CONTAINER = "nextcloud-db"
DB_USER = "nextcloud"
DB_NAME = "nextcloud"

NEXTCLOUD_VOLUME = "nextcloud_nextcloud"

RETENTION_DAYS = 2

# === ЛОГИРОВАНИЕ ===

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = BACKUP_DIR / "backup.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)


def run(cmd, check=True, capture_output=False, text=True):
    """Обёртка над subprocess.run с логированием ошибок."""
    logger.info(f"Выполняю команду: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=capture_output,
        text=text
    )
    if check and result.returncode != 0:
        logger.error(f"Команда завершилась с кодом {result.returncode}")
        if result.stdout:
            logger.error(f"STDOUT: {result.stdout.strip()}")
        if result.stderr:
            logger.error(f"STDERR: {result.stderr.strip()}")
        raise RuntimeError(f"Ошибка выполнения команды: {' '.join(cmd)}")
    return result


def maintenance_mode(on: bool):
    mode = "on" if on else "off"
    logger.info(f"Переключаю maintenance mode: {mode}")
    run([
        "docker", "exec", "-u", "www-data",
        NEXTCLOUD_CONTAINER,
        "php", "occ", "maintenance:mode", f"--{mode}"
    ])


def backup_database(backup_path: Path):
    db_backup = backup_path / "nextcloud_db.sql"
    logger.info(f"Создаю дамп базы данных в {db_backup}")
    with db_backup.open("w") as f:
        result = subprocess.run(
            ["docker", "exec", DB_CONTAINER, "pg_dump", "-U", DB_USER, DB_NAME],
            check=False,
            stdout=f,
            stderr=subprocess.PIPE,
            text=True
        )
    if result.returncode != 0:
        logger.error(f"Ошибка дампа БД: {result.stderr.strip()}")
        raise RuntimeError("Не удалось создать дамп базы данных")
    return db_backup


def backup_files(backup_path: Path):
    files_backup = backup_path / "nextcloud_files.tar.gz"
    logger.info(f"Архивирую файлы Nextcloud в {files_backup}")

    run([
        "docker", "run", "--rm",
        "-v", f"{NEXTCLOUD_VOLUME}:/data",
        "-v", f"{backup_path}:/backup",
        "alpine",
        "tar", "czf", "/backup/nextcloud_files.tar.gz", "-C", "/data", "."
    ])
    return files_backup


def rotate_backups():
    logger.info(f"Запускаю ротацию бэкапов старше {RETENTION_DAYS} дней")
    now = datetime.now()
    for entry in BACKUP_DIR.iterdir():
        if not entry.is_dir():
            continue
        # Пропускаем директории, не похожие на наши бэкапы (по имени)
        # Ожидаемый формат: YYYY-MM-DD_HH-MM-SS
        try:
            datetime.strptime(entry.name, "%Y-%m-%d_%H-%M-%S")
        except ValueError:
            continue

        mtime = datetime.fromtimestamp(entry.stat().st_mtime)
        if now - mtime > timedelta(days=RETENTION_DAYS):
            logger.info(f"Удаляю старый бэкап: {entry}")
            shutil.rmtree(entry, ignore_errors=True)


def main():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = BACKUP_DIR / timestamp
    backup_path.mkdir(parents=True, exist_ok=True)

    logger.info("=== Начало бэкапа Nextcloud ===")
    logger.info(f"Каталог бэкапа: {backup_path}")

    maintenance_enabled = False

    try:
        # 1. Maintenance mode ON
        maintenance_mode(True)
        maintenance_enabled = True

        # 2. Бэкап БД
        backup_database(backup_path)

        # 3. Бэкап файлов
        backup_files(backup_path)

        logger.info(f"Бэкап успешно завершён: {backup_path}")

    except Exception as e:
        logger.error(f"ОШИБКА при выполнении бэкапа: {e}")# Не выходим, пока не попробуем выключить maintenance
        if maintenance_enabled:
            try:
                maintenance_mode(False)
            except Exception as e2:
                logger.error(f"Доп. ошибка при выключении maintenance mode: {e2}")
        sys.exit(1)

    # 4. Maintenance mode OFF
    if maintenance_enabled:
        try:
            maintenance_mode(False)
        except Exception as e:
            logger.error(f"Ошибка при выключении maintenance mode: {e}")
            # Но сам бэкап уже сделан, не считаем это фаталом

    # 5. Ротация
    rotate_backups()

    logger.info("=== Бэкап Nextcloud завершён ===")


if __name__ == "__main__":
    main()
