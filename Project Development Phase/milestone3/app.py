# app.py - Complete Streamlit UI for MedSafe AI
# Put this file next to your other project files in MEDSAFE_AI

import streamlit as st
from typing import List, Dict, Any
import os
import tempfile
import traceback

st.set_page_config(page_title="MedSafe AI", layout="wide")

# --- Safe imports for project modules (fall back if missing) ---
# We'll import functions if they exist; otherwise provide safe minimal versions.

# ocr_reader: expected function read_prescription(image_path) -> str (extracted text)
try:
    import ocr_reader
    _read_prescription = getattr(ocr_reader, "read_prescription", None) or getattr(ocr_reader, "ocr_image", None)
    if _read_prescription is None:
        raise ImportError("ocr_reader has no read_prescription / ocr_image")
except Exception as e:
    _read_prescription = None
    st.sidebar.warning("ocr_reader.py missing or lacks read_prescription. OCR tab will use fallback (pytesseract if installed).")

# medicine_identifier: expected function identify_medicines(text) -> list[str]
try:
    import medicine_identifier
    identify_medicines = getattr(medicine_identifier, "identify_medicines", None)
    if identify_medicines is None:
        raise ImportError("medicine_identifier.identify_medicines missing")
except Exception as e:
    identify_medicines = None
    st.sidebar.warning("medicine_identifier.py missing or lacks identify_medicines. Medicine detection will be simple token match fallback.")

# risk_engine: expected check_interactions(meds)->list[dict], calculate_risk_score(meds, warnings)->int
try:
    from risk_engine import check_interactions, calculate_risk_score
except Exception:
    # fallback simple implementations
    def check_interactions(meds: List[str]) -> List[Dict[str,str]]:
        warnings = []
        meds_set = set(meds or [])
        if "ibuprofen" in meds_set and "aspirin" in meds_set:
            warnings.append({"pair": "ibuprofen + aspirin", "risk": "Increased risk of stomach bleeding"})
        return warnings

    def calculate_risk_score(meds: List[str], warnings: List[Dict[str,str]]) -> int:
        score = 10 + len(warnings) * 30
        return min(100, score)

    st.sidebar.warning("risk_engine.py missing or functions absent — using simple fallback rule engine.")

# symptom_engine (optional): expected analyze_symptoms(symptoms, age, gender) -> str / dict
try:
    import symptom_engine
    analyze_symptoms = getattr(symptom_engine, "analyze_symptoms", None)
    if analyze_symptoms is None:
        raise ImportError("symptom_engine.analyze_symptoms missing")
except Exception:
    analyze_symptoms = None
    st.sidebar.info("symptom_engine.py missing — symptom guidance will use a simple fallback.")

# AI modules
# ai_model: generate_ai_explanation(meds, warnings, symptoms, risk_score, prefer_remote=True)
try:
    import ai_model
    generate_ai_explanation = getattr(ai_model, "generate_ai_explanation")
except Exception:
    ai_model = None
    def generate_ai_explanation(meds, warnings, symptoms, risk_score, prefer_remote=True):
        # simple textual fallback
        parts = []
        if meds:
            parts.append("Detected medicines: " + ", ".join(meds) + ".")
        if warnings:
            for w in warnings:
                parts.append(f"Interaction: {w.get('pair')} — {w.get('risk')}.")
        if symptoms:
            parts.append("Symptoms: " + symptoms + ".")
        if risk_score >= 75:
            parts.append("Risk: high — seek urgent care.")
        elif risk_score >= 40:
            parts.append("Risk: moderate — consult a healthcare professional.")
        else:
            parts.append("Risk: low — monitor and follow guidance.")
        parts.append("This is educational information only — not medical advice.")
        return " ".join(parts)

    st.sidebar.info("ai_model.py missing — using local deterministic fallback for AI explanations.")


# ai_ollama (optional): for local ollama path
try:
    import ai_ollama
    call_ollama = getattr(ai_ollama, "call_ollama", None)
except Exception:
    call_ollama = None

# ai_explainer optional: might contain helper prompts
try:
    import ai_explainer
except Exception:
    ai_explainer = None


# -----------------------
# Helper utilities
# -----------------------
def save_uploaded_file(uploaded_file) -> str:
    """Save a Streamlit uploaded file to a temporary path and return path."""
    if uploaded_file is None:
        return ""
    suffix = os.path.splitext(uploaded_file.name)[1]
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def normalize_meds_input(text: str) -> List[str]:
    """Take comma-separated or newline-separated input and return list of lowercase stripped meds."""
    if not text:
        return []
    # split on comma or newline; allow semicolon
    parts = []
    for token in text.replace(";", ",").split(","):
        token = token.strip()
        if token:
            parts.append(token.lower())
    return parts


def show_warning_box(msg: str):
    st.markdown(f"<div style='background:#1e3a8a;color:#e6f0ff;padding:12px;border-radius:8px'>{msg}</div>", unsafe_allow_html=True)


