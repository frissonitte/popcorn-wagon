import os

from app import create_app
from app.extensions import db, migrate

os.environ["FLASK_APP"] = "run.py"

app = create_app()

migrate.init_app(app, db)

if __name__ == "__main__":
    app.run(debug=True)
