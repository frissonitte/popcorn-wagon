from flask import Blueprint, render_template, flash, redirect, url_for
import tmdb_api
import logging

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def index():
    movies_1 = tmdb_api.get_popular_movies()
    movies_2 = tmdb_api.get_trending_movies()
    if movies_1 and 'results' in movies_1:
        popular_movies = movies_1['results']
    else:
        popular_movies = []
    
    if movies_2 and 'results' in movies_2:
        trending_movies = movies_2['results']
    else:
        trending_movies = []
    
    return render_template('index.html', popular_movies=popular_movies, trending_movies=trending_movies)

@main.route('/movie/<int:movie_id>') 
def movie_details(movie_id):
    movie = tmdb_api.get_movie_details(movie_id)
    if movie:
        return render_template('movie_details.html', movie=movie)
    else:
        flash("Movie details not found.", "danger")
        return redirect(url_for("home"))

def init_routes(app):
    app.register_blueprint(main)
