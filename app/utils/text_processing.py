"""
Text processing utilities for name normalization and comparison
"""
import re
import unicodedata
from typing import Tuple
from rapidfuzz import fuzz


def normalize_name(name: str) -> str:
    """
    Normalize name for comparison:
    - Convert to lowercase
    - Remove accents and diacritics
    - Remove extra whitespace
    - Remove special characters
    """
    if not name:
        return ""
    
    text = name.lower().strip()
    text = remove_accents(text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-z\s\-]', '', text)
    
    return text.strip()


def remove_accents(text: str) -> str:
    """Remove accents from text using Unicode normalization."""
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


def fuzzy_match_names(name1: str, name2: str, threshold: float = 85.0) -> Tuple[float, bool]:
    """Compare two names using fuzzy matching."""
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    
    if not norm1 or not norm2:
        return 0.0, False
    
    score = fuzz.token_sort_ratio(norm1, norm2)
    return float(score), score >= threshold


def combine_names(first_name: str, last_name: str) -> str:
    """Combine first and last names into full name."""
    parts = [part.strip() for part in [first_name, last_name] if part and part.strip()]
    return " ".join(parts)


def extract_document_number(text: str) -> str:
    """Extract document number from OCR text."""
    if not text:
        return ""
    
    # Spanish DNI/NIF pattern
    dni_pattern = r'\b(\d{8}[A-Z]|[A-Z]\d{7}[A-Z])\b'
    match = re.search(dni_pattern, text)
    if match:
        return match.group(1)
    
    return ""


def parse_username_email(email: str) -> tuple:
    """Parse an email-like username and return (first_name, last_name).

    Examples:
    - ibai.mutiloa@domain.tld -> ("Ibai", "Mutiloa")
    - j.perez@... -> ("J", "Perez")
    - juanperez@... -> ("Juanperez", "")
    """
    if not email or '@' not in email:
        return "", ""

    local = email.split('@', 1)[0]

    # Replace separators with a single space
    parts = re.split(r'[._\-\s]+', local)
    parts = [p for p in parts if p]

    if len(parts) == 0:
        return "", ""
    if len(parts) == 1:
        # Try to split camelcase or letters+surname heuristics
        name = parts[0]
        # If name contains digits, strip them
        name = re.sub(r"\d+", "", name)
        # Capitalize
        return name.capitalize(), ""

    # First element -> first name, last element -> last name
    first = parts[0].capitalize()
    last = parts[-1].capitalize()
    return first, last
