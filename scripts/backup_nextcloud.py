#!/usr/bin/env python3
import os
import subprocess
import datetime
import logging
from pathlib import Path
import shutil
from dotenv import load_dotenv

# === БАЗОВЫЕ ПУТИ ===
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / "config" / "secrets.env")

BACKUP_DIR = Path.home() / "Documents" / "Backups" / "Nextcloud"
LOG_DIR = BASE_DIR / "logs"

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "backup_nextcloud.log"

# === НАСТРОЙКИ Nextcloud / MariaDB ===
NEXTCLOUD_CONTAINER = os.getenv("NEXTCLOUD_CONTAINER", "nextcloud-app-1")
DB_CONTAINER = os.getenv("DB_CONTAINER", "nextcloud-db-1")
DB_USER = os.getenv("DB_USER", "nextcloud")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "nextcloud")
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", 2))


# === ЛОГИРОВАНИЕ ===

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def run(cmd: list[str], check: bool = True):
    logger.info(f"RUN: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check)


def enable_maintenance():
    logger.info("Включаю maintenance mode в Nextcloud")
    run([
        "docker", "exec", "-u", "www-data", NEXTCLOUD_CONTAINER,
        "php", "/var/www/html/occ", "maintenance:mode", "--on"
    ])


def disable_maintenance():
    logger.info("Выключаю maintenance mode в Nextcloud")
    run([
        "docker", "exec", "-u", "www-data", NEXTCLOUD_CONTAINER,
        "php", "/var/www/html/occ", "maintenance:mode", "--off"
    ])


def backup_db(backup_dir: Path, timestamp: str) -> Path:
    db_file = backup_dir / f"db_{timestamp}.sql"
    logger.info(f"Делаю дамп БД в {db_file}")

    with db_file.open("wb") as f:
        proc = subprocess.Popen(
            [
                "docker", "exec", "-i", DB_CONTAINER,
                "mysqldump",
                f"-u{DB_USER}",
                f"-p{DB_PASSWORD}",
                DB_NAME,
            ],
            stdout=f
        )
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError("mysqldump завершился с ошибкой")

    return db_file


def backup_files(backup_dir: Path, timestamp: str) -> Path:
    tar_file = backup_dir / f"files_{timestamp}.tar.gz"
    logger.info(f"Архивирую файлы Nextcloud в {tar_file}")

    run([
        "docker", "exec", NEXTCLOUD_CONTAINER,
        "tar", "czf", f"/tmp/nextcloud_{timestamp}.tar.gz",
        "-C", "/var/www", "html"
    ])

    run([
        "docker", "cp",
        f"{NEXTCLOUD_CONTAINER}:/tmp/nextcloud_{timestamp}.tar.gz",
        str(tar_file)
    ])

    run([
        "docker", "exec", NEXTCLOUD_CONTAINER,
        "rm", f"/tmp/nextcloud_{timestamp}.tar.gz"
    ])

    return tar_file


def cleanup_old_backups():
    if RETENTION_DAYS <= 0:
        logger.info("RETENTION_DAYS <= 0, чистку старых бэкапов не делаю")
        return

    cutoff = datetime.datetime.now() - datetime.timedelta(days=RETENTION_DAYS)
    logger.info(f"Удаляю бэкапы старше {RETENTION_DAYS} дней (до {cutoff})")

    for item in BACKUP_DIR.iterdir():
        try:
            mtime = datetime.datetime.fromtimestamp(item.stat().st_mtime)
        except FileNotFoundError:
            continue

        if mtime < cutoff:
            logger.info(f"Удаляю старый бэкап: {item}")
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                item.unlink(missing_ok=True)


def main():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_backup_dir = BACKUP_DIR / timestamp
    current_backup_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"=== Старт бэкапа Nextcloud: {timestamp} ===")

    try:
        enable_maintenance()

        db_file = backup_db(current_backup_dir, timestamp)
        files_archive = backup_files(current_backup_dir, timestamp)

        logger.info(f"Бэкап завершён: DB={db_file}, FILES={files_archive}")

    except Exception as e:
        logger.exception(f"Ошибка при бэкапе: {e}")
    finally:
        try:
            disable_maintenance()
        except Exception as e:
            logger.exception(f"Не удалось выключить maintenance mode: {e}")

    cleanup_old_backups()
    logger.info("=== Бэкап Nextcloud завершён ===")


def backup_nextcloud():
    main()


if __name__ == "__main__":
    backup_nextcloud()
