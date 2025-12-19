# 🖥️ Pi Monitor Bot  
Мониторинг температуры и диска на Raspberry Pi с уведомлениями в Telegram.

## 🚀 Возможности  
- Проверка температуры CPU через `vcgencmd`  
- Проверка заполненности диска  
- Уведомления в Telegram при превышении лимитов  
- Логирование событий в `monitor.log`

## 📁 Структура проекта 
```
pi-monitor-bot/
├── config/secrets.env
├── scripts/
│   ├── check_temp.py
│   ├── check_disk.py
│   └── notify.py
├── logs/monitor.log
├── main.py
└── README.md
```

## ⚙️ Установка  
1. Клонируй репозиторий:  
``` bash  
git clone https://github.com/твоя-ссылка/pi-monitor-bot.git  
cd pi-monitor-bot
```

2. Установи зависимости:
```bash 
pip3 install python-dotenv requests
```
 
3. Создай файл config/secrets.env
``` env
TOKEN=твой_токен_бота  
CHAT_ID=твой_chat_id  
TEMP_LIMIT=70.0  
DISK_LIMIT=90
```  

## 🧪 Запуск

```bash
python3 main.py  
```

## ⏰ Автозапуск через cron
```bash
crontab -e  
```
Добавь строку:
``` bash
*/10 * * * * /usr/bin/python3 /home/pi/pi-monitor-bot/main.py  
```

## 📜 Лицензия
MIT
