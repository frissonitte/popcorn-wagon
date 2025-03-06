from datetime import datetime

def format_date(date_string):
    try:
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
        return date_obj.strftime("%m-%d-%Y")
    except ValueError:
        return date_string
