FROM python:3.9-slim

# Установка Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    libtesseract-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ИСПРАВЛЕНИЕ: Копируем файлы более явно
COPY *.py ./
COPY gunicorn.conf.py ./

# Копируем директорию app отдельно
COPY app/ ./app/

# ПРОВЕРКА: Размер статических файлов ПОСЛЕ копирования
RUN echo "=== Checking static files after copy ===" && \
    ls -la app/static/js/main.js && \
    wc -c app/static/js/main.js && \
    head -5 app/static/js/main.js && \
    echo "=== End check ==="

RUN mkdir -p logs uploads

# Проверяем Tesseract
RUN echo "=== Available languages ===" && \
    tesseract --list-langs

EXPOSE 8000
CMD ["gunicorn", "--config", "gunicorn.conf.py", "main:app"]
