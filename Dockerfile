FROM python:3.9-slim

# Обновляем пакеты и устанавливаем Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    libtesseract-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Находим правильный путь к tessdata
RUN echo "=== Searching for tessdata files ===" && \
    find /usr -name "*.traineddata" -type f 2>/dev/null | head -10 && \
    echo "=== Checking common tessdata locations ===" && \
    ls -la /usr/share/tesseract-ocr/ 2>/dev/null || echo "No /usr/share/tesseract-ocr/" && \
    ls -la /usr/share/tessdata/ 2>/dev/null || echo "No /usr/share/tessdata/" && \
    echo "=== Tesseract version and config ===" && \
    tesseract --version && \
    tesseract --print-parameters 2>/dev/null | grep tessdata || echo "Cannot get tessdata path"

# НЕ устанавливаем TESSDATA_PREFIX - пусть Tesseract использует системные настройки
# ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5.00/tessdata/

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p logs uploads

# Проверяем доступность языков
RUN echo "=== Available languages ===" && \
    tesseract --list-langs

EXPOSE 8000
CMD ["gunicorn", "--config", "gunicorn.conf.py", "main:app"]
