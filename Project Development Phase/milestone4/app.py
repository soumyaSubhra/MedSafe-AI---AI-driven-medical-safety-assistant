import streamlit as st
from rapidfuzz import process, fuzz
from symptom_engine import analyze_symptoms
from PIL import Image
import pytesseract
import time   # TIMER ADDED

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.set_page_config(page_title="MedSafe AI", page_icon="💊")

# -----------------------------
# Medicine Database
# -----------------------------

MED_DB = {
    "paracetamol": {
        "side_effects": ["nausea", "rash"],
        "interactions": ["ibuprofen"]
    },
    "ibuprofen": {
        "side_effects": ["stomach pain"],
        "interactions": ["paracetamol"]
    },
    "aspirin": {
        "side_effects": ["bleeding"],
        "interactions": []
    },
}

# -----------------------------
# Symptom Engine
# -----------------------------

def symptom_engine(symptom):

    symptom = symptom.lower()

    if "back" in symptom and "pain" in symptom:
        return [
            "Apply a warm compress on the lower back.",
            "Avoid prolonged sitting.",
            "Perform gentle stretching exercises.",
            "Maintain good posture."
        ]

    if "headache" in symptom:
        return [
            "Drink sufficient water.",
            "Take rest in a quiet room.",
            "Reduce screen exposure."
        ]

    if "eye" in symptom:
        return [
            "Wash eyes with clean water.",
            "Avoid rubbing the eyes.",
            "Reduce screen brightness."
        ]

    return [
        "For mild symptoms: rest and stay hydrated.",
        "Use over-the-counter relief if appropriate.",
        "Consult a clinician if symptoms persist."
    ]


# -----------------------------
# Emergency Detection
# -----------------------------

def emergency_check(symptom):

    symptom = symptom.lower()

    if "chest pain" in symptom or "breathing difficulty" in symptom:
        return "🚨 Possible emergency. Seek medical help immediately."

    return None


# -----------------------------
# Medicine Finder
# -----------------------------

def find_medicine(name):

    if not name:
        return None

    medicines = list(MED_DB.keys())

    match, score, _ = process.extractOne(
        name.lower(),
        medicines,
        scorer=fuzz.WRatio
    )

    if score > 80:
        return match

    return None


# -----------------------------
# Interaction Checker
# -----------------------------

def interaction_check(m1, m2):

    if m2 in MED_DB[m1]["interactions"]:
        return "⚠️ Potential interaction detected."

    return "✅ No major interaction found."


# -----------------------------
# OCR Reader
# -----------------------------

def read_prescription(image):

    text = pytesseract.image_to_string(image)
    return text


# -----------------------------
# Navigation
# -----------------------------

menu = [
    "Home",
    "Interaction Checker",
    "Prescription OCR",
    "Symptom Solver",
    "Risk Predictor"
]

page = st.sidebar.selectbox("Menu", menu)


# =====================================================
# HOME
# =====================================================

if page == "Home":

    st.title("💊 MedSafe AI")

    st.write("""
    MedSafe AI is an educational healthcare assistant that helps users:
    
    • Analyze symptoms  
    • Check medicine interactions  
    • Extract prescription text  
    • Detect emergency risks
    """)


# =====================================================
# INTERACTION CHECKER
# =====================================================

elif page == "Interaction Checker":

    st.title("Medicine Interaction Checker")

    med1 = st.text_input("Medicine 1")
    med2 = st.text_input("Medicine 2")

    if st.button("Check Interaction"):

        start_time = time.time()   # TIMER START

        m1 = find_medicine(med1)
        m2 = find_medicine(med2)

        if not m1 or not m2:
            st.error("Medicine not recognized.")

        else:

            result = interaction_check(m1, m2)

            st.write(result)

            st.subheader("Side Effects")

            for s in MED_DB[m1]["side_effects"]:
                st.write("•", s)

        end_time = time.time()   # TIMER END
        st.caption(f"Response time: {round(end_time - start_time,4)} seconds")


# =====================================================
# PRESCRIPTION OCR
# =====================================================

elif page == "Prescription OCR":

    st.title("Prescription OCR Reader")

    file = st.file_uploader("Upload prescription image")

    if file:

        image = Image.open(file)

        st.image(image)

        if st.button("Extract Text"):

            start_time = time.time()   # TIMER START

            text = read_prescription(image)

            st.subheader("Extracted Text")

            st.write(text)

            end_time = time.time()   # TIMER END
            st.caption(f"OCR processing time: {round(end_time - start_time,4)} seconds")


# =====================================================
# SYMPTOM SOLVER
# =====================================================

elif page == "Symptom Solver":

    st.title("Symptom & Doubt Solver")
    st.write("Describe symptoms and get educational guidance (non-diagnostic).")

    age = st.number_input("Age", 1, 120, 25)

    gender = st.selectbox(
        "Gender",
        ["Male", "Female", "Other", "Prefer not to say"]
    )

    symptom = st.text_area("Describe your symptoms")

    if st.button("Analyze Symptoms"):

        start_time = time.time()   # TIMER START

        if symptom.strip() == "":
            st.warning("Please enter symptoms.")
        else:

            symptom = symptom.lower()

            if "chest pain" in symptom or "breathing difficulty" in symptom:
                st.error("🚨 Possible emergency. Seek medical help immediately.")
                advice = [
                    "Stop activity immediately.",
                    "Contact medical services."
                ]

            elif "back" in symptom and "pain" in symptom:
                advice = [
                    "Apply warm compress to the back.",
                    "Avoid long sitting hours.",
                    "Do gentle stretching.",
                    "Maintain proper posture."
                ]

            elif "headache" in symptom:
                advice = [
                    "Drink sufficient water.",
                    "Rest in a quiet room.",
                    "Reduce screen exposure."
                ]

            elif "eye" in symptom:
                advice = [
                    "Wash eyes with clean water.",
                    "Avoid rubbing the eyes.",
                    "Reduce screen brightness."
                ]

            else:
                advice = [
                    "For mild symptoms: rest, hydrate, and monitor condition.",
                    "Use OTC relief if appropriate.",
                    "Consult a clinician if symptoms persist."
                ]

            st.subheader("Guidance")

            for tip in advice:
                st.write("•", tip)

        end_time = time.time()   # TIMER END
        st.caption(f"Analysis time: {round(end_time - start_time,4)} seconds")


# =====================================================
# RISK PREDICTOR
# =====================================================

elif page == "Risk Predictor":

    st.title("Basic Health Risk Predictor")

    symptom = st.text_area("Describe symptoms")

    if st.button("Predict Risk"):

        start_time = time.time()   # TIMER START

        symptom = symptom.lower()

        if "chest pain" in symptom or "breathing difficulty" in symptom:
            st.error("🚨 High Risk. Immediate medical attention advised.")

        elif "fever" in symptom:
            st.warning("Possible infection. Monitor temperature.")

        else:
            st.success("Low immediate risk based on provided symptoms.")

        end_time = time.time()   # TIMER END
        st.caption(f"Prediction time: {round(end_time - start_time,4)} seconds")


st.info("This system provides educational information only and does not replace professional medical advice.")