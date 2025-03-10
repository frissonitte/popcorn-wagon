from math import ceil

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user

import app.models as m
import tmdb_api as tmdb
from app.extensions import db

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
    movie = tmdb.get_movie_details(movieId)
    if movie:
        return render_template("movie_details.html", movie=movie)
    else:
        flash("Movie details not found.", "danger")
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


@main.route("/lists")
def lists():
    lists = m.UserList.query.filter_by(userId=current_user.userId).all()

    return render_template("lists.html", lists=lists)

@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if not query:
            flash("Enter a search term.", "danger")
            return redirect("/")
        return redirect(url_for('main.search', q=query, page=1))
    
    query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 10 

    if not query:
        flash("Enter a search term.", "danger")
        return redirect("/")
    
    result = tmdb.search(query, page=page)
    
    if not result or 'results' not in result or not result['results']:
        flash(f"No results found for '{query}'. Please try another search term.", "warning")
        return redirect("/")
    
    movies = result['results']
    total_pages = result.get('total_pages', 1)
    total_results = result.get('total_results', 0)

    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    return render_template("search_results.html", 
                           movies=movies, 
                           query=query, 
                           page=page, 
                           total_pages=total_pages, 
                           total_results=total_results)


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
    list = m.UserList.query.get(listId)
    if list:
        db.session.delete(list)
        db.session.commit()
        flash("List removed successfully!", "success")
    else:
        flash("List not found.", "danger")
    return redirect(url_for("main.lists"))


@main.route("/remove_item", methods=["POST"])
def remove_item():
    itemId = request.form.get("itemId")
    item = m.UserListItems.query.get(itemId)
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("Item removed successfully!", "success")
    else:
        flash("Item not found.", "danger")
    return redirect(url_for("main.list_details", listId=item.listId))


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


def init_routes(app):
    app.register_blueprint(main)
