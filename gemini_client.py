import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def test_gemini_api(jobs):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    api_key = os.environ['GEMINI_API_KEY'] or os.getenv("GEMINI_API_KEY")
    
    # Resume Summary
    resume_summary = os.getenv("RESUME")

    # Job Listings
    job_listings = jobs

    # Create prompt
    prompt = f"""
Given the following resume details:

{json.dumps(resume_summary, indent=2)}

Analyze the following job listings and determine which are relevant to the resume. 

{json.dumps(job_listings, indent=2)}

Return your response as a JSON array containing job matches. Each match should be a JSON object with:
- "job_uid": The job ID
- "relevant": True or False
- "match_score": A percentage indicating how well the job matches the resume
- "matching_skills": A list of skills from the resume that match the job requirements
- "score_explanation": Provide a brief explanation of the match score based on relevant experience, required skills, and overall fit for the role. Keep the response concise and objective, without mentioning any names or using pronouns.

Ensure the JSON is well-formed and can be parsed without errors.
"""
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    params = {
        "key": api_key
    }
    
    try:
        response = requests.post(url, headers=headers, params=params, json=data)
        print(f"Status Code: {response.status_code}")
        response_json = response.json()
        
        # Extract the text from the response
        if 'candidates' in response_json and len(response_json['candidates']) > 0:
            text_response = response_json['candidates'][0]['content']['parts'][0]['text']
            
            # Remove markdown code block markers
            text_response = text_response.replace('```json', '').replace('```', '').strip()
            
            # Parse the JSON array
            matches = json.loads(text_response)
            
            # Convert to dictionary with job_uid as keys
            matches_dict = {match['job_uid']: match for match in matches}
            
            return matches_dict
            
        else:
            print("No matches found in the response")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    test_gemini_api()