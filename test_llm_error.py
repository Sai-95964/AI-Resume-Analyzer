import requests
import json

resp = requests.get('http://localhost:5000/api/samples')
data = resp.json()
resume_text = data['resume_text']
job_desc = data['job_description']

# Create a file-like object for the resume
from io import BytesIO
resume_file = BytesIO(resume_text.encode())

payload = {
    'job_description': job_desc,
    'include_llm': 'true'
}

files = {
    'resume': ('resume.txt', resume_file, 'text/plain')
}

resp = requests.post('http://localhost:5000/api/analyze', files=files, data=payload)
result = resp.json()

if 'llm_analysis' in result:
    print(json.dumps(result['llm_analysis'], indent=2))
elif 'llm_insights' in result:
    print("LLM INSIGHTS:")
    print(json.dumps(result['llm_insights'], indent=2))
elif 'error' in result:
    print(f"ERROR: {result['error']}")
else:
    print('No llm_analysis or llm_insights found')
    print(f"Keys: {list(result.keys())}")
