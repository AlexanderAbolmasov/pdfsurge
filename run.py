import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from __init__ import create_app
except ImportError as e:
    print(f"Import error: {e}")
    # Альтернативный способ импорта
    import importlib.util

    spec = importlib.util.spec_from_file_location("app_module", "__init__.py")
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)
    create_app = app_module.create_app

app = create_app()

if __name__ == '__main__':
    # Получаем порт из переменной окружения
    port = int(os.environ.get('PORT', 80))
    print(f"Starting application on port {port}")

    # Запускаем приложение
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
