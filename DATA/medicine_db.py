import pandas as pd

# Simple large medicine list
MEDICINES = [
"paracetamol","ibuprofen","aspirin","amoxicillin","azithromycin",
"metformin","atorvastatin","losartan","amlodipine","omeprazole",
"pantoprazole","cetirizine","levocetirizine","montelukast",
"diclofenac","naproxen","prednisone","hydrocortisone","insulin",
"clopidogrel","warfarin","heparin","doxycycline","ciprofloxacin",
"fluconazole","ketoconazole","lisinopril","ramipril","valsartan",
"telmisartan","atenolol","propranolol","metoprolol","carvedilol",
"furosemide","spironolactone","hydrochlorothiazide","glimepiride",
"gliclazide","pioglitazone","rosuvastatin","simvastatin","pravastatin",
"esomeprazole","rabeprazole","ranitidine","famotidine","ondansetron",
"domperidone","metoclopramide","sertraline","fluoxetine","paroxetine",
"escitalopram","venlafaxine","duloxetine","gabapentin","pregabalin",
"tramadol","codeine","morphine","oxycodone","lidocaine","bupivacaine"
]

# Convert to dictionary
MED_DB = {med: {"side_effects": ["nausea","headache"], "interactions": []}
          for med in MEDICINES}