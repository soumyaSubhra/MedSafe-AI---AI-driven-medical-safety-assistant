def analyze_symptoms(symptom, age=None, gender=None):

    symptom = symptom.lower()

    advice = []

    # BACK PAIN
    if "back" in symptom and "pain" in symptom:
        advice = [
            "Apply a warm compress to the back.",
            "Avoid prolonged sitting.",
            "Try gentle stretching exercises.",
            "Maintain proper posture."
        ]

    # HEADACHE
    elif "headache" in symptom:
        advice = [
            "Drink sufficient water.",
            "Rest in a quiet room.",
            "Reduce screen exposure."
        ]

    # EYE PROBLEMS
    elif "eye" in symptom:
        advice = [
            "Wash eyes with clean cold water.",
            "Avoid rubbing the eyes.",
            "Reduce screen brightness."
        ]

    # EMERGENCY
    elif "chest pain" in symptom or "breathing" in symptom:
        advice = [
            "🚨 Possible emergency detected.",
            "Seek medical attention immediately."
        ]

    # DEFAULT
    else:
        advice = [
            "For mild symptoms: rest and stay hydrated.",
            "Use over-the-counter relief if appropriate.",
            "Consult a clinician if symptoms persist."
        ]

    return advice