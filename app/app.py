#!/usr/bin/env python3
import os
from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def hello():
        return jsonify({
            'message': 'Flask app is running!',
            'port': os.environ.get('PORT', 'unknown')
        })

    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting simple Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)