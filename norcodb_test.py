import requests
import json

url = "https://app.nocodb.com/api/v2/tables/m0ie1m31ppddrew/records?limit=87"

headers = {
    "xc-token": "rdtB29RbpxOXAEp9Lhe6idL80ifLwi0QEGNR11TI",
    "Content-Type": "application/json"
}

# Sample job data
# job_data = json.load(open('jobs_20250326_085412.json'))

try:
    # Send POST request with the job data
    response = requests.get(url, headers=headers)

    job_uids = [job['job_uid'] for job in response.json()['list']]

    
    # Print response status code
    print(f"Status Code: {response.status_code}")
    
    # Print response as json
    print(len(job_uids))

except Exception as e:
    print(f"Error sending data: {e}")

    # Try to parse and pretty print JSON response if available
    # try:
#         response_json = response.json()
#         print("\nFormatted Response:")
#         print(json.dumps(response_json, indent=2))
#     except json.JSONDecodeError:
#         print("Response is not in JSON format")

# except Exception as e:
#     print(f"Error sending data: {e}")