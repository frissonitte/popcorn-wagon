from app import create_app
from app.utils.recommend_utils import load_ratings
from annoy import AnnoyIndex
from json import dump

def train_model():
    app = create_app()
    with app.app_context():
        ratings_df = load_ratings(force_reload=True)
        if ratings_df is None:
            print("❌ No rating data available!")
            return
    
        user_movie_matrix = ratings_df.pivot_table(index="movieId", columns="userId", values="rating", fill_value=0)

        f = user_movie_matrix.shape[1] 
        print(f"🔢 Feature dimension: {f}")

        annoy_index = AnnoyIndex(f, 'angular')

        for i, row in enumerate(user_movie_matrix.values):
            annoy_index.add_item(i, row.astype(float).tolist())

        annoy_index.build(10)
        annoy_index.save("popcorn.ann")

        with open("popcorn_config.json", "w") as f_out:
            dump({"dimension": f}, f_out)

        print("✅ Annoy model trained and saved!")

if __name__ == "__main__":
    train_model()
