from flask import Flask
from flask_executor import Executor

from app.extensions import cache, db, login_manager, migrate
from app.utils.recommend_utils import init_executor
from config import Config

from .utils.date_utils import register_filters


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    register_filters(app)
    login_manager.init_app(app)
    cache.init_app(app)

    executor = Executor(app)
    init_executor(app)

    from app.routes import init_routes

    init_routes(app)

    from app.auth import auth

    app.register_blueprint(auth)

    return app
