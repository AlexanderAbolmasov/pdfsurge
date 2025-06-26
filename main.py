import os
import sys

# Добавляем текущую директорию в Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("Starting Flask application...")

try:
    from __init__ import create_app
    print("Successfully imported create_app using absolute import")


    # Создаем приложение
    app = create_app()
    print("Flask app created successfully")
   
except Exception as e:
    print(f"Error creating app: {e}")

    # Создаем fallback приложение
    from flask import Flask  
    app = Flask(__name__)    
    
    @app.route('/')
    def fallback():
        return "Fallback app"
        
    @app.route('/health')
    def health():
        return "OK"

     print("Using fallback application")

    if __name__ == "__main__":
        port = int(os.environ.get('PORT', 8000))
        print(f"Starting development server on port: {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
