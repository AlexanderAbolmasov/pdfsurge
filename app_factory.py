from flask import Flask
from flask_cors import CORS
from config import Config
import logging
import os

def create_app():
    # Получаем абсолютный путь к директории с app_factory.py
    basedir = os.path.abspath(os.path.dirname(__file__))

    app = Flask(__name__,
                template_folder='app/templates',
                static_folder='app/static')
    # ИСПРАВЛЕНИЕ: Используем абсолютные пути
    app = Flask(__name__,
                template_folder=os.path.join(basedir, 'app', 'templates'),
                static_folder=os.path.join(basedir, 'app', 'static'),
                static_url_path='/static')  # ДОБАВЛЯЕМ: явный URL путь
    app.config.from_object(Config)

    # Создаем папку для загрузок если её нет
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Создаем папку для логов если её нет
    os.makedirs('logs', exist_ok=True)

    # Настройка CORS с более подробными параметрами
    CORS(app,
         origins=['*'],
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
        ])
    # ДОБАВЛЯЕМ: Отладочная информация о статических файлах
    logger = logging.getLogger(__name__)
    static_path = os.path.join(basedir, 'app', 'static')
    logger.info(f"Static folder path: {static_path}")
    logger.info(f"Static folder exists: {os.path.exists(static_path)}")

    if os.path.exists(static_path):
        js_path = os.path.join(static_path, 'js', 'main.js')
        logger.info(f"main.js exists: {os.path.exists(js_path)}")
        if os.path.exists(js_path):
            logger.info(f"main.js size: {os.path.getsize(js_path)} bytes")

    # Импорт и регистрация маршрутов
    from routes import init_routes
    init_routes(app)

    return app
