import os

# Основные настройки
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
workers = 1
worker_class = "sync"

# Таймауты
timeout = 60
graceful_timeout = 30
keepalive = 2

# Логирование
loglevel = "info"
accesslog = "-"
errorlog = "-"
