import os
import sys

# Добавляем текущую директорию в Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("Starting Flask application...")
print(f"Current directory: {current_dir}")
print(f"Files in directory: {os.listdir(current_dir)}")

# Создание приложения для gunicorn (глобальная переменная)
try:
    from app_factory import create_app

    print("✓ Successfully imported create_app")
    app = create_app()
    print("✓ Flask app created successfully")
    print(f"✓ Available routes: {[rule.rule for rule in app.url_map.iter_rules()]}")
except Exception as e:
    print(f"✗ Error creating app: {e}")
    import traceback

    traceback.print_exc()

    # Fallback приложение
    from flask import Flask, jsonify

    app = Flask(__name__)


    @app.route('/')
    def fallback():
        return jsonify({
            "status": "fallback",
            "message": "Main app failed to load",
            "error": str(e)
        })


    @app.route('/health')
    def health():
        return jsonify({"status": "fallback_healthy"})

# Для прямого запуска
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting development server on port: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)