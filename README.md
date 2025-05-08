# 🍿 Popcorn Wagon

### 🎬 A Personalized Movie Recommendation Platform

📺 **Video Demo:** [Watch on YouTube](https://youtu.be/GBsyBuIxiC8)  
🔗 **GitHub Repo:** [github.com/frissonitte/popcorn-wagon](https://github.com/frissonitte/popcorn-wagon)

---

## 📖 Table of Contents

-   [About](#about)
-   [Features](#features)
-   [Getting Started](#getting-started)
    -   [Prerequisites](#prerequisites)
    -   [Installation](#installation)
-   [Project Structure](#project-structure)
-   [Reflections](#reflections)
-   [Roadmap](#roadmap)
-   [License](#license)
-   [Acknowledgments](#acknowledgments)
-   [Powered By](#powered-by)

---

## 📌 About

**Popcorn Wagon** is a Flask-powered web application that helps users discover and manage movies they love. It leverages a hybrid recommendation engine that combines:

-   ✅ Content-based filtering (TMDB API)
-   ✅ Collaborative filtering (MovieLens + SVD + Annoy)

Whether you're a cinephile or just browsing, Popcorn Wagon will help you find your next favorite movie!

---

## ✨ Features

-   🔍 Search movies via the TMDB API
-   🎞️ View movie details: posters, genres, overviews
-   ❤️ Like/dislike movies and add custom tags
-   📝 Create and manage personalized movie lists
-   🧠 Hybrid AI-powered recommendations using SVD + Annoy
-   🔐 User authentication and session management
-   🌐 Responsive UI built with Bootstrap 5

---

## 🚀 Getting Started

### Prerequisites

-   Python 3.x
-   Flask
-   SQLite
-   TMDB API Key (stored in a `.env` file as `SECRET_KEY`)

### Installation

```bash
# Clone the repository
git clone https://github.com/frissonitte/popcorn-wagon.git
cd popcorn-wagon

# (Optional) Set up a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dataset Setup

1. Download the full MovieLens dataset:  
   https://grouplens.org/datasets/movielens/latest/

2. Place these files in `app/data/`:

    - `links.csv`
    - `ratings.csv`
    - `tags.csv`

3. Remove `gnome-tags.csv` and `gnome-scores.csv` if included.

### Build the App

```bash
# (Optional) Clean and filter active users
python filter_csv.py

# Initialize the SQLite database
python data_loader.py

# Train the recommendation model
python train_model.py

# Run the Flask app
python run.py  # or use: flask run
```

Then open your browser to:  
http://127.0.0.1:5000

---

## 🗂️ Project Structure

```
popcorn-wagon/
├── app/
│   ├── data/             # MovieLens dataset
│   ├── static/           # CSS, JS, images
│   ├── templates/        # HTML templates
│   ├── utils/            # Utility scripts
│   ├── routes.py         # Main views
│   ├── auth.py           # Login/register
│   ├── models.py         # SQLAlchemy models
│   └── extensions.py     # Flask extensions
├── instance/             # SQLite DB
├── .env                  # Your API keys
├── train_model.py        # SVD + Annoy trainer
├── filter_csv.py         # Dataset cleaner
├── data_loader.py        # DB initializer
├── run.py                # App entry point
├── requirements.txt
└── README.md
```

---

## 💭 Reflections

This project taught me:

-   Flask routing, sessions, and form handling
-   Designing normalized SQL databases with SQLAlchemy
-   Building hybrid recommender systems
-   Using SVD + Annoy for fast similarity searches
-   Data cleaning and optimization with Pandas and Dask

---

## 📈 Roadmap

Planned enhancements:

-   UI/UX overhaul
-   REST API support
-   OAuth login (e.g. Google)
-   TMDB/IMDB list import
-   Shareable movie lists
-   Dark mode

---

## 🪪 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

-   CS50 team — for the CS foundation
-   MovieLens — for the public dataset
-   TMDB — for the movie metadata API
-   Flask & SQLAlchemy — backend technologies

---

## 🔌 Powered By

[![TMDB](https://www.themoviedb.org/assets/2/v4/logos/v2/blue_square_2-d537fb228cf3ded904ef09b136fe3fec72548ebc1fea3fbbd1ad9e36364db38b.svg)](https://www.themoviedb.org/)  
**MovieLens**, **Flask**, **Annoy**, **SVD**, **Dask**
