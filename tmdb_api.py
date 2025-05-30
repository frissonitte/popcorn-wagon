import os
import random

import requests
from dotenv import load_dotenv

from app.extensions import cache

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

def get_movie_keywords(movie_id):

    endpoint = f"movie/{movie_id}/keywords"
    response_data = fetch_from_tmdb(endpoint)

    if response_data and "keywords" in response_data:
        return [keyword["name"] for keyword in response_data["keywords"]]
    return []

def get_keyword_id(keyword):

    params = {"query": keyword, "api_key": api_key}
    data = fetch_from_tmdb("search/keyword", params)
    
    if data and "results" in data and data["results"]:
        return data["results"][0]["id"] 

def keyword_search(keyword, page=1):

    keyword_id = get_keyword_id(keyword)
    if not keyword_id:
        print(f"Tag '{keyword}' not found.")
        return []

    params = {"with_keywords": keyword_id, 
              "api_key": api_key, 
              "page":page,}
    data = fetch_from_tmdb("discover/movie", params)
    
    return data.get("results", []) if data else []


def search(query, page=1, include_adult=False):

    endpoint = "search/movie"
    params = {
        "query": query,
        "include_adult": str(include_adult).lower(),
        "language": "en-US",
        "page": page,
    }
    return fetch_from_tmdb(endpoint, params=params)


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
