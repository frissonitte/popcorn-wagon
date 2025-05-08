Popcorn Wagon 🍿🎬

License: MIT

A movie recommendation platform powered by Flask, TMDB API, MovieLens dataset, and hybrid recommendation algorithms.

📌 This project was submitted as the Final Project for CS50x (Introduction to Computer Science) by HarvardX.
Table of Contents

    About Popcorn Wagon

    Features

    Demo

    Getting Started

        Prerequisites

        Installation

    Project Structure

    Reflections

    License

    Acknowledgments

    Powered By

About Popcorn Wagon

Popcorn Wagon is a Flask-based movie recommendation website designed to help users discover and organize their favorite movies. It combines content-based filtering (via the TMDB API) with collaborative filtering (via the MovieLens dataset) to deliver personalized recommendations.

Whether you're a cinephile or just browsing, Popcorn Wagon helps you find your next movie night pick!
Features

    🔍 Search for movies using TMDB API

    📄 View detailed movie info, including poster, genres, and overview

    ❤️ Like / dislike movies and tag them

    📝 Create and manage your own movie lists

    💡 Get AI-powered recommendations based on your lists using hybrid filtering

    🌐 Responsive, user-friendly interface built with Bootstrap 5

    🧠 Recommender system powered by SVD + Annoy + Dask

    🔐 User authentication and session management

Demo

You can watch the CS50 final project demo video here:

📺 YouTube: https://youtu.be/YOUR_VIDEO_LINK
🗂️ GitHub Repo: https://github.com/frissonitte/popcorn-wagon
Getting Started
Prerequisites

    Python 3.x

    Flask

    SQLite

    TMDB API Key (place it in your .env file as SECRET_KEY)

Installation

    Clone the repository:

    git clone https://github.com/frissonitte/popcorn-wagon.git
    cd popcorn-wagon

    Set up a virtual environment (optional but recommended):

    python -m venv venv
    source venv/bin/activate (Windows: venv\Scripts\activate)

    Install dependencies:

    pip install -r requirements.txt

    Download the MovieLens Dataset (Full):

        https://grouplens.org/datasets/movielens/latest/

        Place links.csv, ratings.csv, and tags.csv inside app/data/

        DELETE gnome-tags.csv and gnome-scores.csv if included

    (Optional) Filter active users and clean data:

    python filter_csv.py

    Set up the SQLite database:

    python data_loader.py

    Train the recommendation model (SVD + Annoy):

    python train_model.py

    Run the Flask application:

    python run.py
    or
    flask run

    Open your browser and navigate to:

    http://127.0.0.1:5000

Project Structure

popcorn-wagon/
├── app/
│ ├── data/ — Dataset files (MovieLens CSV)
│ ├── static/ — CSS, JS, images
│ ├── templates/ — HTML templates
│ ├── utils/ — Utility modules
│ ├── routes.py — Main views
│ ├── auth.py — Login/register routes
│ |── models.py — SQLAlchemy models
| └── extensions.py ─ Several helpers
├── instance/ — SQLite DB file
├── .env — Your API key and secrets (you create this)
├── train_model.py — SVD + Annoy training
├── filter_csv.py — Dataset cleaner
├── data_loader.py — Database initializer
├── run.py — App entry point
├── requirements.txt
└── README.md

Reflections

Popcorn Wagon helped me understand the following in depth:

    How web apps manage routes, sessions, and forms (Flask)

    How to design a normalized SQL database (SQLAlchemy)

    Recommender system logic using collaborative & content-based filtering

    Model optimization using SVD + Annoy for scalable similarity search

    Data cleaning and performance optimization with Pandas + Dask

I plan to expand it further with:

    UI Overhaul

    REST API support

    OAuth integration (e.g., Google login)

    List importing from TMDB and IMDB

    List sharing via public URLs

    Dark mode and mobile-first UI improvements

License

MIT License — See LICENSE file for more details.

Acknowledgments

    CS50 Team — for a great foundation in computer science

    MovieLens — for providing open-source user rating datasets

    TMDB — for the movie metadata API

    Flask + SQLAlchemy — for powering the backend

Powered By

[![TMDB](https://www.themoviedb.org/assets/2/v4/logos/v2/blue_square_2-d537fb228cf3ded904ef09b136fe3fec72548ebc1fea3fbbd1ad9e36364db38b.svg)](https://www.themoviedb.org/)
MovieLens
