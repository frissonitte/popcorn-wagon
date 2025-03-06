from flask import Flask
from config import Config
from app.extensions import db, migrate
import app.models
from .filters import format_date

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    app.jinja_env.filters['format_date'] = format_date

    from app.routes import init_routes
    init_routes(app)

    return app
