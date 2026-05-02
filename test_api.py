"""Test the /api/v1/analyze endpoint."""
import requests
import json

url = "http://localhost:8001/api/v1/analyze"

payload = {
    "patient_id": "P001",
    "clinical_note": "Patient is a 65-year-old male with chief complaint of chest tightness and shortness of breath for 3 days. Past medical history: hypertension for 10 years. Vitals: BP 150/95 mmHg, HR 82 bpm."
}

resp = requests.post(url, json=payload, timeout=120)
print("Status:", resp.status_code)
print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
