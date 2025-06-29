FROM python:3.9-slim

# Обновляем пакеты и устанавливаем Tesseract OCR с правильными путями
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    libtesseract-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Проверяем и устанавливаем правильный TESSDATA_PREFIX
RUN find /usr -name "*.traineddata" -type f 2>/dev/null | head -5
RUN ls -la /usr/share/tesseract-ocr/*/tessdata/ || ls -la /usr/share/tessdata/

# Устанавливаем правильную переменную окружения
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5.00/tessdata/

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p logs uploads

# Проверяем доступность языков Tesseract
RUN tesseract --list-langs

EXPOSE 8000
CMD ["gunicorn", "--config", "gunicorn.conf.py", "main:app"]