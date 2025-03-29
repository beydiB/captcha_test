from selenium.webdriver.common.by import By
import re
from datetime import datetime, timedelta

def get_post_date_time(post_string):
    """
    Parse a post string and return the date and time in a structured format.
    
    Args:
        post_string: String containing the post time (e.g., "Posted 2 hours ago")
        
    Returns:
        dict: Dictionary containing postDate and postTime
    """
    minutes_match = re.search(r"Posted (\d+) minutes ago", post_string)
    hours_match = re.search(r"Posted (\d+) hour(s)? ago", post_string)
    yesterday_match = re.search(r"Posted yesterday", post_string, re.IGNORECASE)
    days_match = re.search(r"Posted (\d+) day(s)? ago", post_string, re.IGNORECASE)

    if minutes_match:
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

def extract_posted_date(job_element):
    """
    Extract the posted date from a job element and parse it into a structured format.
    
    Args:
        job_element: The Selenium WebElement containing the job data
        
    Returns:
        dict: Dictionary containing the original posted date string and parsed date/time
    """
    try:
        # Find the element containing the posted date
        date_element = job_element.find_element(By.CSS_SELECTOR, 'small[data-test="job-pubilshed-date"]')
        
        # Find all span elements within the date element
        date_spans = date_element.find_elements(By.TAG_NAME, 'span')
        
        # Check if there are at least 2 spans (which is how Upwork formats their dates)
        if len(date_spans) >= 2:
            # Combine the text from both spans with a space between them
            # For example: "Posted" + "2 days ago" = "Posted 2 days ago"
            posted_date = f"{date_spans[0].text.strip()} {date_spans[1].text.strip()}"
        else:
            # If there's only one span or no spans, just get the text directly
            posted_date = date_element.text.strip()
            
        print(f"Posted date: {posted_date}")
        
        # Parse the posted date string into structured format
        parsed_date = get_post_date_time(posted_date)
        
        return {
            "posted_date_string": posted_date,
            "parsed_date": parsed_date
        }
        
    except Exception as e:
        print(f"Error extracting posted date: {e}")
        return {
            "posted_date_string": None,
            "parsed_date": {"postDate": None, "postTime": None}
        } 