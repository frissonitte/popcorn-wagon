import logging
import time

import numpy as np
from annoy import AnnoyIndex
from scipy.sparse import coo_matrix
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import LabelEncoder
from tqdm import tqdm

from app.utils.recommend_utils import load_ratings

BATCH_SIZE = 500


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def prepare_data():
    ratings_df = load_ratings()
    if ratings_df is None:
        logger.error("❌ No rating data available!")
        return None, None

    movie_encoder = LabelEncoder()
    user_encoder = LabelEncoder()
    ratings_df["movieId"] = movie_encoder.fit_transform(ratings_df["movieId"])
    ratings_df["userId"] = user_encoder.fit_transform(ratings_df["userId"])

    row = ratings_df["movieId"].values
    col = ratings_df["userId"].values
    data = ratings_df["rating"].values
    return coo_matrix((data, (row, col))).tocsr(), movie_encoder


def apply_dimensionality_reduction(sparse_matrix):
    svd = TruncatedSVD(n_components=0.9)
    return svd.fit_transform(sparse_matrix)


def train_annoy_model(reduced_matrix, movie_encoder, trees=50):
    num_movies, DIMENSION = reduced_matrix.shape
    annoy_index = AnnoyIndex(DIMENSION, "angular")

    for i in tqdm(range(num_movies), desc="Adding items to Annoy index"):
        annoy_index.add_item(i, reduced_matrix[i].astype(np.float32))

    annoy_index.build(trees)
    annoy_index.save("popcorn.ann")
    return annoy_index


def main():
    start_time = time.time()

    logger.info("🔄 Preparing data...")
    sparse_matrix, movie_encoder = prepare_data()
    if sparse_matrix is None:
        return

    logger.info("🔄 Applying dimensionality reduction...")
    reduced_matrix = apply_dimensionality_reduction(sparse_matrix)

    logger.info("🔄 Training Annoy model...")
    train_annoy_model(reduced_matrix, movie_encoder)

    elapsed_time = time.time() - start_time
    logger.info(
        f"✅ Annoy model trained and saved! ({reduced_matrix.shape[0]} movies, {elapsed_time:.2f} sec)"
    )


if __name__ == "__main__":
    main()
