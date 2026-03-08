import json
import os


def identify_medicines(text):

    base_dir = os.path.dirname(__file__)
    json_path = os.path.join(base_dir, "DATA", "medicine_db.json")

    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    medicine_db = data["medicines"]

    detected = []

    text = text.lower()

    for med in medicine_db:
        if med in text:
            detected.append(med)

    return detected