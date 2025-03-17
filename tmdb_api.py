import os
import random

import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
access_token = os.getenv("ACCESS_TOKEN")

BASE_URL = "https://api.themoviedb.org/3"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json;charset=utf-8",
}


def fetch_from_tmdb(endpoint, params=None):

    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {endpoint}: {e}")
        return None


def get_popular_movies(page=1):

    endpoint = "movie/popular"
    params = {"language": "en-US", "page": page}
    return fetch_from_tmdb(endpoint, params=params)


def get_trending_movies(time_window="day"):

    endpoint = f"trending/movie/{time_window}"
    params = {"language": "en-US"}
    return fetch_from_tmdb(endpoint, params=params)


def get_movie_details(movie_id):

    endpoint = f"movie/{movie_id}"
    params = {"language": "en-US"}
    return fetch_from_tmdb(endpoint, params=params)


def search(query, page=1, include_adult=False):

    endpoint = "search/movie"
    params = {
        "query": query,
        "include_adult": str(include_adult).lower(),
        "language": "en-US",
        "page": page,
    }
    return fetch_from_tmdb(endpoint, params=params)


def get_movie_credits(movie_id):

    endpoint = f"movie/{movie_id}/credits"
    return fetch_from_tmdb(endpoint)


def get_movie_images(movie_id):
    endpoint = f"movie/{movie_id}/images"
    data = fetch_from_tmdb(endpoint)

    if not data:
        return None

    backdrops = data.get("backdrops", [])
    posters = data.get("posters", [])

    if backdrops:
        return random.choice(backdrops).get("file_path")
    if posters:
        return posters[0].get("file_path")


def get_content_recommendations(movie_id):
    endpoint = f"movie/{movie_id}/recommendations"
    params = {"api_key": api_key, "language": "en-US"}
    response_data = fetch_from_tmdb(endpoint, params=params)

    if response_data:
        content_based_recommendations = [
            movie["id"] for movie in response_data.get("results", [])
        ]
        return content_based_recommendations
    return []
