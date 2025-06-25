# run.py
import os
import sys

# Добавляем текущую директорию в Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("Starting Flask application...")
print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path}")

try:
    # Импортируем create_app из __init__.py
    from __init__ import create_app

    print("Successfully imported create_app")

    # Создаем приложение
    app = create_app()
    print("Flask app created successfully")

    # Получаем порт из переменной окружения
    port = int(os.environ.get('PORT', 80))
    print(f"Using port: {port}")

    # Обязательно запускаем приложение
    print("Starting Flask server...")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True
    )

except Exception as e:
    print(f"Error starting application: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
