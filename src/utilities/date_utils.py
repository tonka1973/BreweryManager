"""
Date Utility Functions
Handles conversion between database and display formats
"""

from datetime import datetime
from ..config.constants import DATE_FORMAT, DATETIME_FORMAT, DISPLAY_DATE_FORMAT, DISPLAY_DATETIME_FORMAT


def format_date_for_display(date_string):
    """
    Convert database date format (YYYY-MM-DD) to display format (DD/MM/YYYY)

    Args:
        date_string: Date string in YYYY-MM-DD format or datetime object

    Returns:
        Date string in DD/MM/YYYY format, or empty string if invalid
    """
    if not date_string:
        return ''

    try:
        # If it's already a datetime object
        if isinstance(date_string, datetime):
            return date_string.strftime(DISPLAY_DATE_FORMAT)

        # Try to parse the date string
        date_obj = datetime.strptime(str(date_string), DATE_FORMAT)
        return date_obj.strftime(DISPLAY_DATE_FORMAT)
    except (ValueError, AttributeError):
        # If parsing fails, return as-is (might already be in display format or invalid)
        return str(date_string) if date_string else ''


def format_datetime_for_display(datetime_string):
    """
    Convert database datetime format to display format (DD/MM/YYYY HH:MM)

    Args:
        datetime_string: Datetime string in YYYY-MM-DD HH:MM:SS format or datetime object

    Returns:
        Datetime string in DD/MM/YYYY HH:MM format, or empty string if invalid
    """
    if not datetime_string:
        return ''

    try:
        # If it's already a datetime object
        if isinstance(datetime_string, datetime):
            return datetime_string.strftime(DISPLAY_DATETIME_FORMAT)

        # Try to parse the datetime string
        dt_obj = datetime.strptime(str(datetime_string), DATETIME_FORMAT)
        return dt_obj.strftime(DISPLAY_DATETIME_FORMAT)
    except (ValueError, AttributeError):
        # If parsing fails, return as-is
        return str(datetime_string) if datetime_string else ''


def parse_display_date(display_date):
    """
    Convert display format (DD/MM/YYYY) to database format (YYYY-MM-DD)

    Args:
        display_date: Date string in DD/MM/YYYY format

    Returns:
        Date string in YYYY-MM-DD format, or None if invalid
    """
    if not display_date:
        return None

    try:
        # Try to parse as display format first
        date_obj = datetime.strptime(str(display_date).strip(), DISPLAY_DATE_FORMAT)
        return date_obj.strftime(DATE_FORMAT)
    except ValueError:
        try:
            # Maybe it's already in database format
            date_obj = datetime.strptime(str(display_date).strip(), DATE_FORMAT)
            return date_obj.strftime(DATE_FORMAT)
        except ValueError:
            return None


def get_today_display():
    """
    Get today's date in display format (DD/MM/YYYY)

    Returns:
        Today's date as DD/MM/YYYY string
    """
    return datetime.now().strftime(DISPLAY_DATE_FORMAT)


def get_today_db():
    """
    Get today's date in database format (YYYY-MM-DD)

    Returns:
        Today's date as YYYY-MM-DD string
    """
    return datetime.now().strftime(DATE_FORMAT)


def get_now_db():
    """
    Get current datetime in database format (YYYY-MM-DD HH:MM:SS)

    Returns:
        Current datetime as YYYY-MM-DD HH:MM:SS string
    """
    return datetime.now().strftime(DATETIME_FORMAT)


def get_next_weekday_date(day_name):
    """
    Get the next date for a given weekday name.
    
    Args:
        day_name: Full day name (e.g., 'Monday', 'Tuesday')
        
    Returns:
        datetime object of the next occurrence of that day
    """
    days = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 
        'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    target_day = days.get(day_name.lower())
    if target_day is None:
        return datetime.now() # Fallback
        
    today_dt = datetime.now()
    current_day = today_dt.weekday()
    
    days_ahead = target_day - current_day
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
        
    from datetime import timedelta
    return today_dt + timedelta(days=days_ahead)
