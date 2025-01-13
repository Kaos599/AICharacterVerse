# utils.py
from datetime import datetime

def format_datetime(dt: datetime) -> str:
    """Formats a datetime object into a readable string."""
    return dt.strftime("%dth %b %Y %I:%M%p").replace("AM", "am").replace("PM","pm")