import asyncio
import json
import logging
import os
import time
from typing import List

import dask.dataframe as dd
import joblib
import pandas as pd
from annoy import AnnoyIndex
from dask.diagnostics import ProgressBar
from flask import current_app
from flask_executor import Executor
from scipy.sparse import csr_matrix

from app.extensions import db
from app.models import Movie

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
_cached_ratings = None
_last_updated = 0

executor = None


def init_executor(app):
    global executor
    executor = Executor(app)


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

        if "dimension" not in config:
            logging.error("❌ 'dimension' key not found in the config file!")
            return None

        f = config["dimension"]

    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"❌ Error loading config file: {e}")
        return None

    if not os.path.exists("popcorn.ann"):
        logging.error("❌ Annoy index file 'popcorn.ann' not found!")
        return None

    try:
        annoy_index = AnnoyIndex(f, "angular")
        annoy_index.load("popcorn.ann")
        return annoy_index
    except Exception as e:
        logging.error(f"❌ Error loading Annoy index: {e}")
        return None


def get_sparse_matrix(ratings_df):
    row = ratings_df["movieId"].values
    col = ratings_df["userId"].values
    data = ratings_df["rating"].values

    sparse_matrix = csr_matrix((data, (row, col)))
    return sparse_matrix


def get_collaborative_recommendations(tmdb_id, num_recommendations=5):
    with current_app.app_context():
        start_time = time.time()

        # Fetch the movie by TMDB ID
        movie = db.session.query(Movie).filter_by(tmdbId=tmdb_id).first()
        if movie is None:
            logging.warning(f"❌ TMDB ID {tmdb_id} için eşleşen movieId bulunamadı.")
            return []

        movieId = movie.movieId
        logging.info(f"✅ TMDB ID {tmdb_id} için eşleşen Movie ID: {movieId}")

        # Load ratings data
        ratings_df = load_ratings()
        if ratings_df is None:
            return []

        # Create the user-movie matrix
        user_movie_matrix = ratings_df.pivot_table(
            index="movieId", columns="userId", values="rating", fill_value=0
        )
        movie_ids = set(user_movie_matrix.index.tolist())

        # Check if the movie exists in the matrix
        if movieId not in movie_ids:
            logging.warning(f"❌ Movie ID {movieId} rating matrisinde bulunamadı.")
            return []

        # Load the Annoy model
        model = get_model()
        if model is None:
            return []

        # Get the movie vector from the user-movie matrix
        movie_vector = user_movie_matrix.loc[movieId].values.astype(float)

        # Load the SVD and normalizer models
        try:
            normalizer = joblib.load("normalizer.pkl")
            svd = joblib.load("svd.pkl")
        except Exception as e:
            logging.error(f"❌ Error loading SVD or normalizer models: {e}")
            return []

        # Normalize and transform the movie vector using SVD
        movie_vector_normalized = normalizer.transform([movie_vector])
        movie_vector_reduced = svd.transform(movie_vector_normalized)

        # Query the Annoy model
        indices = model.get_nns_by_vector(
            movie_vector_reduced[0], num_recommendations + 1
        )

        # Filter out the queried movie ID
        recommended_movie_ids = [idx for idx in indices if idx != movieId]

        # Map recommended movie IDs to TMDB IDs
        recommended_tmdb_ids = [
            movie.tmdbId
            for movie in db.session.query(Movie)
            .filter(Movie.movieId.in_(recommended_movie_ids))
            .all()
        ]

        elapsed_time = time.time() - start_time
        logging.info(f"🎬 Önerilen TMDB ID'leri: {recommended_tmdb_ids}")
        logging.info(
            f"⏳ Collaborative filtering işlem süresi: {elapsed_time:.2f} saniye"
        )

        return recommended_tmdb_ids[:num_recommendations]


async def async_get_collaborative_recommendations(
    tmdb_id: int, num_recommendations: int = 5
) -> List[int]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, get_collaborative_recommendations, tmdb_id, num_recommendations
    )


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
