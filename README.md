# CodeAlpha Task 1 — Language Translation Tool

## Overview

A web app that translates text between 12 languages. You type or paste
text, pick a source and target language, and click **Translate** to get a
real translation from the MyMemory API by default.
It also supports swapping languages, copying the result, and a short
history of recent translations.

This is a real, working application — text you enter is actually sent to
a translation API over the network and the real response is shown. There
is no mock or hard-coded translation data anywhere in the code.

## Features

- Translate text between English, Urdu, Spanish, French, German, Arabic,
  Chinese, Japanese, Hindi, Portuguese, Russian, and Turkish
- Swap source/target languages with one click (and reuse the translated
  text as new input, to translate it back)
- Live character counter with a 5,000-character limit
- Copy-to-clipboard button with "Copied ✓" confirmation
- Recent-translations history (click one to reload it)
- Friendly error messages for empty input, network failures, timeouts,
  and API errors — no raw Python tracebacks shown to the user
- Loading state: the Translate button disables itself and shows a spinner
  while a request is in progress

## Technologies Used

- **Python 3.10+**
- **Streamlit** — chosen over Flask/FastAPI + HTML/JS because it lets a
  single Python file render a full interactive UI (dropdowns, text areas,
  buttons, session state) with no separate HTML/CSS/JS build step. For a
  learning project like this, that means less boilerplate and fewer moving
  parts, while still being a real, production-usable web framework.
- **requests** — for calling the translation API
- **python-dotenv** — for loading API configuration from a `.env` file
- **MyMemory API** — no-key translation for the default setup
- **LibreTranslate API** — optional self-hosted or managed provider

## Project Structure

```
CodeAlpha_Language_Translation/
│
├── app.py                       # Streamlit UI (layout & user interaction only)
├── src/
│   ├── __init__.py
│   ├── translation_service.py   # All API communication + error handling
│   └── languages.py             # Supported languages (name <-> code)
│
├── .streamlit/
│   └── config.toml              # Theme settings
├── .env.example                 # Template for required environment variables
├── .gitignore
├── requirements.txt
├── README.md
└── tests/
    ├── __init__.py
    └── test_translation.py      # Unit tests (mocked API calls)
```

## How It Works

```
User Input (text + languages)
        │
        ▼
   app.py (Streamlit UI)
        │  calls translate_text(text, source, target)
        ▼
src/translation_service.py
        │  builds the API request, reads TRANSLATION_API_URL / _KEY from .env
        ▼
  Translation API (MyMemory by default)
     │  returns a translated text response
        ▼
src/translation_service.py
        │  parses the response, raises a friendly error if anything's wrong
        ▼
   app.py displays the result (or the error message) in the UI
```

`app.py` never talks to the network directly — it only calls functions in
`translation_service.py`. That separation is what lets the API logic be
unit-tested without needing Streamlit or a real network connection (see
`tests/test_translation.py`).

## Installation

```bash
# 1. Clone or download this folder, then move into it
cd CodeAlpha_Language_Translation

# 2. (Recommended) create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Environment Variables

Copy the example file and edit it if needed:

```bash
cp .env.example .env
```

| Variable               | Required? | Description                                                                 |
|-------------------------|-----------|-------------------------------------------------------------------------------|
| `TRANSLATION_API_URL`   | No        | Full translation endpoint. Defaults to MyMemory if left unset; LibreTranslate URLs are also supported. |
| `TRANSLATION_API_KEY`   | No        | Only needed if your chosen API URL requires a key.                          |

No API keys are hard-coded anywhere in the source code — everything comes
from environment variables at runtime.

## API Setup

By default, this app uses the no-key MyMemory translation API, so it works
without any API setup. You can also use a LibreTranslate-compatible server:

1. **Do nothing (default).** MyMemory is used automatically and does not
   require an API key. Its free service has usage limits.
2. **Self-host LibreTranslate** (most reliable, runs on your own
   machine):
   ```bash
   pip install libretranslate
   libretranslate
   ```
   Then set in `.env`:
   ```
   TRANSLATION_API_URL=http://localhost:5000/translate
   ```
3. **Use a paid managed LibreTranslate instance** — get a key from
   [portal.libretranslate.com](https://portal.libretranslate.com) and set:
   ```
   TRANSLATION_API_URL=https://libretranslate.com/translate
   TRANSLATION_API_KEY=your-key-here
   ```

If the configured API ever becomes unreachable, the app will show a clear
"Translation service is temporarily unavailable" message instead of
crashing or showing a raw error.

## Running the Application

```bash
streamlit run app.py
```

Then open the URL Streamlit prints in your terminal (usually
`http://localhost:8501`).

To switch between light and dark mode, use Streamlit's built-in menu:
click the **⋮** icon in the top-right corner → **Settings** → **Theme**.

## Running the Tests

```bash
python -m unittest discover -s tests -v
```

or, if you have `pytest` installed:

```bash
pytest
```

The tests mock every network call, so they run instantly and don't depend
on the translation API being online. They cover: a valid translation
response, empty input, an invalid/unparseable API response, a
network/connection failure, a timeout, and language-name/code validation.

## Screenshots

_(Add screenshots here after running the app locally, e.g.
`![Main screen](screenshots/main.png)`)_

## Future Improvements

- Text-to-speech for the translated output
- Voice input for the source text
- More languages (just add entries to `src/languages.py`)
- Persist translation history in a small database instead of session memory
- User accounts to save history across sessions
- Offline translation using a locally-bundled model

## Internship

This project was developed as part of the **CodeAlpha AI Internship — Task 1**.
