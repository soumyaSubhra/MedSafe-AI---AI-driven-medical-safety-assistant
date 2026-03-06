import streamlit as st
from ocr_reader import read_prescription
from medicine_identifier import identify_medicines
from risk_engine import check_interactions, calculate_risk_score

st.title("MedSafe AI - Prescription Safety Analyzer")

uploaded_file = st.file_uploader("Upload Prescription", type=["png", "jpg", "jpeg"])

if uploaded_file:

    st.image(uploaded_file, caption="Uploaded Prescription")

    extracted_text = read_prescription(uploaded_file)

    st.subheader("Extracted Text")
    st.write(extracted_text)

    medicines = identify_medicines(extracted_text)

    st.subheader("Detected Medicines")

    if medicines:
        for med in medicines:
            st.write("💊", med)
    else:
        st.write("No medicines detected")

    warnings = check_interactions(medicines)

    if warnings:

        st.subheader("⚠ Drug Interaction Warnings")

        for w in warnings:
            st.write("⚠", w["pair"])
            st.write("Risk:", w["risk"])

    risk_score = calculate_risk_score(medicines, warnings)

    st.subheader("Risk Score")

    st.progress(risk_score / 100)

    st.write(f"Estimated Risk Level: {risk_score}%")