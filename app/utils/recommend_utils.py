import json
import logging
import time

import dask.dataframe as dd
import pandas as pd
from annoy import AnnoyIndex
from dask.diagnostics import ProgressBar
from flask import current_app
from flask_executor import Executor
from scipy.sparse import csr_matrix

from app.extensions import db
from app.models import Rating

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

_cached_ratings = None
_last_updated = 0
_movie_lens_to_tmdb = {}
_tmdb_to_movie_lens = {}

executor = None


def init_executor(app):
    global executor
    executor = Executor(app)


def get_movie_lens_id(tmdb_id):
    return _tmdb_to_movie_lens.get(str(tmdb_id))


def get_tmdb_id(movie_lens_id):
    return _movie_lens_to_tmdb.get(str(movie_lens_id))


def load_ratings(force_reload=False):
    global _cached_ratings, _last_updated

    if (
        not force_reload
        and _cached_ratings is not None
        and (time.time() - _last_updated) < 600
    ):
        logging.info("📊 Using cached ratings data...")
        return _cached_ratings

    logging.info("📊 Fetching rating data from DB using Dask...")

    query = "SELECT userId, movieId, rating FROM ratings"
    ratings_df = pd.read_sql(query, con=db.engine)

    ratings_df = dd.from_pandas(ratings_df, npartitions=10)

    ratings_df["userId"] = ratings_df["userId"].astype("int32")
    ratings_df["movieId"] = ratings_df["movieId"].astype("int32")
    ratings_df["rating"] = ratings_df["rating"].astype("float32")

    logging.info("🔁 Converting Dask DataFrame to Pandas DataFrame...")
    with ProgressBar():
        ratings_df = ratings_df.compute()

    _cached_ratings = ratings_df
    _last_updated = time.time()

    logging.info("📊 Ratings data loaded and cached successfully!")
    return _cached_ratings


def get_model():
    try:
        with open("popcorn_config.json", "r") as f_in:
            config = json.load(f_in)
            f = config["dimension"]
    except (FileNotFoundError, KeyError):
        logging.error("❌ Model config file not found. Please retrain the model!")
        return None

    annoy_index = AnnoyIndex(f, "angular")
    annoy_index.load("popcorn.ann")
    return annoy_index


def get_sparse_matrix(ratings_df):
    row = ratings_df["movieId"].values
    col = ratings_df["userId"].values
    data = ratings_df["rating"].values

    sparse_matrix = csr_matrix((data, (row, col)))
    return sparse_matrix


def get_collaborative_recommendations(tmdb_id, num_recommendations=5):
    with current_app.app_context():
        start_time = time.time()

        movieId = get_movie_lens_id(tmdb_id)
        if movieId is None:
            logging.warning(f"❌ No matching MovieLens ID for TMDB ID {tmdb_id}.")
            return []

        logging.info(f"✅ Matching MovieLens ID: {movieId}")
        ratings_df = load_ratings()
        if ratings_df is None:
            return []

        user_movie_matrix = ratings_df.pivot_table(
            index="movieId", columns="userId", values="rating", fill_value=0
        )
        movie_ids = set(user_movie_matrix.index.tolist())

        if movieId not in movie_ids:
            logging.warning(f"❌ Movie ID {movieId} not found in matrix.")
            return []

        model = get_model()
        if model is None:
            return []

        movie_vector = user_movie_matrix.loc[movieId].values.astype(float).tolist()
        indices = model.get_nns_by_vector(movie_vector, num_recommendations + 1)

        recommended_movie_ids = [idx for idx in indices if idx != movieId]
        recommended_tmdb_ids = [
            get_tmdb_id(mid) for mid in recommended_movie_ids if get_tmdb_id(mid)
        ]

        elapsed_time = time.time() - start_time
        logging.info(f"🎬 Recommended TMDB IDs: {recommended_tmdb_ids}")
        logging.info(
            f"⏳ Collaborative filtering işlem süresi: {elapsed_time:.2f} saniye"
        )

        return recommended_tmdb_ids[:num_recommendations]


def async_get_collaborative_recommendations(tmdb_id, num_recommendations=5):
    app = current_app._get_current_object()

    def task():
        with app.app_context():
            return get_collaborative_recommendations(tmdb_id, num_recommendations)

    future = executor.submit(task)
    try:
        return future.result(timeout=10)
    except Exception as e:
        logging.error(f"⚠️ Async collaborative filtering failed: {e}")
        return []


from tmdb_api import get_content_recommendations


def get_hybrid_recommendations(movieId, num_recommendations=10):
    with current_app.app_context():
        start_time = time.time()

        content_future = executor.submit(get_content_recommendations, movieId)
        collaborative_future = executor.submit(
            get_collaborative_recommendations, movieId, num_recommendations
        )

        content_based = content_future.result()
        collaborative_based = collaborative_future.result()

        content_ids = (
            list(map(str, content_based[:5])) if isinstance(content_based, list) else []
        )
        hybrid_list = list(set(content_ids + collaborative_based))

        elapsed_time = time.time() - start_time
        logging.info(f"Hybrid recommendations: {hybrid_list}")
        logging.info(f"⏳ Hybrid filtering işlem süresi: {elapsed_time:.2f} saniye")

        return hybrid_list[:num_recommendations]
