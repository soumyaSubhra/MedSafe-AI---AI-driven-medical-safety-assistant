import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3"


def generate_ai_explanation(medicines, symptoms, risk_score):

    prompt = f"""
You are a medical safety assistant.

Medicines detected:
{medicines}

Symptoms reported:
{symptoms}

Calculated risk score:
{risk_score}

Explain the possible medical risk in simple educational terms.
Do NOT provide diagnosis or prescriptions.
Advise when to consult a doctor.
Keep answer short.
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:

        response = requests.post(OLLAMA_URL, json=payload)

        data = response.json()

        return data["response"]

    except Exception as e:

        return f"AI explanation unavailable: {e}"