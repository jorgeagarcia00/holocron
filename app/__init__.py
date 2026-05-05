import os
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')

    os.makedirs(os.path.join(app.root_path, '..', 'data'), exist_ok=True)

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app
