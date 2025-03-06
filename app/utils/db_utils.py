from app.extensions import db
from app.models import User

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def execute_query(query, params={}):
    return db.session.execute(query, params)