from app.extensions import db
from app.models import Movie, Link, Rating
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pandas as pd
import joblib

global_ratings_df = None

def load_ratings():
    global global_ratings_df
    if global_ratings_df is None:
        print("📊 **Step 3:** Fetching rating data...")
        ratings = db.session.query(Rating.userId, Rating.movieId, Rating.rating).all()
        if not ratings:
            print("❌ No sufficient rating data found in the database.")
            return None
        print(f"✅ Retrieved {len(ratings)} ratings.")
        global_ratings_df = pd.DataFrame(ratings, columns=["userId", "movieId", "rating"])
    return global_ratings_df

def get_collaborative_recommendations(tmdb_id, num_recommendations=5):
    """
    Convert TMDB ID to MovieLens ID, apply collaborative filtering, and return recommendations as TMDB IDs.
    """
    print(f"\n🔍 **Step 1:** Finding MovieLens ID for TMDB ID {tmdb_id}...")

    movie = db.session.query(Movie).join(Link).filter(Link.tmdbId == str(tmdb_id)).first()
    
    if not movie:
        print(f"❌ No matching MovieLens ID found for TMDB ID {tmdb_id}.")
        return []

    movieId = movie.movieId  
    print(f"✅ Matching MovieLens ID: {movieId}\n") 

    ratings_df = load_ratings()
    if ratings_df is None:
        return []

    print("\n📈 **Step 5:** Creating user-movie matrix...")
    user_movie_matrix = ratings_df.pivot_table(index="userId", columns="movieId", values="rating", fill_value=0)
    print(f"✅ Matrix size: {user_movie_matrix.shape}")

    movie_ids = list(map(str, user_movie_matrix.columns.tolist()))

    if str(movieId) not in movie_ids:
        print(f"❌ Movie ID {movieId} not found in the recommendation matrix.")
        return []

    print("\n🧩 **Step 7:** Creating sparse matrix...")
    user_movie_matrix_sparse = csr_matrix(user_movie_matrix.values.T) 

    try:
        model = joblib.load('popcorn.joblib')
        print("✅ Model loaded successfully.")
    except (FileNotFoundError, Exception) as e:
        print(f"❌ Failed to load model: {e}")
        print("🔄 Training a new model...")
        model = NearestNeighbors(metric="cosine", algorithm="brute")
        model.fit(user_movie_matrix_sparse) 
        joblib.dump(model, 'popcorn.joblib')
        print("✅ New model saved.")

    print("\n🔍 **Step 9:** Finding nearest movies...")
    distances, indices = model.kneighbors(
        user_movie_matrix_sparse[movie_ids.index(str(movieId))].reshape(1, -1),
        n_neighbors=num_recommendations + 1 
    )

    recommended_movie_ids = [movie_ids[i] for i in indices.flatten()]
    recommended_movie_ids = [id for id in recommended_movie_ids if id != str(movieId)]
    print(f"🎬 **Step 10:** MovieLens recommendations: {recommended_movie_ids}")

    print("\n🔄 **Step 11:** Converting MovieLens IDs to TMDB IDs...")
    recommended_tmdb_ids = (
        db.session.query(Link.tmdbId)
        .join(Movie)
        .filter(Movie.movieId.in_(recommended_movie_ids))
        .all()
    )

    recommended_tmdb_ids = [str(tmdbId[0]) for tmdbId in recommended_tmdb_ids]
    print(f"✅ TMDB IDs: {recommended_tmdb_ids}\n")

    return recommended_tmdb_ids[:num_recommendations]


from tmdb_api import get_content_recommendations

def get_hybrid_recommendations(movieId, num_recommendations=10):
    content_based = get_content_recommendations(movieId)
    print(f"Content-based recommendations for movie {movieId}: {content_based}")

    collaborative_based = get_collaborative_recommendations(movieId, num_recommendations)
    print(f"Collaborative recommendations for movie {movieId}: {collaborative_based}")

    if isinstance(content_based, list):
        content_ids = list(map(str, content_based[:5]))
    else:
        content_ids = []
    
    hybrid_list = list(set(content_ids + collaborative_based))
    print(f"Hybrid recommendations: {hybrid_list}")
    
    return hybrid_list[:num_recommendations]