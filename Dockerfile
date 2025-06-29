FROM python:3.9-slim

# Оптимизация Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    libtesseract-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Настройка переменных окружения для оптимизации
ENV OMP_THREAD_LIMIT=2
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p logs uploads

# Проверка синтаксиса
RUN python -c "import py_compile; py_compile.compile('yandex_gpt_service.py')"

EXPOSE 8000

# Запуск с увеличенным timeout
CMD ["gunicorn", "--config", "gunicorn.conf.py", "main:app"]
