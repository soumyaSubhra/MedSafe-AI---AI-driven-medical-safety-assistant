import requests

API_URL = "https://api-inference.huggingface.co/models/microsoft/phi-3-mini-4k-instruct"

headers = {
    "Authorization": "Bearer YOUR_TOKEN"
}

def explain_risk(meds, risk):

    prompt = f"""
Medicines: {meds}

Risk level: {risk}

Explain possible medical safety concerns simply.
Advise when to see a doctor.
"""

    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

    return response.json()[0]["generated_text"]