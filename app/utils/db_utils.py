from app.extensions import db
from app.models import User
from sqlalchemy import text 

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def execute_query(query, params={}):
    return db.session.execute(query, params)

def disable_foreign_keys():
    db.session.execute(text('PRAGMA foreign_keys=OFF;'))
    db.session.commit()

def enable_foreign_keys():
    db.session.execute(text('PRAGMA foreign_keys=ON;')) 
    db.session.commit()

def enable_wal_mode():
    db.session.execute(text('PRAGMA journal_mode=WAL;'))
    db.session.commit()

def chunks(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]