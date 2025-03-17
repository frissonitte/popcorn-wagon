from flask_login import UserMixin
from sqlalchemy import (
    REAL,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.extensions import db


class Movie(db.Model):
    __tablename__ = "movies"

    movieId = db.Column(db.Integer, primary_key=True)
    tmdbId = db.Column(db.Integer, nullable=True)
    imdbId = db.Column(db.Integer, nullable=True)

    __table_args__ = (db.Index("idx_movie_movieId", "movieId"),)

    ratings = db.relationship("Rating", back_populates="movie", lazy="select")
    tags = db.relationship("Tag", back_populates="movie", lazy="select")
    user_list_items = db.relationship(
        "UserListItems", back_populates="movie", lazy="select"
    )
    user_movie_data = db.relationship(
        "UserMovieData", back_populates="movie", lazy="select"
    )


class Rating(db.Model):
    __tablename__ = "ratings"
    __table_args__ = (
        db.Index("idx_rating_userId", "userId"),
        db.Index("idx_rating_movieId", "movieId"),
    )
    userId = db.Column(db.Integer, db.ForeignKey("users.userId"), primary_key=True)
    movieId = db.Column(db.Integer, db.ForeignKey("movies.movieId"), primary_key=True)
    timestamp = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.REAL, nullable=False)

    movie = db.relationship("Movie", back_populates="ratings")
    user = db.relationship("User", back_populates="ratings")


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey("users.userId"), nullable=False)
    movieId = db.Column(db.Integer, db.ForeignKey("movies.movieId"), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    tag = db.Column(db.String(100), nullable=False)

    movie = db.relationship("Movie", back_populates="tags")
    user = db.relationship("User", back_populates="tags")

    __table_args__ = (
        db.Index("idx_tag_user_movie", "userId", "movieId"),
        db.Index("idx_tag_tag", "tag"),
        db.UniqueConstraint("userId", "movieId", "tag", name="unique_user_movie_tag"),
    )


class User(db.Model, UserMixin):
    __tablename__ = "users"

    userId = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    hash = db.Column(db.String(255), nullable=False)

    ratings = db.relationship("Rating", back_populates="user", lazy="select")
    tags = db.relationship("Tag", back_populates="user", lazy="select")
    movie_data = db.relationship("UserMovieData", back_populates="user", lazy="select")
    lists = db.relationship("UserList", back_populates="user", lazy="select")
    list_items = db.relationship("UserListItems", back_populates="user", lazy="select")
    mapping = db.relationship("UserMapping", back_populates="user", lazy="joined")

    def get_id(self):
        return str(self.userId)


class UserMovieData(db.Model):
    __tablename__ = "user_movie_data"

    userId = db.Column(Integer, ForeignKey("users.userId"), primary_key=True)
    movieId = db.Column(Integer, ForeignKey("movies.movieId"), primary_key=True)

    liked = db.Column(Integer, nullable=True)
    rating = db.Column(REAL, nullable=True)
    tagId = db.Column(Integer, ForeignKey("tags.id"), nullable=True)

    tag = relationship("Tag", backref="user_movie_data", lazy=True)
    user = relationship("User", back_populates="movie_data")
    movie = relationship("Movie", back_populates="user_movie_data")

    __table_args__ = (
        Index("idx_user_movie_data_userId", "userId"),
        Index("idx_user_movie_data_movieId", "movieId"),
        CheckConstraint("rating BETWEEN 1 AND 10", name="rating_check"),
        CheckConstraint("liked IN (-1, 1)", name="liked_check"),
        PrimaryKeyConstraint("userId", "movieId", name="primary_key_constraint"),
    )


class UserList(db.Model):
    __tablename__ = "user_lists"
    listId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey("users.userId"), nullable=False)
    list_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    background_image = db.Column(db.String(255))

    user = db.relationship("User", back_populates="lists")
    items = db.relationship("UserListItems", back_populates="list", cascade="all")


class UserListItems(db.Model):
    __tablename__ = "user_list_items"

    itemId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    listId = db.Column(db.Integer, db.ForeignKey("user_lists.listId"), nullable=False)
    movieId = db.Column(db.Integer, db.ForeignKey("movies.movieId"), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey("users.userId"), nullable=False)

    timestamp = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    list = db.relationship("UserList", back_populates="items")
    movie = db.relationship("Movie", back_populates="user_list_items")
    user = db.relationship("User", back_populates="list_items")

    __table_args__ = (
        db.UniqueConstraint("listId", "movieId", name="unique_list_movie"),
    )


class UserMapping(db.Model):
    __tablename__ = "user_mapping"
    movielens_userId = db.Column(db.Integer, primary_key=True)
    system_userId = db.Column(db.Integer, db.ForeignKey("users.userId"), unique=True)

    user = db.relationship("User", back_populates="mapping")
