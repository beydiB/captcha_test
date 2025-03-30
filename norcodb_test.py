import requests
import json
import os

# url = f"https://app.nocodb.com/api/v2/tables/{os.environ['NOCODB_TABLE_MARKETING']}/records?limit=87"

# headers = {
#     "xc-token": os.environ['NOCODB_TOKEN'],
#     "Content-Type": "application/json"
# }

# # Sample job data
# # job_data = json.load(open('jobs_20250326_085412.json'))

# try:
#     # Send POST request with the job data
#     response = requests.get(url, headers=headers)

#     job_uids = [job['job_uid'] for job in response.json()['list']]

    
#     # Print response status code
#     print(f"Status Code: {response.status_code}")
    
#     # Print response as json
#     print(len(job_uids))

# except Exception as e:
#     print(f"Error sending data: {e}")

url = f"https://app.nocodb.com/api/v2/tables/m0ie1m31ppddrew/records"

headers = {
    "xc-token": "rdtB29RbpxOXAEp9Lhe6idL80ifLwi0QEGNR11TI",
    "Content-Type": "application/json"
}

# Sample job data
# job_data = json.load(open('jobs_20250326_085412.json'))

try:
    # Send POST request with the job data
    response = requests.get(url, headers=headers)

    # job_uids = [job['job_uid'] for job in response.json()['list']]

    total_rows = response.json()['pageInfo']['totalRows']

    if total_rows > 100:
        # get oldest records based on job_uid and delete them
        response = requests.get(f'https://app.nocodb.com/api/v2/tables/m0ie1m31ppddrew/records?limit={total_rows - 100}&sort=job_uid&fields=id', headers=headers)
        print(response.json()['list'])
        #delete record
        delete_response = requests.delete(f'https://app.nocodb.com/api/v2/tables/m0ie1m31ppddrew/records', headers=headers, json=response.json()['list'])
        print(delete_response.json())
    
    # Print response status code
    print(f"Status Code: {response.status_code}")
    
    # Print response as json
    # print(len(job_uids))

except Exception as e:
    print(f"Error sending data: {e}")
