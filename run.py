try:
    from __init__ import create_app
except ImportError:
    # Альтернативный импорт
    import importlib.util
    spec = importlib.util.spec_from_file_location("__init__", "__init__.py")
    init_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(init_module)
    create_app = init_module.create_app

import os

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port, debug=False)