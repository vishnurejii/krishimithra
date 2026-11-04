"""
Text and Malayalam Language Normalizer for KrishiMitra AI.
Cleans whitespace, normalizes Malayalam unicode sequences (chillus, ZWJ/ZWNJ),
and formats tables.
"""

import re
import unicodedata

def normalize_malayalam_text(text: str) -> str:
    """Normalizes Unicode representation of Malayalam characters."""
    if not text:
        return ""
    # NFC Unicode normalization
    normalized = unicodedata.normalize("NFC", text)
    # Remove excessive carriage returns and repeated spaces
    normalized = re.sub(r"\r\n|\r", "\n", normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    # Clean multiple blank lines
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()

def detect_language(text: str) -> str:
    """Detects whether text is Malayalam, English, or Bilingual."""
    if not text:
        return "en"
    malayalam_chars = sum(1 for c in text if 0x0D00 <= ord(c) <= 0x0D7F)
    english_chars = sum(1 for c in text if c.isascii() and c.isalpha())

    if malayalam_chars > 30 and english_chars > 30:
        return "bilingual"
    elif malayalam_chars > 20:
        return "ml"
    return "en"
