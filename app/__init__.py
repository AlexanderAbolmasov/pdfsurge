from flask import Flask
from flask_cors import CORS
from config import Config
import logging
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Создаем папку для загрузок если её нет
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Создаем папку для логов если её нет
    os.makedirs('logs', exist_ok=True)

    # Настройка CORS с более подробными параметрами
    CORS(app,
         origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5000', 'http://127.0.0.1:5000'],
         supports_credentials=True,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'])

    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )

    # Импорт и регистрация маршрутов
    from .routes import init_routes
    init_routes(app)

    return app
