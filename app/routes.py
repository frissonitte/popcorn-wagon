from flask import Blueprint

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return  "Hello"

def init_routes(app):
    app.register_blueprint(main) 