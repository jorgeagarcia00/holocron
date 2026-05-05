import os
from flask import Flask
from app.extensions import db, migrate


def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object('config.DevelopmentConfig')

    os.makedirs(os.path.join(flask_app.root_path, '..', 'data'), exist_ok=True)

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)

    import app.models  # noqa: F401 — registers models with SQLAlchemy metadata

    from app.routes.main import main_bp
    from app.routes.api import api_bp
    flask_app.register_blueprint(main_bp)
    flask_app.register_blueprint(api_bp)

    from app.seeds import seed_all
    seed_all(flask_app)

    return flask_app
