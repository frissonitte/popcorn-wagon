import gc
import json
import logging
import os
import time

import joblib
import numpy as np
from annoy import AnnoyIndex
from scipy.sparse import coo_matrix
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from tqdm import tqdm

from app.__init__ import create_app
from app.utils.recommend_utils import load_ratings

BATCH_SIZE = 500
ANNOY_TREES = 75
ANNOY_FILE = "popcorn.ann"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def prepare_data():
    try:
        ratings_df = load_ratings()
    except Exception as e:
        logger.exception(f"❌ Failed to load ratings data: {e}")
        return None, None, None

    if ratings_df is None or ratings_df.empty:
        logger.error("❌ No rating data available!")
        return None, None, None

    # Check for NaN or infinite values
    if ratings_df.isnull().values.any() or np.isinf(ratings_df.values).any():
        logger.error("❌ Ratings data contains NaN or infinite values!")
        return None, None, None

    # Map movie and user IDs to sequential indices
    movie_ids = ratings_df["movieId"].unique()
    movie_map = {id_: i for i, id_ in enumerate(movie_ids)}
    ratings_df["movieId"] = ratings_df["movieId"].map(movie_map)

    user_ids = ratings_df["userId"].unique()
    user_map = {id_: i for i, id_ in enumerate(user_ids)}
    ratings_df["userId"] = ratings_df["userId"].map(user_map)

    # Extract row, col, and data as 1D arrays
    row = ratings_df["movieId"].values.astype(int)  # Ensure integer type
    col = ratings_df["userId"].values.astype(int)  # Ensure integer type
    data = ratings_df["rating"].values.astype(float)  # Ensure float type

    # Log the shapes of row, col, and data
    logger.info(
        f"Row shape: {row.shape}, Col shape: {col.shape}, Data shape: {data.shape}"
    )

    # Create the sparse matrix
    try:
        sparse_matrix = coo_matrix((data, (row, col)), dtype=np.float32)
        logger.info(f"Sparse matrix shape: {sparse_matrix.shape}")
    except Exception as e:
        logger.error(f"❌ Failed to create sparse matrix: {e}")
        return None, None, None

    return sparse_matrix, movie_map, len(user_ids)


def apply_dimensionality_reduction(sparse_matrix, max_dimension):
    """Apply SVD with the manually configured dimension."""
    # Normalize the matrix
    normalizer = Normalizer()
    normalized_matrix = normalizer.fit_transform(sparse_matrix)

    # Check for NaN or infinite values after normalization
    if np.isnan(normalized_matrix.data).any() or np.isinf(normalized_matrix.data).any():
        logger.error("❌ Normalized matrix contains NaN or infinite values!")
        return None

    target_variance = 0.85
    svd = TruncatedSVD(
        n_components=max_dimension, algorithm="randomized", random_state=42
    )
    svd.fit(normalized_matrix)

    cumulative_variance = np.cumsum(svd.explained_variance_ratio_)
    new_dimension = np.argmax(cumulative_variance >= target_variance) + 1

    logger.info(
        f"🔍 New SVD dimension for {target_variance * 100}% variance retained: {new_dimension}"
    )

    # Apply SVD to the entire matrix
    svd = TruncatedSVD(
        n_components=new_dimension, algorithm="randomized", random_state=42
    )
    reduced_matrix = svd.fit_transform(normalized_matrix)

    # Save the normalizer and SVD models
    joblib.dump(normalizer, "normalizer.pkl")
    joblib.dump(svd, "svd.pkl")

    # Log the variance retained
    variance_retained = np.sum(svd.explained_variance_ratio_)
    data_loss = 1 - variance_retained
    logger.info(f"🔍 Using SVD Components: {new_dimension}")
    import json

    config = {"dimension": int(new_dimension)}
    with open("popcorn_config.json", "w") as f:
        json.dump(config, f)
    logger.info(
        f"📊 Variance Retained: {variance_retained:.2f}, Data Loss: {data_loss:.2%}"
    )
    logger.info(f"📦 Reduced matrix shape: {reduced_matrix.shape}")
    return reduced_matrix


def train_annoy_model(reduced_matrix, movie_map):
    """Train the Annoy model with the reduced matrix."""
    num_movies, dimension = reduced_matrix.shape
    annoy_index = AnnoyIndex(dimension, "angular")

    if os.path.exists(ANNOY_FILE):
        temp_index = AnnoyIndex(dimension, "angular")
        temp_index.load(ANNOY_FILE)
        if temp_index.get_n_items() > 0 and temp_index.f == dimension:
            annoy_index = temp_index
            logger.info("♻️ Loaded existing Annoy model for updates...")
        else:
            logger.warning("⚠️ Annoy index dimension mismatch! Recreating index...")
            os.remove(ANNOY_FILE)

    for i in tqdm(range(num_movies), desc="Adding items to Annoy index"):
        annoy_index.add_item(i, reduced_matrix[i].astype(np.float32))

    annoy_index.build(ANNOY_TREES, n_jobs=-1)
    annoy_index.save(ANNOY_FILE)
    return annoy_index


def main():
    start_time = time.time()

    logger.info("🔄 Preparing data...")
    sparse_matrix, movie_map, num_users = prepare_data()
    if sparse_matrix is None:
        return

    max_dimension = num_users

    logger.info("🔄 Applying dimensionality reduction...")
    reduced_matrix = apply_dimensionality_reduction(sparse_matrix, max_dimension)
    if reduced_matrix is None:
        return

    logger.info("🔄 Training Annoy model...")
    train_annoy_model(reduced_matrix, movie_map)

    gc.collect()

    elapsed_time = time.time() - start_time
    logger.info(
        f"✅ Annoy model trained and saved! ({reduced_matrix.shape[0]} movies, {elapsed_time:.2f} sec)"
    )


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        main()
