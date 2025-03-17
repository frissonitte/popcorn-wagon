import gc
import logging
import os
import time

import numpy as np
from annoy import AnnoyIndex
from scipy.sparse import coo_matrix
from tqdm import tqdm

from app import create_app
from app.utils.recommend_utils import load_ratings

# Constants
DIMENSION = 330976
BATCH_SIZE = 500  # Adjust based on your memory capacity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_model():
    app = create_app()
    with app.app_context():
        # Load ratings data
        logger.info("📊 Loading ratings data...")
        ratings_df = load_ratings()
        if ratings_df is None:
            logger.error("❌ No rating data available!")
            return

        # Create sparse matrix
        logger.info("🔢 Creating sparse matrix...")
        row = ratings_df["movieId"].values
        col = ratings_df["userId"].values
        data = ratings_df["rating"].values
        sparse_matrix = coo_matrix((data, (row, col))).tocsr()

        num_movies = sparse_matrix.shape[0]
        logger.info(f"🎥 Number of movies: {num_movies}")

        # Remove old model if exists
        if os.path.exists("popcorn.ann"):
            os.remove("popcorn.ann")
            logger.info("🗑️ Old model deleted, training new model...")

        # Initialize Annoy Index
        annoy_index = AnnoyIndex(DIMENSION, "angular")

        # Add items to Annoy Index in batches
        logger.info("🏗️ Building Annoy index...")
        for i in tqdm(range(0, num_movies, 500), desc="Adding items to Annoy index"):  # BATCH_SIZE=500
            batch = sparse_matrix[i:i + 500].toarray().astype(np.float32)  # BATCH_SIZE=500
            for j, vector in enumerate(batch):
                annoy_index.add_item(i + j, vector)

        # Build and save the Annoy index
        logger.info("🔨 Building Annoy index...")
        annoy_index.build(5)  # build(5) daha hızlı model oluşturur
        annoy_index.save("popcorn.ann")

        logger.info(f"✅ Annoy model trained and saved! (dimension: {DIMENSION})")

        # Clean up
        del ratings_df, sparse_matrix
        gc.collect()


if __name__ == "__main__":
    start_time = time.time()
    train_model()
    logger.info(f"⏱️ Total execution time: {time.time() - start_time:.2f} seconds")