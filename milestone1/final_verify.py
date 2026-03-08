import streamlit as st
import pytesseract
from PIL import Image
from rapidfuzz import fuzz
import ollama
import sys

print("--- MEDSAFE AI ACTIVITY 1 VERIFICATION ---")

# 1. Check Python Version
print(f"Python Version: {sys.version.split()[0]} - {'✅ OK' if sys.version_info >= (3,10) else '❌ Update Needed'}")

# 2. Check Fuzzy Matching (RapidFuzz)
ratio = fuzz.ratio("Amoxicillin", "Amoxycillin")
print(f"Fuzzy Matching: {ratio}% match - ✅ OK")

# 3. Check AI Interaction (Ollama)
try:
    # Testing with the smaller model you downloaded
    response = ollama.list()
    print("AI Model Interaction: ✅ Connected to Ollama")
except:
    print("AI Model Interaction: ❌ Ollama app not running")

# 4. Check UI Rendering (Streamlit)
print(f"Streamlit Version: {st.__version__} - ✅ OK")

print("\n--- ALL CORE MODULES IMPORTED SUCCESSFULLY ---")
