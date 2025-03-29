import json
import requests
from datetime import datetime
import os

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
        print(f"\nNew jobs after filtering: {len(new_jobs)}")
        
        # Debug: Print first few filtered jobs
        # print("\nDebug: First few filtered jobs")
        # for job in new_jobs[:5]:
        #     print(f"  {job.get('job_uid')}")

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