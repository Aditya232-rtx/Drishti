"""Model routing logic to choose between light and heavy LLMs."""
import re


INDIC_LANGS = {"hi", "bn", "mr", "ta", "te", "gu", "kn", "ml", "or", "pa"}

HEAVY_KEYWORDS = [
    "step by step",
    "detailed",
    "detail",
    "explain",
    "code",
    "algorithm",
    "complex",
    "advanced",
]


def choose_model(user_text: str, lang_code: str) -> str:
    """
    Decide between 'light' (Sarvam-1) and 'heavy' (Llama 3.1 8B).
    
    Rules:
      - If len(text) > 300 chars -> 'heavy'
      - If text contains heavy keywords -> 'heavy'
      - If lang_code is Indic AND text length <= 300 -> 'light'
      - Otherwise default to 'heavy'
    
    Args:
        user_text: User input text
        lang_code: Detected language code
    
    Returns:
        'light' or 'heavy'
    """
    text_lower = user_text.lower()
    
    # Rule 1: Long text -> heavy
    if len(user_text) > 300:
        return "heavy"
    
    # Rule 2: Heavy keywords -> heavy
    for keyword in HEAVY_KEYWORDS:
        if keyword in text_lower:
            return "heavy"
    
    # Rule 3: Short Indic text -> light
    if lang_code in INDIC_LANGS and len(user_text) <= 300:
        return "light"
    
    # Default: heavy
    return "heavy"
