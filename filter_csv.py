import pandas as pd

ratings_file = "app/data/ratings.csv"
movies_file = "app/data/movies.csv"
links_file = "app/data/links.csv"
tags_file = "app/data/tags.csv"

ratings = pd.read_csv(ratings_file)

user_counts = ratings["userId"].value_counts()
active_users = user_counts[user_counts >= 350].index

filtered_ratings = ratings[ratings["userId"].isin(active_users)]

filtered_ratings.to_csv("rename_me_to_ratings.csv", index=False)
print(f"✅ Filtrelenmiş ratings kaydedildi: {filtered_ratings.shape}")

tags = pd.read_csv(tags_file)
filtered_tags = tags[tags["userId"].isin(active_users)]

filtered_tags.to_csv("rename_me_to_tags.csv", index=False)
print(f"✅ Filtrelenmiş tags kaydedildi: {tags.shape}")
