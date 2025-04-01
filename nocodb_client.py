import json
import requests
from datetime import datetime
import os
from gemini_client import test_gemini_api

class NocodbClient:
    def __init__(self, base_url, token):
        """
        Initialize the Nocodb client.
        
        Args:
            base_url: The base URL of the Nocodb API
            token: The authentication token
            data_dir: Directory to store data files (logs and saved jobs)
        """
        self.base_url = base_url
        self.headers = {
            "xc-token": token,
            "Content-Type": "application/json"
        }
        
        self.params = {
            "limit": 100,
            "sort": "-job_uid",
        }

    def cleanup_old_records(self, max_rows=500):
        """
        Delete oldest records if total rows exceed max_rows.
        
        Args:
            max_rows: Maximum number of rows to keep (default: 100)
            
        Returns:
            bool: True if cleanup was successful, False otherwise
        """
        try:
            # Get total number of rows
            response = requests.get(self.base_url, headers=self.headers)
            if response.status_code != 200:
                print(f"Failed to get total rows. Response: {response.text}")
                return False
                
            total_rows = response.json()['pageInfo']['totalRows']
            print(f"Total rows in database: {total_rows}")
            
            if total_rows > max_rows:
                # Get oldest records to delete
                delete_params = {
                    "limit": 100,
                    "sort": "job_uid",  # Sort ascending to get oldest records
                    "fields": "Id,post_date",  # Only get id and job_uid fields
                    # "select": "id"  # Explicitly select only these fields
                }
                response = requests.get(self.base_url, headers=self.headers, params=delete_params)
                print(f"Rows to be deleted: {response.text}")
                
                if response.status_code != 200:
                    # print(f"Failed to get records to delete. Response: {response.text}")
                    return False
                    
                records_to_delete = response.json()['list']
                print(f"Found {len(records_to_delete)} records to delete")
                
                # Delete the records
                delete_response = requests.delete(self.base_url, headers=self.headers, json=records_to_delete)
                if delete_response.status_code == 200:
                    print(f"Successfully deleted {len(records_to_delete)} old records")
                    return True
                else:
                    print(f"Failed to delete records. Response: {delete_response.text}")
                    return False
            else:
                print("No cleanup needed - total rows within limit")
                return True
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return False

    def get_existing_job_uids(self):
        """
        Get all existing job_uids from NocoDB.
        
        Returns:
            set: Set of existing job_uids
        """
        try:
            response = requests.get(self.base_url, headers=self.headers, params=self.params)
            if response.status_code == 200:
                response_json = response.json()
                print("\nNocoDB Response:")
                # print(json.dumps(response_json, indent=2))
                
                # Extract job_uids from the list of jobs
                existing_jobs = response_json.get('list', [])
                # print(f"\nNumber of existing jobs from NocoDB: {len(existing_jobs)}")
                
                
                job_uids = {job.get('job_uid') for job in existing_jobs if job.get('job_uid')}
                print(f"\nTotal unique job UIDs found: {len(job_uids)}")
                return job_uids
            else:
                print(f"Failed to retrieve existing jobs. Response: {response.text}")
                return set()
        except Exception as e:
            print(f"Error retrieving existing jobs: {e}")
            return set()

    def send_jobs(self, jobs):
        """
        Send job data to NocoDB only if they don't already exist in NocoDB.
        Only sends jobs with rating > 4.2.
        
        Args:
            jobs: List of job dictionaries to send
            
        Returns:
            dict: The response from NocoDB
        """
        # First filter jobs by rating
        high_rated_jobs = [job for job in jobs if job.get("rating") and float(job["rating"]) > 4.2]
        print(f"High rated jobs to process: {len(high_rated_jobs)}")

       
        
        # Clean up old records before sending new ones
        self.cleanup_old_records(max_rows=100)
        
        # Get existing job_uids from NocoDB
        existing_job_uids = self.get_existing_job_uids()
        print(f"Existing job_uids in NocoDB: {existing_job_uids}")
        
        # Print job_uids we're trying to send
        new_job_uids = {job.get("job_uid") for job in high_rated_jobs if job.get("job_uid")}
        print(f"Job UIDs to send: {new_job_uids}")
        
        # Debug: Print first few jobs from both sets
        print("\nDebug: First few jobs from each set")
        print("Existing jobs in NocoDB:")
        for uid in list(existing_job_uids):
            print(f"  {uid}")
        print("\nJobs to send:")
        for uid in list(new_job_uids):
            print(f"  {uid}")
            
        # Filter out jobs that already exist
        new_jobs = [job for job in high_rated_jobs if job.get("job_uid") not in existing_job_uids]
        print(f"\nNew jobs after filtering low rated jobs: {len(new_jobs)}")

        #send jobs to Gemini
        if new_jobs:
            gemini_response = test_gemini_api(jobs=new_jobs)
            
            if gemini_response is not None:
                # Step 1: Convert Gemini response into a lookup dictionary
                gemini_lookup = {}
                # print(f"Gemini response: {gemini_response}")
                for job in new_jobs:
                    job_uid = job.get('job_uid')
                    if job_uid in gemini_response:
                        gemini_lookup[job_uid] = gemini_response[job_uid]
                        # print(f"Gemini lookup: {gemini_lookup}")
                
                # Step 2: Update new_jobs with Gemini response
                for job in new_jobs:
                    job_uid = job.get('job_uid')
                    if job_uid in gemini_lookup:
                        job.update(gemini_lookup[job_uid])
                
                # # Step 3: Filter out jobs that are not relevant to the resume
                # new_jobs = [job for job in new_jobs if job.get("relevant")]
                # print(f"\nNew jobs after filtering relevant jobs: {len(new_jobs)}")
                # # print(f"New jobs after filtering: {new_jobs}")
            else:
                print("No Gemini response received, skipping job filtering")

        if not new_jobs:
            print("No new jobs to send.")
            return None

        try:
            response = requests.post(self.base_url, headers=self.headers, json=new_jobs)

            if response.status_code == 200:
                response_json = response.json()
                print(f"Successfully sent {len(new_jobs)} jobs to NocoDB.")

                return response_json
            else:
                print(f"Failed to send jobs. Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error sending data: {e}")
            return None

    def get_jobs(self):
        """
        Get job data from NocoDB.
        
        Returns:
            list: List of job dictionaries
        """
        try:
            response = requests.get(self.base_url, headers=self.headers, params=self.params)

            if response.status_code == 200:
                response_json = response.json()
                print(f"Successfully retrieved {len(response_json)} jobs from NocoDB.")
                return response_json
            else:
                print(f"Failed to retrieve jobs. Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error retrieving data: {e}")
            return None

# Create a default client instance
default_client = NocodbClient(
    base_url=f"https://app.nocodb.com/api/v2/tables/{os.environ['NOCODB_TABLE_MARKETING']}/records",
    token=os.environ['NOCODB_TOKEN']
)

# Example usage
if __name__ == "__main__":
    jobs_to_send = [
        {"job_uid": "12345", "title": "Software Engineer", "company": "Tech Corp"},
        {"job_uid": "67890", "title": "Data Scientist", "company": "AI Labs"}
    ]
    
    default_client.send_jobs(jobs_to_send)
    default_client.save_extracted_jobs(jobs_to_send) 