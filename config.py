import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(
        os.path.join(os.getcwd(), "instance", "movie.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    CSV_PATH = os.getenv("CSV_PATH", "app/data")
    HTML_PATH = os.getenv("HTML_PATH", "app/templates")
    CACHE_TYPE = "filesystem"
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_DIR = "app/cache"
