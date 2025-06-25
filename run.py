from app import create_app
import logging
import os

app = create_app()

if __name__ == '__main__':
    # Настройка логирования для разработки
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Создаем необходимые директории
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('app/static/css', exist_ok=True)
    os.makedirs('app/static/js', exist_ok=True)
    os.makedirs('app/templates', exist_ok=True)

    print("=" * 50)
    print("🚀 PDF Surge - Запуск сервера")
    print("=" * 50)
    print("📁 Структура папок:")
    print("   app/")
    print("   ├── static/")
    print("   │   ├── css/style.css")
    print("   │   └── js/main.js")
    print("   ├── templates/")
    print("   │   └── index.html")
    print("   ├── __init__.py")
    print("   ├── routes.py")
    print("   ├── pdf_processor.py")
    print("   config.py")
    print("   run.py")
    print("   requirements.txt")
    print("=" * 50)
    print("🌐 Сервер запущен на: http://localhost:5001")
    print("=" * 50)

    # Запуск в режиме разработки
    app.run(debug=True, host='0.0.0.0', port=5001)