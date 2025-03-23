import pandas as pd

# File paths
ratings_file = "app/data/ratings.csv"
tags_file = "app/data/tags.csv"
links_file = "app/data/links.csv"

# Threshold values
ACTIVE_USER_THRESHOLD = 750


def filter_active_users():
    """Filters out inactive users and movies that these users have not interacted with."""

    # Load ratings data
    print("📊 Loading ratings data...")
    ratings = pd.read_csv(ratings_file)

    # Identify active users
    user_counts = ratings["userId"].value_counts()
    active_users = user_counts[user_counts >= ACTIVE_USER_THRESHOLD].index
    print(f"🟢 Total number of active users: {len(active_users)}")

    # Identify movies that active users are interacting with
    active_movies = ratings[ratings["userId"].isin(active_users)]["movieId"].unique()
    print(
        f"🎥 Number of movies that active users interacted with: {len(active_movies)}"
    )

    # Get ratings data of active users only
    filtered_ratings = ratings[ratings["userId"].isin(active_users)]
    filtered_ratings.to_csv("app/data/ratings.csv", index=False)
    print(f"✅ Filtered ratings saved: {filtered_ratings.shape}")

    # Load tags data and get movies tagged by active users
    print("📂 Loading tags data...")
    tags = pd.read_csv(tags_file)
    filtered_tags = tags[tags["userId"].isin(active_users)]
    filtered_tags.to_csv("app/data/tags.csv", index=False)
    print(f"✅ Filtered tags saved: {filtered_tags.shape}")

    # Upload links file and get movies that active users are interacting with
    print("📂 Loading links data...")
    links = pd.read_csv(links_file)
    filtered_links = links[links["movieId"].isin(active_movies)]
    filtered_links.to_csv("app/data/links.csv", index=False)
    print(f"✅ Filtered links saved: {filtered_links.shape}")


if __name__ == "__main__":
    filter_active_users()
