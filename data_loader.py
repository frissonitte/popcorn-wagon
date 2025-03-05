from app.__init__ import create_app
from app.extensions import db
import app.models as mod
import pandas as pd
from sqlalchemy import text 
from tqdm import tqdm
import logging
import os
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = create_app()

try:
    movies = pd.read_csv(f'{Config.CSV_PATH}/movies.csv')
    ratings = pd.read_csv(f'{Config.CSV_PATH}/ratings.csv')
    tags = pd.read_csv(f'{Config.CSV_PATH}/tags.csv')
    links = pd.read_csv(f'{Config.CSV_PATH}/links.csv')
except FileNotFoundError as e:
    logging.error(f"Error reading CSV file: {e}")
    exit(1)

def enable_wal_mode():
    db.session.execute(text('PRAGMA journal_mode=WAL;'))
    db.session.commit()

def load_movielens_users():
    movielens_users = db.session.query(mod.Rating.userId).distinct().all()
    movielens_users = [user[0] for user in movielens_users]

    existing_users = set(
        userId for userId, in db.session.query(mod.User.userId).filter(
            mod.User.userId.in_(movielens_users))
    )
    existing_mappings = set(
        mapping.movielens_userId for mapping in mod.UserMapping.query.filter(
            mod.UserMapping.movielens_userId.in_(movielens_users)).all()
    )

    new_users = [
        {"userId": userId, "username": f"anonymous_{userId}", "hash": ""}
        for userId in movielens_users if userId not in existing_users
    ]
    new_mappings = [
        {"movielens_userId": userId, "system_userId": userId}
        for userId in movielens_users if userId not in existing_mappings
    ]

    db.session.bulk_insert_mappings(mod.User, new_users)
    db.session.bulk_insert_mappings(mod.UserMapping, new_mappings)
    db.session.commit()

def batch_insert(model, data, batch_size=1000):
    for i in tqdm(range(0, len(data), batch_size), desc=f"Inserting {model.__tablename__}"):
        batch = data[i:i + batch_size]
        try:
            db.session.bulk_insert_mappings(model, batch)
            db.session.commit()
        except Exception as e:
            logging.error(f"Error inserting data: {e}")
            db.session.rollback()
            
def disable_foreign_keys():
    db.session.execute(text('PRAGMA foreign_keys=OFF;'))
    db.session.commit()

def enable_foreign_keys():
    db.session.execute(text('PRAGMA foreign_keys=ON;')) 
    db.session.commit()

def load_data():
    try:
        disable_foreign_keys()

        logging.info("Loading movies...")
        batch_insert(mod.Movie, movies.to_dict(orient="records"))

        logging.info("Loading ratings...")
        batch_insert(mod.Rating, ratings.to_dict(orient="records"))

        logging.info("Loading tags...")
        tags['tag'] = tags['tag'].replace('', 'unknown').fillna('unknown')
        tags_df = tags.drop_duplicates(subset=['userId', 'movieId'])
        batch_insert(mod.Tag, tags_df.to_dict(orient="records"))

        logging.info("Loading links...")
        batch_insert(mod.Link, links.to_dict(orient="records"))

        enable_foreign_keys()
        logging.info("Data upload completed")
    except Exception as e:
        db.session.rollback()
        enable_foreign_keys()
        logging.error(f"An error occurred: {e}")

def main():
    enable_wal_mode()
    load_movielens_users()
    load_data()

if __name__ == "__main__":
    with app.app_context():
        main()