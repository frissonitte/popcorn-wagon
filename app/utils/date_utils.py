from datetime import datetime
from flask import Flask

def format_date(date_string):
    try:
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
        return date_obj.strftime("%m-%d-%Y")
    except ValueError:
        return date_string

def register_filters(app: Flask):
    app.jinja_env.filters['format_date'] = format_date