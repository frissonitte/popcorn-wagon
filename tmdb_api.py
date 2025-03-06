import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('API_KEY')
access_token = os.getenv('ACCESS_TOKEN')

headers = {
    'Authorization': f'Bearer {access_token}'
}

def fetch_from_tmdb(endpoint):
    url = f"https://api.themoviedb.org/3/{endpoint}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching {endpoint}: {response.status_code}") 
        return None
    
def get_popular_movies():
    return fetch_from_tmdb("movie/popular?language=en-US&page=1")

def get_trending_movies():
    return fetch_from_tmdb("trending/movie/day?language=en-US")
    
def get_movie_details(movie_id):
    return fetch_from_tmdb(f"movie/{movie_id}?language=en-US")