# -----------------------
# Page layout and tabs
# -----------------------
st.title("MedSafe AI — Medicine Safety Assistant")
st.write("Prototype — educational only. Not medical advice.")

tabs = st.tabs(["Home", "Interaction Checker", "Prescription OCR", "Symptom Solver", "Risk Predictor"])
tab1, tab2, tab3, tab4, tab5 = tabs


# -----------------------
# TAB: HOME
# -----------------------
with tab1:
    st.header("Welcome")
    st.markdown("""
    **MedSafe AI** helps extract medicines from prescriptions, check drug interactions,
    compute a simple risk score and generate an AI-based educational explanation.

    Use the tabs to:
    - Upload a prescription image (Prescription OCR)
    - Check interactions for medicines (Interaction Checker)
    - Describe symptoms and get symptom guidance (Symptom Solver)
    - See combined risk & AI explanation (Risk Predictor)
    """)
    st.markdown("**Quick demo inputs:** `ibuprofen, aspirin` — then go to Risk Predictor → Check Interactions → Generate AI Explanation.")


# -----------------------
# TAB: INTERACTION CHECKER
# -----------------------
with tab2:
    st.header("Medicine Interaction Checker")

    # prefer detected meds from OCR if present
    detected = st.session_state.get("detected_meds", [])
    st.subheader("Medicines")
    if detected:
        st.write("Detected from prescription/OCR:")
        for m in detected:
            st.write("•", m)
    meds_manual_input = st.text_input("Or enter medicines (comma separated)", value=", ".join(detected) if detected else "")

    meds_list = normalize_meds_input(meds_manual_input)
    if st.button("Check Interactions"):
        warnings = check_interactions(meds_list)
        risk_score = calculate_risk_score(meds_list, warnings)
        st.session_state["warnings"] = warnings
        st.session_state["risk_score"] = risk_score
        st.session_state["detected_meds"] = meds_list
        st.success("Interaction check complete.")
        if warnings:
            st.warning("Warnings found:")
            for w in warnings:
                st.write("•", w.get("pair"), " — ", w.get("risk"))
        else:
            st.info("No known interaction warnings found.")
        st.write("Risk score:", risk_score)


# -----------------------
# TAB: PRESCRIPTION OCR
# -----------------------
with tab3:
    st.header("Prescription OCR")
    st.markdown("Upload a prescription image (jpg/png). The app will try to extract text and detect medicines.")

    uploaded = st.file_uploader("Upload prescription image", type=["png", "jpg", "jpeg"], accept_multiple_files=False)
    btn_ocr = st.button("Run OCR") if uploaded else None

    if uploaded and (btn_ocr or st.session_state.get("auto_ocr_run") is None):
        # Save uploaded file
        path = save_uploaded_file(uploaded)
        extracted_text = ""
        # try project OCR function
        if _read_prescription is not None:
            try:
                # some read_prescription accept path, some accept bytes; try path first
                try:
                    extracted_text = _read_prescription(path)
                except Exception:
                    # try reading bytes
                    with open(path, "rb") as f:
                        data = f.read()
                    extracted_text = _read_prescription(data)
            except Exception as e:
                st.error(f"OCR function failed: {e}")
                extracted_text = ""
        else:
            # fallback: try pytesseract if installed
            try:
                from PIL import Image
                import pytesseract
                img = Image.open(path).convert("L")
                extracted_text = pytesseract.image_to_string(img)
            except Exception as e:
                st.error("No OCR available (pytesseract not installed and ocr_reader missing). Install pytesseract or add read_prescription.")
                extracted_text = ""

        if extracted_text:
            st.subheader("Extracted text")
            st.text_area("OCR text", value=extracted_text, height=200)
            # identify medicines
            medicines = []
            if identify_medicines is not None:
                try:
                    medicines = identify_medicines(extracted_text)
                except Exception as e:
                    st.error(f"medicine_identifier failed: {e}")
                    medicines = []
            else:
                # fallback: crude tokenizer looking for known tokens
                tokens = [w.strip(".,()").lower() for w in extracted_text.split()]
                common_drugs = ["paracetamol","ibuprofen","aspirin","pantoprazole","amoxicillin","cetirizine"]
                medicines = [t for t in tokens if t in common_drugs]
                medicines = list(dict.fromkeys(medicines))  # unique preserve order

            if medicines:
                st.success(f"Detected medicines: {', '.join(medicines)}")
                st.session_state["detected_meds"] = medicines
            else:
                st.info("No medicines detected automatically. You can add them in Interaction Checker.")

        # cleanup temp file
        try:
            os.remove(path)
        except Exception:
            pass


