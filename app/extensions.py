from flask_caching import Cache
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

cache = Cache()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
