# Используем официальный Python образ
FROM python:3.9-slim

# Обновляем пакеты и устанавливаем Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
COPY . .

# Создаем необходимые директории
RUN mkdir -p logs uploads

# Указываем порт
EXPOSE 8000

# Команда запуска приложения
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]
