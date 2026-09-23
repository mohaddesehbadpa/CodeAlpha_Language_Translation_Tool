"""
translation_service.py
-----------------------
Everything related to talking to the translation API lives in this file.
Keeping it separate from app.py (the UI) means:
  - the UI code stays simple and focused on layout,
  - this module can be tested on its own (see tests/test_translation.py),
  - the API could be swapped for a different provider later by only
    editing this one file.

The default uses the no-key MyMemory API. A LibreTranslate-compatible server
can still be selected with TRANSLATION_API_URL. See the README for details.
"""

import os

import requests
from dotenv import load_dotenv

# Load variables from a local .env file (if present) into the environment.
load_dotenv()

# Used when the user has not set TRANSLATION_API_URL. Unlike the old public
# LibreTranslate mirror, this endpoint is currently usable without a key.
DEFAULT_API_URL = "https://api.mymemory.translated.net/get"

REQUEST_TIMEOUT_SECONDS = 10
MAX_TEXT_LENGTH = 5000


class TranslationError(Exception):
    """Base class for every error this module can raise."""


class EmptyTextError(TranslationError):
    """Raised when the text to translate is empty or only whitespace."""


class TextTooLongError(TranslationError):
    """Raised when the text exceeds MAX_TEXT_LENGTH characters."""


class TranslationTimeoutError(TranslationError):
    """Raised when the translation API does not respond in time."""


class TranslationServiceError(TranslationError):
    """
    Raised when the API is unreachable, returns an error status code,
    or sends back a response we can't understand.
    """


def _get_api_config() -> tuple[str, str]:
    """
    Read the API URL and (optional) API key from environment variables.
    Falls back to DEFAULT_API_URL if TRANSLATION_API_URL isn't set.
    """
    api_url = os.getenv("TRANSLATION_API_URL", DEFAULT_API_URL).strip()
    api_key = os.getenv("TRANSLATION_API_KEY", "").strip()
    return api_url, api_key


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate `text` from `source_lang` to `target_lang` using the
    configured translation API.

    Args:
        text: The text to translate.
        source_lang: ISO 639-1 code of the source language (e.g. "en"),
            or "auto" to let the API detect it.
        target_lang: ISO 639-1 code to translate into (e.g. "es").

    Returns:
        The translated text.

    Raises:
        EmptyTextError: `text` is empty or whitespace-only.
        TextTooLongError: `text` is longer than MAX_TEXT_LENGTH characters.
        TranslationTimeoutError: the API took too long to respond.
        TranslationServiceError: the API is unreachable, returned an
            error, or sent back a response we couldn't parse.
    """
    if not text or not text.strip():
        raise EmptyTextError("Please enter some text to translate.")

    if len(text) > MAX_TEXT_LENGTH:
        raise TextTooLongError(
            f"Text is too long ({len(text)} characters). "
            f"Please shorten it to {MAX_TEXT_LENGTH} characters or fewer."
        )

    api_url, api_key = _get_api_config()

    using_mymemory = api_url.rstrip("/") == DEFAULT_API_URL.rstrip("/")
    if using_mymemory:
        payload = {"q": text, "langpair": f"{source_lang}|{target_lang}"}
    else:
        payload = {
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text",
        }
    if api_key:
        payload["api_key"] = api_key

    try:
        response = requests.post(api_url, data=payload, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.exceptions.Timeout as exc:
        raise TranslationTimeoutError(
            "The translation service took too long to respond. Please try again."
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        raise TranslationServiceError(
            "Could not reach the translation service. Please check your "
            "internet connection and try again."
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise TranslationServiceError(
            "Translation service is temporarily unavailable. Please try again."
        ) from exc

    if response.status_code != 200:
        raise TranslationServiceError(
            "Translation service is temporarily unavailable. Please try again."
        )

    try:
        data = response.json()
        if "responseData" in data:
            translated = data["responseData"]["translatedText"]
        else:
            translated = data["translatedText"]
    except (ValueError, KeyError) as exc:
        # ValueError -> response wasn't valid JSON.
        # KeyError -> JSON was valid but didn't have the field we expect.
        raise TranslationServiceError(
            "Received an unexpected response from the translation service."
        ) from exc

    if not isinstance(translated, str) or not translated.strip():
        raise TranslationServiceError(
            "The translation service returned an empty result."
        )

    return translated
