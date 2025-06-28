from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return {"message": "Hello from PDF Surge!", "port": os.environ.get('PORT', '8000')}

@app.route('/health')
def health():
    return {"status": "OK"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting on port {port}")
    app.run(host='0.0.0.0', port=port)