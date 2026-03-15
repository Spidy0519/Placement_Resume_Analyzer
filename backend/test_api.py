import requests
import json
import sys

base_url = "http://localhost:8000"

print("1. Uploading resume...")
with open("test_resume.docx", "rb") as f:
    files = {"file": ("test_resume.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    res = requests.post(f"{base_url}/upload-resume", files=files)
    
if res.status_code != 200:
    print(f"Failed to upload: {res.text}")
    sys.exit(1)

data = res.json()
session_id = data["session_id"]
print(f"Upload success! Session ID: {session_id}")

print("2. Detecting department...")
req_data = {"session_id": session_id, "department": "CSE", "selected_job": "Software Developer"}
res = requests.post(f"{base_url}/detect-department", json=req_data)
if res.status_code != 200:
    print(f"Failed to detect: {res.text}")
    sys.exit(1)
print(f"Detect success: {res.json()}")

print("3. Getting placement scores...")
res = requests.post(f"{base_url}/get-placement-scores", json=req_data)
if res.status_code != 200:
    print(f"Failed to evaluate: {res.text}")
    sys.exit(1)
print("Scores computed successfully!")