# -----------------------
# TAB: SYMPTOM SOLVER
# -----------------------
with tab4:
    st.header("Symptom & Doubt Solver")
    st.markdown("Describe symptoms and get educational guidance (non-diagnostic).")

    age = st.number_input("Age", min_value=0, max_value=120, value=int(st.session_state.get("age", 25)))
    gender = st.selectbox("Gender", options=["Prefer not to say", "Male", "Female", "Other"], index=0)
    symptom_text = st.text_area("Describe your symptoms", value=st.session_state.get("symptom_input", ""), height=150)

    if st.button("Analyze Symptoms"):
        st.session_state["age"] = age
        st.session_state["symptom_input"] = symptom_text
        if analyze_symptoms is not None:
            try:
                result = analyze_symptoms(symptom_text, age=age, gender=gender)
                st.info(result)
            except Exception as e:
                st.error(f"Symptom engine failed: {e}")
                # fallback
                st.info("If symptoms are severe or worsening, seek medical attention. Rest and hydration may help for mild symptoms.")
        else:
            # fallback simple guidance
            if "fever" in symptom_text.lower() or "breath" in symptom_text.lower():
                st.warning("Red flag symptoms detected — seek urgent medical attention.")
            else:
                st.info("For mild symptoms: rest, hydrate, over-the-counter relief as appropriate. Consult a clinician if symptoms persist.")

# -----------------------
# TAB: RISK PREDICTOR
# -----------------------
with tab5:
    st.header("🚨 Emergency Risk Predictor")

    # use medicines stored in session_state
    medicines_list = st.session_state.get("detected_meds", [])
    st.subheader("Detected Medicines")
    if medicines_list:
        for m in medicines_list:
            st.write("💊", m)
    else:
        st.info("No medicines detected. Use Prescription OCR or Interaction Checker to add medicines.")
        manual = st.text_input("Or enter medicines (comma-separated to check)", key="risk_manual")
        if manual:
            medicines_list = normalize_meds_input(manual)
            st.session_state["detected_meds"] = medicines_list

    # button to (re)compute interactions if not computed
    if st.button("Check Interactions (Risk tab)"):
        warnings = check_interactions(medicines_list)
        st.session_state["warnings"] = warnings
        st.session_state["risk_score"] = calculate_risk_score(medicines_list, warnings)
        st.success("Interaction check completed.")

    warnings = st.session_state.get("warnings", [])
    risk_score = st.session_state.get("risk_score", 0)

    st.subheader("Risk Score")
    st.progress(max(0, min(100, int(risk_score or 0))) / 100)
    if risk_score >= 75:
        st.error("⚠ High Risk – Seek immediate medical attention")
    elif risk_score >= 40:
        st.warning("Moderate Risk – Consult a healthcare professional")
    else:
        st.success("Low Risk – Monitor and follow guidance")

    st.subheader("⚠ Interaction Warnings")
    if warnings:
        for w in warnings:
            st.markdown(f"- **{w.get('pair')}** — {w.get('risk')}")
    else:
        st.info("No interaction warnings recorded.")

    st.subheader("Symptoms (context)")
    symptoms = st.text_input("Optional: describe symptoms to add context", value=st.session_state.get("symptom_input", ""), key="risk_symptoms")

    st.subheader("AI Medical Explanation")
    if st.button("Generate AI Explanation"):
        # Call remote AI then fallback to local explanation if fails (generate_ai_explanation handles fallback)
        with st.spinner("Generating explanation..."):
            try:
                explanation = generate_ai_explanation(
                    st.session_state.get("detected_meds", medicines_list or []),
                    st.session_state.get("warnings", warnings or []),
                    st.session_state.get("symptom_input", symptoms or ""),
                    st.session_state.get("risk_score", risk_score or 0),
                    prefer_remote=True
                )
                # If explanation too long, show in expander
                if len(explanation) > 800:
                    with st.expander("AI Explanation (click to expand)"):
                        st.write(explanation)
                else:
                    st.info(explanation)
            except Exception as e:
                st.error(f"AI generation failed: {e}")
                # try local fallback if ai_model exposes _local_explanation
                try:
                    if ai_model and hasattr(ai_model, "_local_explanation"):
                        fallback = ai_model._local_explanation(
                            st.session_state.get("detected_meds", medicines_list or []),
                            st.session_state.get("warnings", warnings or []),
                            st.session_state.get("symptom_input", symptoms or ""),
                            st.session_state.get("risk_score", risk_score or 0)
                        )
                        st.info(fallback)
                except Exception:
                    st.info("Local fallback not available. See sidebar messages for diagnostic hints.")

# -----------------------
# Footer / quick diagnostics
# -----------------------
st.sidebar.title("Project Shortcuts & Diagnostics")
st.sidebar.markdown("- Files present: ")
try:
    files = os.listdir(".")
    show = [f for f in files if f.endswith(".py") or f.endswith(".json")]
    st.sidebar.write(show)
except Exception:
    pass

st.sidebar.markdown("**Helpful:** restart Streamlit after edits: `Ctrl+C` then `streamlit run app.py`.")