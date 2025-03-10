from datetime import datetime

from flask import Flask


def format_date(date_input, format="%b %d %Y"):
    if isinstance(date_input, datetime):
        return date_input.strftime(format)
    elif date_input and isinstance(date_input, str):
        try:
            date_obj = datetime.strptime(date_input, "%Y-%m-%d")
            return date_obj.strftime(format)
        except ValueError:
            return date_input
    return date_input or "Unknown Date"


def register_filters(app: Flask):
    app.jinja_env.filters["format_date"] = format_date
