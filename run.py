import os
from app import app
os.environ["FLASK_APP"] = "run.py"

if __name__ == "__main__":
    app.run(debug=True)
