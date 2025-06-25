import os
import sys

# Добавляем текущую директорию в Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("Starting Flask application...")
print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path}")

try:
    # Попробуем разные способы импорта
    try:
        # Сначала попробуем абсолютный импорт
        from __init__ import create_app
        print("Successfully imported create_app using absolute import")
    except ImportError:
        # Если не получается, попробуем как модуль
        import __init__ as init_module
        create_app = init_module.create_app
        print("Successfully imported create_app using module import")

    # Создаем приложение
    app = create_app()
    print("Flask app created successfully")

    # Получаем порт из переменной окружения
    port = int(os.environ.get('PORT', 8000))
    print(f"Using port: {port}")

    # Запускаем приложение
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