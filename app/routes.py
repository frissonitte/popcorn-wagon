import logging
import time
from math import ceil

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_caching import Cache
from flask_login import current_user

import app.models as m
import tmdb_api as tmdb
from app.extensions import db
from app.utils.recommend_utils import get_hybrid_recommendations

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def index():
    movies_1 = tmdb.get_popular_movies()
    movies_2 = tmdb.get_trending_movies()
    if movies_1 and "results" in movies_1:
        popular_movies = movies_1["results"]
    else:
        popular_movies = []

    if movies_2 and "results" in movies_2:
        trending_movies = movies_2["results"]
    else:
        trending_movies = []

    return render_template(
        "index.html", popular_movies=popular_movies, trending_movies=trending_movies
    )


@main.route("/movie/<int:movieId>")
def movie_details(movieId):
    try:
        movie = tmdb.get_movie_details(movieId)

        if not movie:
            flash("Movie details not found.", "danger")
            return redirect(url_for("main.index"))

        movie_tags = m.Tag.query.filter_by(movieId=movieId).all()
        user_tags = [tag.tag for tag in movie_tags]

        tmdb_keywords = tmdb.get_movie_keywords(movieId)

        tags = list(set(user_tags + tmdb_keywords))

        with open("movie.txt", "w") as f:
            f.write(f"{tags}")
            f.close()

        return render_template("movie_details.html", movie=movie, tags=tags)

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for("main.index"))


