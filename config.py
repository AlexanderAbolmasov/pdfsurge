import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 50 * 1024 * 1024)

    # Yandex GPT API настройки
    YANDEX_API_KEY = os.environ.get('YANDEX_GPT_API_KEY', 'your_yandex_api_key_here')
    YANDEX_FOLDER_ID = os.environ.get('YANDEX_FOLDER_ID', 'your_folder_id_here')

    # Разрешенные расширения файлов
    ALLOWED_EXTENSIONS = {'pdf'}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
