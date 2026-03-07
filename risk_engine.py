import json
import os


def check_interactions(medicines):

    base_dir = os.path.dirname(__file__)
    json_path = os.path.join(base_dir, "DATA", "medicine_db.json")

    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    interactions = data["interactions"]

    warnings = []

    for rule in interactions:

        drug1 = rule["drug1"]
        drug2 = rule["drug2"]

        if drug1 in medicines and drug2 in medicines:

            warnings.append({
                "pair": f"{drug1} + {drug2}",
                "risk": rule["risk"]
            })

    return warnings


def calculate_risk_score(medicines, warnings):

    score = 0

    score += len(medicines) * 10
    score += len(warnings) * 30

    if score > 100:
        score = 100

    return score