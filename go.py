# https://github.com/2captcha/2captcha-python

import time
import sys
import os
import json
from datetime import datetime
from seleniumbase import SB
from selenium.webdriver.common.by import By
from job_extractor import extract_posted_date, extract_job_data
from auth import login
from nocodb_client import default_client

def main():
    url = os.environ['UPWORK_SEARCH_URL']
    
    with SB(uc=True, test=True, locale="en") as sb:
        sb.uc_open_with_reconnect(url, 8)
        sb.uc_gui_click_captcha()
        sb.sleep(2)


        
        # First try to login
        if not login(sb):
            print("Login failed. Exiting...")
            return
            
        print("Navigating to job search...")
        sb.uc_open_with_reconnect(url, 4)
        sb.uc_gui_click_captcha()
        sb.sleep(2)


        
        # Check if we got through
        #give time to load
        # sb.assert_element("#job-tile", timeout=10)
        # if "job-tile" not in sb.get_page_source():
        #     print("Could not find job listings. Page may not have loaded properly.")
        #     return
            
        # Extract job data
        print("Extracting job data...")
        jobs = extract_job_data(sb)
        
        if not jobs:
            print("No jobs were successfully extracted. Exiting...")
            return
            
        # Filter high-rated jobs
        high_rated_jobs = [job for job in jobs if job.get("rating") and float(job["rating"]) > 4.2]
        print(f"Found {len(high_rated_jobs)} high-rated jobs out of {len(jobs)} total jobs")

        # Send high-rated jobs to Nocodb
        default_client.send_jobs(high_rated_jobs)
        


        # Keep browser open for inspection
        print("Keeping browser open for inspection...")
        sb.sleep(10)  # Adjust time as needed

if __name__ == "__main__":
    main()