@main.route("/list_details/<int:listId>")
def list_details(listId):
    page = request.args.get("page", 1, type=int)
    per_page = 10

    total_movies = (
        db.session.query(m.UserListItems.movieId)
        .join(m.UserList, m.UserListItems.listId == m.UserList.listId)
        .filter(m.UserList.userId == current_user.userId, m.UserList.listId == listId)
        .count()
    )

    total_pages = ceil(total_movies / per_page)

    movies = (
        db.session.query(m.UserListItems.movieId)
        .join(m.UserList, m.UserListItems.listId == m.UserList.listId)
        .filter(m.UserList.userId == current_user.userId, m.UserList.listId == listId)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    if not movies:
        return render_template(
            "list_details.html",
            listId=listId,
            data=[],
            page=page,
            total_pages=total_pages,
        )

    movie_ids = [int(movie[0]) for movie in movies]
    data = []
    for movie_id in movie_ids:
        movie_details = tmdb.get_movie_details(movie_id)
        if movie_details:
            data.append(movie_details)

    return render_template(
        "list_details.html",
        listId=listId,
        data=data,
        page=page,
        total_pages=total_pages,
    )


@main.route("/recommendator", methods=["POST"])
def recommendator():
    movieIds = request.form.getlist("movieId", type=int)

    all_recommendations = []
    for movieId in movieIds:
        recommendations = get_hybrid_recommendations(movieId)
        all_recommendations.extend(recommendations)

    unique_recommendations = list(set(all_recommendations))

    recommended_movies = []
    for movieId in unique_recommendations[:10]:
        movie_details = tmdb.get_movie_details(movieId)
        if movie_details:
            recommended_movies.append(movie_details)

    return render_template(
        "recommendations.html", recommended_movies=recommended_movies
    )


@main.route("/lists")
def lists():
    lists = m.UserList.query.filter_by(userId=current_user.userId).all()

    return render_template("lists.html", lists=lists)


@main.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if not query:
            flash("Enter a search term.", "danger")
            return redirect("/")
        return redirect(url_for("main.search", q=query, page=1))

    query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 10

    if not query:
        flash("Enter a search term.", "danger")
        return redirect("/")

    result = tmdb.search(query, page=page)

    if not result or "results" not in result or not result["results"]:
        flash(
            f"No results found for '{query}'. Please try another search term.",
            "warning",
        )
        return redirect("/")

    movies = result["results"]
    total_pages = result.get("total_pages", 1)
    total_results = result.get("total_results", 0)

    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    return render_template(
        "search_results.html",
        movies=movies,
        query=query,
        page=page,
        total_pages=total_pages,
        total_results=total_results,
    )


@main.route("/dynamic_search")
def dynamic_search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    page = request.args.get("page", 1, type=int)
    result = tmdb.search(query, page=page)

    if not result or "results" not in result:
        return jsonify([])

    placeholder_url = url_for(
        "static", filename="images/No-Image-Placeholder.svg", _external=True
    )
    movies = [
        {
            "id": movie["id"],
            "title": movie["title"],
            "year": movie.get("release_date", "")[:4],
            "poster_url": (
                f"https://image.tmdb.org/t/p/w92{movie['poster_path']}"
                if movie.get("poster_path")
                else placeholder_url
            ),
        }
        for movie in result["results"]
    ]

    return jsonify(movies)


@main.route("/edit_list/<int:listId>", methods=["GET", "POST"])
def edit_list(listId):
    list = m.UserList.query.get_or_404(listId)
    if request.method == "POST":
        list.list_name = request.form.get("list_name")
        db.session.commit()
        flash("List updated successfully!", "success")
        return redirect(url_for("main.list_details", listId=listId))
    return render_template("edit_list.html", list=list)


@main.route("/remove_list", methods=["POST"])
def remove_list():
    listId = request.form.get("listId")
    if not listId or not listId.isdigit():
        flash("Invalid list ID.", "danger")
        return redirect(url_for("main.lists"))

    list_id = int(listId)
    user_list = m.UserList.query.get(list_id)

    if not user_list:
        flash(f"List with ID {list_id} not found.", "danger")
        return redirect(url_for("main.lists"))

    # Proceed with deleting the list if it exists
    db.session.delete(user_list)
    db.session.commit()
    flash("List removed successfully!", "success")
    return redirect(url_for("main.lists"))


@main.route("/remove_item", methods=["POST"])
def remove_item():
    movieId = request.form.get("movieId")
    listId = request.form.get("listId")

    if not movieId or not listId:
        flash("Invalid movie or list ID.", "danger")
        return redirect(url_for("main.lists"))

    item = m.UserListItems.query.filter_by(
        listId=listId, movieId=movieId, userId=current_user.userId
    ).first()

    if item:
        db.session.delete(item)
        db.session.commit()
        flash("Movie removed successfully!", "success")
    else:
        flash("Movie not found.", "danger")

    return redirect(url_for("main.list_details", listId=listId))


@main.route("/create_list", methods=["GET", "POST"])
def create_list():
    if request.method == "POST":
        list_name = request.form.get("list_name")
        movies = request.form.get("movies", "").strip()
        background_image = request.form.get("background_image")

        if not list_name:
            flash("List name is required!", "error")
            return redirect(url_for("main.create_list"))

        movie_ids = [movie.strip() for movie in movies.split(",") if movie.strip()]

        if not background_image or background_image == "null":
            if movie_ids:
                first_movie_image = tmdb.get_movie_images(movie_ids[0])
                if first_movie_image:
                    background_image = (
                        f"https://image.tmdb.org/t/p/w1280{first_movie_image}"
                    )
                else:
                    background_image = url_for(
                        "static", filename="images/No-Image-Placeholder.svg"
                    )
            else:
                background_image = url_for(
                    "static", filename="images/No-Image-Placeholder.svg"
                )

        new_list = m.UserList(
            userId=current_user.userId,
            list_name=list_name,
            background_image=background_image,
        )
        db.session.add(new_list)
        db.session.commit()

        for movie_id in movie_ids:
            new_items = m.UserListItems(
                listId=new_list.listId, movieId=movie_id, userId=current_user.userId
            )
            db.session.add(new_items)

        db.session.commit()
        flash("List created successfully!", "success")
        return redirect(url_for("main.list_details", listId=new_list.listId))

    movies = []
    return render_template("create_list.html", movies=movies)


@main.route("/add_to_list", methods=["POST"])
def add_to_list():
    movieId = request.form.get("movieId")
    listId = request.form.get("listId")

    if not movieId or not listId:
        flash("Invalid request.", "danger")
        return redirect(url_for("main.index"))

    user_list = m.UserList.query.get(listId)
    if not user_list:
        flash("List not found!", "danger")
        return redirect(url_for("main.index"))

    logging.info(
        f"Existing movie IDs in list: {[item.movieId for item in user_list.items]}"
    )
    logging.info(f"Trying to add movieId: {movieId}")
    logging.info(f"Type of user_list.items: {type(user_list.items)}")

    if any(item.movieId == int(movieId) for item in user_list.items):
        flash("This movie is already in the list!", "warning")
    else:
        new_item = m.UserListItems(
            listId=listId, movieId=movieId, userId=current_user.userId
        )
        db.session.add(new_item)
        db.session.commit()
        flash(f"Movie added to {user_list.list_name} successfully!", "success")

    return redirect(url_for("main.movie_details", movieId=movieId))


@main.route("/add_to_liked", methods=["POST"])
def add_to_liked():
    movieId = request.form.get("movieId")
    action = request.form.get("action")

    if not movieId or not action:
        flash("Invalid request. Action is required.", "danger")
        return redirect(url_for("main.index"))

    user_data = m.UserMovieData.query.filter_by(
        userId=current_user.userId, movieId=movieId
    ).first()

    if action == "LIKE":
        new_value = 1
    elif action == "DISLIKE":
        new_value = -1
    else:
        flash("Invalid action.", "danger")
        return redirect(url_for("main.index"))

    if user_data:
        if user_data.liked == new_value:
            user_data.liked = None
            flash("Your preference has been removed.", "info")
        else:
            user_data.liked = new_value
            flash(
                f"Movie {'liked' if new_value == 1 else 'disliked'} successfully!",
                "success",
            )
        db.session.commit()
    else:
        new_data = m.UserMovieData(
            userId=current_user.userId,
            movieId=movieId,
            liked=new_value,
        )
        db.session.add(new_data)
        db.session.commit()
        flash(
            f"Movie {'liked' if new_value == 1 else 'disliked'} successfully!",
            "success",
        )

    return redirect(url_for("main.movie_details", movieId=movieId))


@main.route("/add_to_tags", methods=["POST"])
def add_to_tags():
    movieId = request.form.get("movieId")
    tag_text = request.form.get("tag")

    if not tag_text:
        flash("You need to enter a tag", "info")
        return redirect(request.referrer)

    existing_tag = m.Tag.query.filter_by(
        userId=current_user.userId, movieId=movieId, tag=tag_text
    ).first()

    if existing_tag:
        flash("You have already added this tag to this movie!", "warning")
        return redirect(request.referrer)

    new_tag = m.Tag(
        userId=current_user.userId,
        movieId=movieId,
        tag=tag_text,
        timestamp=int(time.time()),
    )
    db.session.add(new_tag)
    db.session.commit()

    user_movie_data = m.UserMovieData.query.filter_by(
        userId=current_user.userId, movieId=movieId
    ).first()

    if not user_movie_data:
        user_movie_data = m.UserMovieData(
            userId=current_user.userId, movieId=movieId, tagId=new_tag.id
        )
        db.session.add(user_movie_data)
    else:
        user_movie_data.tagId = new_tag.id

    db.session.commit()
    flash("Tag successfully added!", "success")
    return redirect(request.referrer)


def init_routes(app):
    app.register_blueprint(main)
