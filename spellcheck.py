import time
import os
from spellchecker import SpellChecker
from google import genai
from difflib import SequenceMatcher
from dotenv import load_dotenv

load_dotenv()

spell = SpellChecker()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def preserve_case(original, corrected):
    """Match corrected word’s case with the original word"""
    if original.isupper():
        return corrected.upper()
    elif original[0].isupper():
        return corrected.capitalize()
    else:
        return corrected.lower()

def edit_distance(a, b):
    """Return simple edit distance between two strings"""
    return int(round((1 - SequenceMatcher(None, a, b).ratio()) * max(len(a), len(b))))


def gemini_correction(text: str):
    """Call Gemini API to correct text"""
    prompt = f"Correct the spelling and grammar of the following text but preserve the original capitalization and casing:\n{text}\nReturn only the corrected text."
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()


def correct_text(text: str):
    """Compare spellchecker and Gemini outputs and decide if fallback was needed"""
    start_time = time.time()

    # --- Step 1: Spellchecker correction ---
    words = text.split()
    corrected_words = []
    corrections_made = 0
    distances = []

    for word in words:
        corrected = spell.correction(word) or word
        corrected = preserve_case(word, corrected)
        corrected_words.append(corrected)
        if corrected.lower() != word.lower():
            corrections_made += 1
        distances.append(edit_distance(word.lower(), corrected.lower()))

    spell_corrected_text = " ".join(corrected_words)

    # --- Step 2: Gemini correction ---
    gemini_corrected_text = gemini_correction(text)

    # --- Step 3: Compare both results ---
    use_fallback = (spell_corrected_text.strip().lower() != gemini_corrected_text.strip().lower())

    # --- Step 4: Compute metrics only if fallback not used ---
    if not use_fallback:
        confidence = 1 - (corrections_made / len(words)) if words else 1
        accuracy = sum(
            1 for orig, corr in zip(words, corrected_words) if orig.lower() == corr.lower()
        ) / len(words) if words else 1
        confidence = round(confidence * 100, 2)
        accuracy = round(accuracy * 100, 2)
        final_corrected_text = spell_corrected_text
    else:
        confidence = None
        accuracy = None
        final_corrected_text = gemini_corrected_text

    end_time = time.time()
    time_taken = round(end_time - start_time, 2)

    # --- Step 5: Return structured output ---
    return {
        "original": text,
        "corrected": final_corrected_text,
        "confidence": confidence,
        "accuracy": accuracy,
        "used_fallback": use_fallback,
        "time_taken_seconds": time_taken
    }
