# ai_model.py
# Robust HF caller that handles chat models and text-only models,
# with a deterministic local fallback so the UI never breaks.

import requests
import traceback
from typing import List, Dict, Any

# ===== CONFIG - set these =====
API_TOKEN = ""   # <- put your token here
MODEL_ID = "google/flan-t5-base"                  # <- change if you prefer another model
# ==============================

HF_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TEXT_URL_TEMPLATE = "https://api-inference.huggingface.co/models/{}"  # text-generation endpoint

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}


def _local_explanation(medicines: List[str], warnings: List[Dict[str, str]], symptoms: str, risk_score: int) -> str:
    """
    Safe, deterministic local explanation. Always available.
    """
    pieces = []
    if medicines:
        pieces.append("Detected medicines: " + ", ".join(medicines) + ".")
    else:
        pieces.append("No medicines detected.")
    if warnings:
        top = warnings[:3]
        for w in top:
            pair = w.get("pair", "combination")
            r = w.get("risk", "")
            pieces.append(f"Interaction: {pair} — {r}.")
    else:
        pieces.append("No known interaction warnings found.")
    if symptoms:
        pieces.append(f"Reported symptoms: {symptoms}.")
    if risk_score >= 75:
        pieces.append("Risk level: high — seek immediate medical attention.")
    elif risk_score >= 40:
        pieces.append("Risk level: moderate — consult a healthcare professional soon.")
    else:
        pieces.append("Risk level: low — monitor and follow guidance.")
    pieces.append("This is educational information only — not medical advice.")
    return " ".join(pieces)


def _call_chat_model(prompt: str, model_id: str, timeout: int = 40) -> Dict[str, Any]:
    """
    Call HF router chat completions (OpenAI-compatible). Returns dict with ok/text/error/raw.
    """
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150
    }
    try:
        r = requests.post(HF_CHAT_URL, headers=HEADERS, json=payload, timeout=timeout)
    except Exception as e:
        return {"ok": False, "error": f"Network error calling chat endpoint: {e}", "raw": None}

    # try parse json
    try:
        data = r.json()
    except Exception:
        return {"ok": False, "error": f"Non-JSON response (status {r.status_code})", "raw": r.text}

    # HTTP error -> return structured error
    if r.status_code != 200:
        # often data has {"message": "...", "type": "..."} or {"error": "..."}
        # normalize to an error string
        err = None
        if isinstance(data, dict):
            err = data.get("message") or data.get("error") or str(data)
        else:
            err = str(data)
        return {"ok": False, "error": f"Chat endpoint HTTP {r.status_code}: {err}", "raw": data}

    # success shape: choices -> [ { message: { content: "..." } } ]
    if isinstance(data, dict) and "choices" in data and data["choices"]:
        try:
            content = data["choices"][0]["message"]["content"]
            return {"ok": True, "text": content}
        except Exception:
            return {"ok": False, "error": "Malformed chat response structure", "raw": data}

    # unexpected but valid
    return {"ok": False, "error": "Unexpected chat response format", "raw": data}


def _call_text_model(prompt: str, model_id: str, timeout: int = 40) -> Dict[str, Any]:
    """
    Call text-generation endpoint. Returns dict with ok/text/error/raw.
    Uses the /models/{model} endpoint (some models are text-only).
    """
    url = HF_TEXT_URL_TEMPLATE.format(model_id)
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 150}}
    try:
        r = requests.post(url, headers=HEADERS, json=payload, timeout=timeout)
    except Exception as e:
        return {"ok": False, "error": f"Network error calling text endpoint: {e}", "raw": None}

    try:
        data = r.json()
    except Exception:
        return {"ok": False, "error": f"Non-JSON response (status {r.status_code})", "raw": r.text}

    if r.status_code != 200:
        # data may include {"error": "..."} or similar
        if isinstance(data, dict):
            err = data.get("error") or data.get("message") or str(data)
        else:
            err = str(data)
        return {"ok": False, "error": f"Text endpoint HTTP {r.status_code}: {err}", "raw": data}

    # typical shape: list with generated_text or dict with generated_text
    if isinstance(data, list) and data and isinstance(data[0], dict) and "generated_text" in data[0]:
        return {"ok": True, "text": data[0]["generated_text"]}
    if isinstance(data, dict) and "generated_text" in data:
        return {"ok": True, "text": data["generated_text"]}

    # fallback to stringifying the whole response if it's unusual but useful
    return {"ok": True, "text": str(data)}


def generate_ai_explanation(medicines: List[str], warnings: List[Dict[str, str]], symptoms: str, risk_score: int, prefer_remote: bool = True) -> str:
    """
    Public function for app.py to call.
    Tries remote (chat -> text) if prefer_remote and token present; otherwise local fallback.
    Returns a short informative string (remote result or deterministic local fallback with short debug).
    """
    meds_text = ", ".join(medicines) if medicines else "none"
    prompt = (
        f"Medicines: {meds_text}\n"
        f"Symptoms: {symptoms or 'none'}\n"
        f"Risk Score: {risk_score}\n\n"
        "You are a cautious medical-education assistant. In 2-4 short sentences, explain the main safety concerns (non-diagnostic) and give a single short actionable advice line (e.g. 'Seek urgent care' or 'Monitor and follow up'). Avoid prescriptions or definitive diagnoses."
    )

    # If remote is allowed and token looks set, try remote
    if prefer_remote and API_TOKEN and not API_TOKEN.startswith("hf_xxx_REPLACE"):
        # 1) Try chat endpoint (works for chat-capable models)
        try:
            chat_res = _call_chat_model(prompt, MODEL_ID)
            if chat_res.get("ok"):
                return chat_res["text"].strip()
            # If chat failed and error message indicates "not a chat model" or "model_not_supported", fall through to text endpoint
            err_text = chat_res.get("error", "")
            # Common sign phrases
            not_chat_phrases = ["not a chat model", "model_not_supported", "is not supported", "model is not a chat model"]
            if any(p.lower() in (err_text or "").lower() for p in not_chat_phrases):
                # try text-gen endpoint
                text_res = _call_text_model(prompt, MODEL_ID)
                if text_res.get("ok"):
                    return text_res["text"].strip()
                # both failed -> fallback
                debug = f"chat_error: {err_text} | text_error: {text_res.get('error')}"
                fallback = _local_explanation(medicines, warnings, symptoms, risk_score)
                return f"{fallback}\n\n[AI unavailable: {debug}]"
            else:
                # chat failed for other reason -> try text endpoint anyway (useful if provider rejected)
                text_res = _call_text_model(prompt, MODEL_ID)
                if text_res.get("ok"):
                    return text_res["text"].strip()
                debug = f"chat_error: {err_text} | text_error: {text_res.get('error')}"
                fallback = _local_explanation(medicines, warnings, symptoms, risk_score)
                return f"{fallback}\n\n[AI unavailable: {debug}]"

        except Exception as e:
            debug = traceback.format_exc()
            fallback = _local_explanation(medicines, warnings, symptoms, risk_score)
            return f"{fallback}\n\n[AI call exception: {str(e)}]"

    # Remote not preferred or token missing -> local fallback
    return _local_explanation(medicines, warnings, symptoms, risk_score)