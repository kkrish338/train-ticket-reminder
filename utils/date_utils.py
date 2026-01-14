"""Date utility functions for reminder calculations"""
from datetime import datetime, timedelta
from typing import Tuple


def calculate_reminder_date(event_date: str) -> str:
    """Calculate reminder date (60 days before event date)
    
    Args:
        event_date: Event date in YYYY-MM-DD format
    
    Returns:
        Reminder date in YYYY-MM-DD format
    """
    event_dt = datetime.strptime(event_date, '%Y-%m-%d')
    reminder_dt = event_dt - timedelta(days=60)
    return reminder_dt.strftime('%Y-%m-%d')


def get_notification_timestamp(reminder_date: str, time_str: str = '07:45') -> int:
    """Get timestamp in milliseconds for notification time
    
    Args:
        reminder_date: Date in YYYY-MM-DD format
        time_str: Time in HH:MM format (default: 07:45)
    
    Returns:
        Timestamp in milliseconds (for Android AlarmManager)
    """
    dt = datetime.strptime(f"{reminder_date} {time_str}", '%Y-%m-%d %H:%M')
    return int(dt.timestamp() * 1000)


def format_date_display(date_str: str) -> str:
    """Format date for user-friendly display
    
    Args:
        date_str: Date in YYYY-MM-DD format
    
    Returns:
        Formatted date string (e.g., "Jan 14, 2026")
    """
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return dt.strftime('%b %d, %Y')


def validate_future_date(date_str: str) -> Tuple[bool, str]:
    """Validate that the date is in the future
    
    Args:
        date_str: Date in YYYY-MM-DD format
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        event_dt = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if event_dt <= today:
            return False, "Please select a future date"
        
        # Check if reminder date (60 days before) is in the past
        reminder_dt = event_dt - timedelta(days=60)
        if reminder_dt <= today:
            return False, "Event date must be more than 60 days in the future"
        
        return True, ""
    except ValueError:
        return False, "Invalid date format"


def get_days_until(date_str: str) -> int:
    """Calculate number of days until the given date
    
    Args:
        date_str: Date in YYYY-MM-DD format
    
    Returns:
        Number of days until the date
    """
    event_dt = datetime.strptime(date_str, '%Y-%m-%d')
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = event_dt - today
    return delta.days
