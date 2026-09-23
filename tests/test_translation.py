"""
test_translation.py
--------------------
Tests for src/translation_service.py and src/languages.py.

These tests never make a real network call - they use unittest.mock to
stand in for `requests.post`, so the test suite is fast and doesn't depend
on any external service being online.

Built on Python's built-in `unittest` module (no extra install required),
but it also works fine if you run it with `pytest` instead.

Run with:
    python -m unittest discover -s tests
or:
    pytest
from the project root.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

# Make sure the project root (and therefore "src") is importable, whether
# these tests are run from the project root or from inside tests/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import languages
from src.translation_service import (
    EmptyTextError,
    TextTooLongError,
    TranslationServiceError,
    TranslationTimeoutError,
    translate_text,
)


def _mock_response(status_code=200, json_data=None, raise_on_json=False):
    """Build a fake `requests.Response`-like object for mocking."""
    response = MagicMock()
    response.status_code = status_code
    if raise_on_json:
        response.json.side_effect = ValueError("not valid json")
    else:
        response.json.return_value = json_data or {}
    return response


class TestTranslateText(unittest.TestCase):
    """Tests for translation_service.translate_text()."""

    @patch("src.translation_service.requests.post")
    def test_valid_translation_response(self, mock_post):
        mock_post.return_value = _mock_response(
            status_code=200, json_data={"translatedText": "Hola"}
        )

        result = translate_text("Hello", "en", "es")

        self.assertEqual(result, "Hola")
        mock_post.assert_called_once()

    @patch("src.translation_service.requests.post")
    def test_default_mymemory_response(self, mock_post):
        mock_post.return_value = _mock_response(
            status_code=200,
            json_data={"responseData": {"translatedText": "Hola"}},
        )

        result = translate_text("Hello", "en", "es")

        self.assertEqual(result, "Hola")
        mock_post.assert_called_once()
        self.assertEqual(
            mock_post.call_args.kwargs["data"],
            {"q": "Hello", "langpair": "en|es"},
        )

    def test_empty_input_raises_empty_text_error(self):
        with self.assertRaises(EmptyTextError):
            translate_text("", "en", "es")

    def test_whitespace_only_input_raises_empty_text_error(self):
        with self.assertRaises(EmptyTextError):
            translate_text("     ", "en", "es")

    def test_text_over_limit_raises_text_too_long_error(self):
        too_long = "a" * 6000
        with self.assertRaises(TextTooLongError):
            translate_text(too_long, "en", "es")

    @patch("src.translation_service.requests.post")
    def test_invalid_json_response_raises_service_error(self, mock_post):
        mock_post.return_value = _mock_response(status_code=200, raise_on_json=True)

        with self.assertRaises(TranslationServiceError):
            translate_text("Hello", "en", "es")

    @patch("src.translation_service.requests.post")
    def test_missing_translated_text_field_raises_service_error(self, mock_post):
        # Valid JSON, but missing the field we expect.
        mock_post.return_value = _mock_response(
            status_code=200, json_data={"unexpected": "shape"}
        )

        with self.assertRaises(TranslationServiceError):
            translate_text("Hello", "en", "es")

    @patch("src.translation_service.requests.post")
    def test_non_200_status_raises_service_error(self, mock_post):
        mock_post.return_value = _mock_response(status_code=500, json_data={})

        with self.assertRaises(TranslationServiceError):
            translate_text("Hello", "en", "es")

    @patch("src.translation_service.requests.post")
    def test_connection_error_raises_service_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError("no network")

        with self.assertRaises(TranslationServiceError):
            translate_text("Hello", "en", "es")

    @patch("src.translation_service.requests.post")
    def test_timeout_raises_timeout_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout("too slow")

        with self.assertRaises(TranslationTimeoutError):
            translate_text("Hello", "en", "es")


class TestLanguages(unittest.TestCase):
    """Tests for languages.py language-selection helpers."""

    def test_code_for_known_language(self):
        self.assertEqual(languages.code_for("Spanish"), "es")
        self.assertEqual(languages.code_for("Urdu"), "ur")

    def test_code_for_unknown_language_raises_value_error(self):
        with self.assertRaises(ValueError):
            languages.code_for("Klingon")

    def test_name_for_known_code(self):
        self.assertEqual(languages.name_for("fr"), "French")

    def test_name_for_unknown_code_returns_code_unchanged(self):
        self.assertEqual(languages.name_for("xx"), "xx")

    def test_is_supported(self):
        self.assertTrue(languages.is_supported("German"))
        self.assertFalse(languages.is_supported("Klingon"))

    def test_all_required_languages_present(self):
        required = {
            "English", "Urdu", "Spanish", "French", "German", "Arabic",
            "Chinese", "Japanese", "Hindi", "Portuguese", "Russian", "Turkish",
        }
        self.assertTrue(required.issubset(set(languages.LANGUAGE_NAMES)))


if __name__ == "__main__":
    unittest.main()
