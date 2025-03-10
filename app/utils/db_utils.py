import logging

import pandas as pd
from sqlalchemy import text
from tqdm import tqdm

import app.models as mod
from app.extensions import db
from app.models import Tag, User
from config import Config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def execute_query(query, params={}):
    return db.session.execute(query, params)


def disable_foreign_keys():
    db.session.execute(text("PRAGMA foreign_keys=OFF;"))
    db.session.commit()


def enable_foreign_keys():
    db.session.execute(text("PRAGMA foreign_keys=ON;"))
    db.session.commit()


def enable_wal_mode():
    db.session.execute(text("PRAGMA journal_mode=WAL;"))
    db.session.commit()


def chunks(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


def batch_insert(model, data, batch_size=1000):
    try:
        for i in tqdm(
            range(0, len(data), batch_size),
            desc=f"Inserting {model.__tablename__}",
            unit="row",
        ):
            batch = data[i : i + batch_size]
            db.session.bulk_insert_mappings(model, batch)
            db.session.commit()
    except Exception as e:
        logging.error(f"Error inserting data: {e}")
        db.session.rollback()


def read_csv(file_path, encoding="utf-8", sep=","):
    try:
        data = pd.read_csv(file_path, encoding=encoding, sep=sep)
        logging.info(f"Successfully read file: {file_path}")
        return data
    except FileNotFoundError as e:
        logging.error(f"Error reading CSV file {file_path}: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error reading CSV file {file_path}: {e}")
        raise


def load_csv_and_insert(model, file_path, sep=",", chunk_size=100000):
    try:
        logging.info(f"Loading {model.__tablename__}...")
        total_rows = sum(1 for _ in open(file_path, "r", encoding="utf-8")) - 1
        with tqdm(
            total=total_rows, desc=f"Processing {model.__tablename__}", unit="row"
        ) as pbar:
            for chunk in pd.read_csv(file_path, sep=sep, chunksize=chunk_size):
                if model == Tag:
                    chunk["tag"] = chunk["tag"].replace("", "unknown").fillna("unknown")
                    chunk = chunk.drop_duplicates(subset=["userId", "movieId", "tag"])
                batch_insert(model, chunk.to_dict(orient="records"))
                pbar.update(len(chunk))
    except Exception as e:
        logging.error(f"Error loading CSV file {file_path}: {e}")
        raise


def load_movielens_users():
    movielens_users = db.session.query(mod.Rating.userId).distinct().all()
    movielens_users = [user[0] for user in movielens_users]
    logging.info(f"Found {len(movielens_users)} unique users in ratings.")

    existing_users = set()
    existing_mappings = set()

    for chunk in tqdm(
        chunks(movielens_users, 1000), desc="Processing user chunks", unit="chunk"
    ):

        existing_users.update(
            userId
            for userId, in db.session.query(mod.User.userId).filter(
                mod.User.userId.in_(chunk)
            )
        )

        existing_mappings.update(
            mapping.movielens_userId
            for mapping in mod.UserMapping.query.filter(
                mod.UserMapping.movielens_userId.in_(chunk)
            ).all()
        )

    logging.info(f"Found {len(existing_users)} existing users in User table.")
    logging.info(
        f"Found {len(existing_mappings)} existing mappings in UserMapping table."
    )

    new_users = [
        {"userId": userId, "username": f"anonymous_{userId}", "hash": ""}
        for userId in movielens_users
        if userId not in existing_users
    ]
    logging.info(f"Adding {len(new_users)} new users.")

    new_mappings = [
        {"movielens_userId": userId, "system_userId": userId}
        for userId in movielens_users
        if userId not in existing_mappings
    ]
    logging.info(f"Adding {len(new_mappings)} new mappings.")

    for chunk in tqdm(chunks(new_users, 1000), desc="Inserting new users", unit="user"):
        db.session.bulk_insert_mappings(mod.User, chunk)
        db.session.commit()

    for chunk in tqdm(
        chunks(new_mappings, 1000), desc="Inserting new mappings", unit="mapping"
    ):
        db.session.bulk_insert_mappings(mod.UserMapping, chunk)
        db.session.commit()

    logging.info("Users and mappings added successfully.")


def check_users_and_mappings():
    users_count = db.session.query(mod.User).count()
    mappings_count = db.session.query(mod.UserMapping).count()
    print(f"Total users in User table: {users_count}")
    print(f"Total mappings in UserMapping table: {mappings_count}")


def load_data():
    try:
        disable_foreign_keys()
        load_csv_and_insert(mod.Movie, f"{Config.CSV_PATH}/movies.csv")
        load_csv_and_insert(mod.Rating, f"{Config.CSV_PATH}/ratings.csv")
        load_csv_and_insert(mod.Link, f"{Config.CSV_PATH}/links.csv")
        enable_foreign_keys()
        logging.info("Data upload completed")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        db.session.rollback()
        enable_foreign_keys()
