import os

# Основные настройки
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
workers = int(os.environ.get('GUNICORN_WORKERS', 2))
worker_class = "gthread"  # Лучше для I/O операций
threads = 3

timeout = 600
graceful_timeout = 60
keepalive = 2

# Логирование
loglevel = "info"
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Безопасность и производительность
preload_app = True
max_requests = 1000
max_requests_jitter = 100
