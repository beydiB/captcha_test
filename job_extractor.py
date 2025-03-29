from selenium.webdriver.common.by import By
from date_parser import parse_relative_time

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
        parsed_date = parse_relative_time(posted_date)
        
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

def extract_job_data(sb):
    """
    Extract job data from the Upwork job listings page.
    
    Args:
        sb: SeleniumBase instance for browser interaction
        
    Returns:
        list: List of dictionaries containing job data
    """
    jobs = []
    try:
        # Wait for the job container to load with explicit wait
        print("Waiting for job listings to load...")
        sb.wait_for_element('section[data-test="JobsList"]', timeout=20)
        
        # Additional wait to ensure content is fully loaded
        sb.sleep(2)
        
        # Get all job elements
        job_elements = sb.find_elements('article[data-test="JobTile"]')
        print(f"Found {len(job_elements)} job listings")
        
        for index, job_element in enumerate(job_elements, 1):
            try:
                job = {}
                print(f"\nProcessing job {index} of {len(job_elements)}")
                
                # Extract job-uid first
                try:
                    job['job_uid'] = job_element.get_attribute('data-ev-job-uid')
                    print(f"Job UID: {job['job_uid']}")
                except Exception as e:
                    print(f"Error extracting job UID: {e}")
                    job['job_uid'] = None

                # Extract posted date using the new module
                posted_date_data = extract_posted_date(job_element)
                job['posted_date'] = posted_date_data['posted_date_string']
                job['post_date'] = posted_date_data['parsed_date']['postDate']
                job['post_time'] = posted_date_data['parsed_date']['postTime']
                
                # Extract title and URL
                try:
                    title_element = job_element.find_element(By.CSS_SELECTOR, 'a[data-test="job-tile-title-link UpLink"]')
                    job['title'] = title_element.text.strip()
                    job['job_url'] = title_element.get_attribute('href')
                    print(f"Title: {job['title']}")
                except Exception as e:
                    print(f"Error extracting title: {e}")
                
                # Extract payment verification
                try:
                    payment_element = job_element.find_element(By.CSS_SELECTOR, 'li[data-test="payment-verified"]')
                    job['payment_verified'] = payment_element.text.strip()
                    print(f"Payment verification: {job['payment_verified']}")
                except Exception as e:
                    print(f"Error extracting payment verification: {e}")
                
                # Extract rating and total feedback
                try:
                    rating_element = job_element.find_element(By.CSS_SELECTOR, 'div[data-test="feedback-rating UpCRating"]')
                    rating_value = rating_element.find_element(By.CSS_SELECTOR, '.air3-rating-value-text').text.strip()
                    tooltip = job_element.find_element(By.CSS_SELECTOR, 'div.air3-popper-content div')
                    total_feedback = tooltip.text.strip()
                    job['rating'] = rating_value
                    job['total_feedback'] = total_feedback
                    print(f"Rating: {rating_value}, Total feedback: {total_feedback}")
                except Exception as e:
                    print(f"Error extracting rating: {e}")
                
                # Extract total spent
                try:
                    spent_elements = job_element.find_elements(By.CSS_SELECTOR, 'li[data-test="total-spent"]')
                    if spent_elements:
                        spent_element = spent_elements[0]
                        strong_elements = spent_element.find_elements(By.TAG_NAME, 'strong')
                        if strong_elements:
                            job['total_spent'] = strong_elements[0].text.strip()
                            print(f"Total spent: {job['total_spent']}")
                        else:
                            job['total_spent'] = ""
                            print("No strong element found for total spent")
                    else:
                        job['total_spent'] = ""
                        print("No total spent section found")
                except Exception as e:
                    print(f"Error extracting total spent: {e}")
                    job['total_spent'] = ""
                
                # Extract location
                try:
                    location_element = job_element.find_element(By.CSS_SELECTOR, 'li[data-test="location"]')
                    location_text = location_element.text.strip()
                    # Remove any icon text if present
                    if 'GBR' in location_text or 'USA' in location_text:
                        job['location'] = location_text.split()[-1]
                    else:
                        job['location'] = location_text
                    print(f"Location: {job['location']}")
                except Exception as e:
                    print(f"Error extracting location: {e}")
                
                # Extract job type
                try:
                    job_type_element = job_element.find_element(By.CSS_SELECTOR, 'li[data-test="job-type-label"]')
                    job_type_text = job_type_element.text.strip()
                    # Remove "Hourly:" prefix if present
                    job['job_type'] = job_type_text.replace('Hourly:', '').strip()
                    print(f"Job type: {job['job_type']}")
                except Exception as e:
                    print(f"Error extracting job type: {e}")
                
                # Extract experience level
                try:
                    exp_element = job_element.find_element(By.CSS_SELECTOR, 'li[data-test="experience-level"]')
                    job['experience_level'] = exp_element.text.strip()
                    print(f"Experience level: {job['experience_level']}")
                except Exception as e:
                    print(f"Error extracting experience level: {e}")
                
                # Extract estimated time
                try:
                    time_element = job_element.find_element(By.CSS_SELECTOR, 'li[data-test="duration-label"]')
                    time_text = time_element.text.strip()
                    # Remove "Est. time:" prefix if present
                    job['estimated_time'] = time_text.replace('Est. time:', '').strip()
                    print(f"Estimated time: {job['estimated_time']}")
                except Exception as e:
                    print(f"Error extracting estimated time: {e}")
                
                # Extract description
                try:
                    desc_element = job_element.find_element(By.CSS_SELECTOR, 'div[data-test="UpCLineClamp JobDescription"] p')
                    job['description'] = desc_element.text.strip()
                    print(f"Description length: {len(job['description'])} characters")
                except Exception as e:
                    print(f"Error extracting description: {e}")
                
                # Extract skills
                try:
                    skill_elements = job_element.find_elements(By.CSS_SELECTOR, 'div[data-test="TokenClamp JobAttrs"] button[data-test="token"] span')
                    job['skills'] = [skill.text.strip() for skill in skill_elements]
                    print(f"Skills: {', '.join(job['skills'])}")
                except Exception as e:
                    print(f"Error extracting skills: {e}")
                
                # Extract proposals
                try:
                    # First check if the proposals section exists
                    proposals_section = job_element.find_element(By.CSS_SELECTOR, 'ul[data-test="JobInfoClientMore"]')
                    proposals_element = proposals_section.find_element(By.CSS_SELECTOR, 'li[data-test="proposals-tier"]')
                    proposals_text = proposals_element.text.strip()
                    # Remove "Proposals:" prefix if present
                    job['proposals'] = proposals_text.replace('Proposals:', '').strip()
                    print(f"Proposals: {job['proposals']}")
                except Exception as e:
                    print(f"No proposals information available for this job")
                    job['proposals'] = "Not specified"
                
                # Only append job if at least title was found
                if job.get('title'):
                    jobs.append(job)
                    print(f"Successfully extracted data for job: {job['title']}")
                else:
                    print(f"Skipping job {index} - no title found")
                
            except Exception as e:
                print(f"Error processing job {index}: {e}")
                continue
        
        print(f"\nSuccessfully extracted data for {len(jobs)} jobs")
        return jobs
        
    except Exception as e:
        print(f"Error during job data extraction: {e}")
        return [] 