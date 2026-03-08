def check_interactions(meds):

    warnings = []

    if "ibuprofen" in meds and "aspirin" in meds:

        warnings.append({
            "pair": "ibuprofen + aspirin",
            "risk": "Increased risk of stomach bleeding"
        })

    if "atorvastatin" in meds and "azithromycin" in meds:

        warnings.append({
            "pair": "atorvastatin + azithromycin",
            "risk": "May increase muscle toxicity"
        })

    return warnings


def calculate_risk_score(meds, warnings):

    score = 10

    score += len(warnings) * 30

    if score > 100:
        score = 100

    return score