import os
from your_app_module import create_app  # замените на правильный путь

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
