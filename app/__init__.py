from flask import Flask

import app.models
from app.extensions import db, login_manager, migrate
from config import Config

from .utils.date_utils import register_filters


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    register_filters(app)
    login_manager.init_app(app)

    from app.routes import init_routes

    init_routes(app)

    from app.auth import auth

    app.register_blueprint(auth)

    return app
