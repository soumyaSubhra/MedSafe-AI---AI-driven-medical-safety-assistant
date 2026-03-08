SYMPTOM_DB = {
    "headache": {
        "likely_meds": ["paracetamol"],
        "advice": "Rest, hydrate and take mild pain relief if needed."
    },
    "fever": {
        "likely_meds": ["paracetamol"],
        "advice": "Monitor temperature and stay hydrated."
    }
}

SIDE_EFFECT_DB = {
    "ibuprofen": ["stomach pain", "nausea"],
    "aspirin": ["bleeding risk"],
}


def interpret_symptoms(text):

    results = []

    symptoms = [s.strip().lower() for s in text.split(",")]

    for s in symptoms:

        if s in SYMPTOM_DB:

            results.append(SYMPTOM_DB[s])

    return results


def get_side_effects_for_meds(meds):

    effects = {}

    for m in meds:

        if m in SIDE_EFFECT_DB:

            effects[m] = SIDE_EFFECT_DB[m]

        else:

            effects[m] = ["No data available"]

    return effects