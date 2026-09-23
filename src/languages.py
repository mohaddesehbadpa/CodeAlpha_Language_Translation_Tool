"""
languages.py
------------
Single source of truth for every language the app supports.

To add a new language later, add one line to LANGUAGES below —
the dropdowns, history section, and translation calls all read
from this dictionary automatically.
"""

# Display name -> ISO 639-1 language code used by the translation API.
LANGUAGES = {
    "English": "en",
    "Urdu": "ur",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Arabic": "ar",
    "Chinese": "zh",
    "Japanese": "ja",
    "Hindi": "hi",
    "Portuguese": "pt",
    "Russian": "ru",
    "Turkish": "tr",
}

# Convenience list, in the same order as the dict above (Python dicts keep
# insertion order), used to populate Streamlit dropdowns.
LANGUAGE_NAMES = list(LANGUAGES.keys())


def code_for(language_name: str) -> str:
    """
    Convert a display name to its ISO code, e.g. 'Spanish' -> 'es'.

    Raises:
        ValueError: if the language name is not supported.
    """
    try:
        return LANGUAGES[language_name]
    except KeyError as exc:
        raise ValueError(f"Unsupported language: {language_name!r}") from exc


def name_for(language_code: str) -> str:
    """
    Convert an ISO code back to its display name, e.g. 'es' -> 'Spanish'.
    Falls back to returning the code itself if it isn't recognized
    (this keeps the app from crashing on an unexpected code).
    """
    for name, code in LANGUAGES.items():
        if code == language_code:
            return name
    return language_code


def is_supported(language_name: str) -> bool:
    """Return True if `language_name` is one of our supported languages."""
    return language_name in LANGUAGES
