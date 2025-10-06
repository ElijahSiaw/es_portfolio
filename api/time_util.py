import datetime

# Define the custom filter function
def format_datetime(value, format='%Y-%m-%d %H:%M'):
    if isinstance(value, datetime.datetime):
        return value.strftime(format)
    return value

def format_date(value, format='%b %d, %Y'):
    """Formats a datetime object to a short date string (e.g., 'Sep 19, 2025')."""
    if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
        return value.strftime(format)
    return value

def format_date_long(value, format='%B %d, %Y'):
    """Formats a datetime object to a long date string (e.g., 'September 19, 2025')."""
    if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
        return value.strftime(format)
    return value

def format_datetime_long(value, format='%A, %B %d, %Y at %I:%M %p'):
    """Formats a datetime object to a long datetime string (e.g., 'Friday, September 19, 2025 at 12:05 AM')."""
    if isinstance(value, datetime.datetime):
        return value.strftime(format)
    return value

def format_datetime_short(value, format='%b %d, %Y %I:%M %p'):
    """Formats a datetime object to a short datetime string (e.g., 'Sep 19, 2025 12:05 AM')."""
    if isinstance(value, datetime.datetime):
        return value.strftime(format)
    return value
