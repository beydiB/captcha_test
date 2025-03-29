import re
from datetime import datetime, timedelta

def parse_relative_time(post_string):
    """
    Parse a relative time string into actual date and time.
    
    Args:
        post_string: String containing the post time (e.g., "Posted 2 hours ago")
        
    Returns:
        dict: Dictionary containing postDate and postTime
    """
    minutes_match = re.search(r"Posted (\d+) minute(s)? ago", post_string)
    hours_match = re.search(r"Posted (\d+) hour(s)? ago", post_string)
    yesterday_match = re.search(r"Posted yesterday", post_string, re.IGNORECASE)
    days_match = re.search(r"Posted (\d+) day(s)? ago", post_string, re.IGNORECASE)
    seconds_match = re.search(r"Posted (\d+) second(s)? ago", post_string)

    if seconds_match:
        now = datetime.now()
        return {
            "postDate": now.strftime("%Y-%m-%d"),
            "postTime": now.strftime("%H:%M")
        }
    elif minutes_match:
        minutes_ago = int(minutes_match.group(1))
        date_time = datetime.now() - timedelta(minutes=minutes_ago)
        post_date = date_time.strftime("%Y-%m-%d")
        post_time = date_time.strftime("%H:%M")
    elif hours_match:
        hours_ago = int(hours_match.group(1))
        date_time = datetime.now() - timedelta(hours=hours_ago)
        post_date = date_time.strftime("%Y-%m-%d")
        post_time = date_time.strftime("%H:%M")
    elif yesterday_match:
        yesterday = datetime.now() - timedelta(days=1)
        post_date = yesterday.strftime("%Y-%m-%d")
        post_time = None
    elif days_match:
        days_ago = int(days_match.group(1))
        past_date = datetime.now() - timedelta(days=days_ago)
        post_date = past_date.strftime("%Y-%m-%d")
        post_time = None
    else:
        return {"postDate": None, "postTime": None}

    return {"postDate": post_date, "postTime": post_time} 