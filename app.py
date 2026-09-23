"""
app.py
------
Streamlit UI for the Language Translation Tool.

This file only handles LAYOUT and USER INTERACTION. All the actual API
communication lives in src/translation_service.py, and the list of
supported languages lives in src/languages.py. Keeping them separate
makes each piece easier to read, test, and change on its own.
"""

import json

import streamlit as st
import streamlit.components.v1 as components

from src.languages import LANGUAGE_NAMES, code_for
from src.translation_service import (
    MAX_TEXT_LENGTH,
    EmptyTextError,
    TextTooLongError,
    TranslationError,
    translate_text,
)

MAX_HISTORY_ITEMS = 8

st.set_page_config(
    page_title="Lingo | Language Translator",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# A little bit of CSS for spacing, rounded cards, and focus states.
# This deliberately avoids hard-coding text/background colors so that it
# still looks correct if the user switches Streamlit's built-in dark theme
# on from the Settings menu (top-right "⋮" menu -> Settings -> Theme).
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --ink: #111827;
        --muted: #64748b;
        --line: #e5e7eb;
        --panel: #ffffff;
        --violet: #635bff;
        --violet-dark: #5147e8;
        --mint: #dff8ef;
    }

    .stApp {
        background:
            radial-gradient(circle at 4% 0%, rgba(99, 91, 255, 0.09), transparent 26rem),
            radial-gradient(circle at 96% 18%, rgba(45, 212, 191, 0.08), transparent 24rem),
            #f7f8fc;
        color: var(--ink);
    }

    .block-container {
        max-width: 1180px;
        padding: 2.5rem 2.5rem 4rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    footer {
        visibility: hidden;
    }

    .hero {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 2rem;
        margin-bottom: 2.25rem;
    }

    .hero-copy {
        max-width: 690px;
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.42rem 0.72rem;
        border: 1px solid #dcd9ff;
        border-radius: 999px;
        background: #f2f1ff;
        color: #5147e8;
        font-size: 0.74rem;
        font-weight: 750;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .eyebrow-dot {
        width: 0.42rem;
        height: 0.42rem;
        border-radius: 999px;
        background: #22c55e;
        box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.14);
    }

    .hero h1 {
        margin: 1rem 0 0.55rem;
        color: #101828;
        font-size: clamp(2.15rem, 5vw, 4rem);
        font-weight: 780;
        letter-spacing: -0.055em;
        line-height: 0.98;
    }

    .hero p {
        max-width: 590px;
        margin: 0;
        color: #667085;
        font-size: 1.05rem;
        line-height: 1.65;
    }

    .section-label {
        margin: 0.15rem 0 0.7rem;
        color: #475467;
        font-size: 0.78rem;
        font-weight: 760;
        letter-spacing: 0.085em;
        text-transform: uppercase;
    }

    .language-panel,
    .editor-panel,
    .history-panel {
        border: 1px solid rgba(226, 232, 240, 0.95);
        border-radius: 1.25rem;
        background: rgba(255, 255, 255, 0.88);
        box-shadow: 0 14px 35px rgba(15, 23, 42, 0.055);
    }

    .language-panel {
        padding: 1.1rem 1.25rem 0.35rem;
        margin-bottom: 1.25rem;
    }

    .editor-panel {
        min-height: 19rem;
        padding: 1.1rem 1.2rem 0.9rem;
    }

    .editor-heading {
        display: flex;
        align-items: center;
        justify-content: space-between;
        min-height: 2.1rem;
        margin-bottom: 0.35rem;
    }

    .editor-heading strong {
        color: #111827;
        font-size: 1rem;
        font-weight: 720;
    }

    .editor-heading span {
        color: #98a2b3;
        font-size: 0.75rem;
        font-weight: 600;
    }

    div[data-testid="stTextArea"] textarea {
        min-height: 12.4rem;
        padding: 1rem 1.05rem;
        border: 1px solid #e5e7eb;
        border-radius: 0.9rem;
        background: #fbfcfe;
        color: #111827;
        font-size: 1rem;
        line-height: 1.65;
        resize: vertical;
        transition: border-color 150ms ease, box-shadow 150ms ease;
    }

    div[data-testid="stTextArea"] textarea:focus {
        border-color: #aaa5ff;
        box-shadow: 0 0 0 4px rgba(99, 91, 255, 0.1);
    }

    div[data-testid="stTextArea"] textarea:disabled {
        background: #f7f7ff;
        color: #344054;
        opacity: 1;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stTextArea"] label {
        color: #667085;
        font-size: 0.78rem;
        font-weight: 680;
    }

    div[data-baseweb="select"] > div {
        min-height: 2.8rem;
        border: 1px solid #e4e7ec;
        border-radius: 0.75rem;
        background: #fbfcfe;
    }

    div[data-testid="stButton"] button {
        min-height: 2.8rem;
        border-radius: 0.75rem;
        font-weight: 700;
        transition: transform 150ms ease, box-shadow 150ms ease, border-color 150ms ease;
    }

    div[data-testid="stButton"] button:hover {
        transform: translateY(-1px);
    }

    div[data-testid="stButton"] button[kind="primary"] {
        border: 0;
        background: linear-gradient(135deg, var(--violet), var(--violet-dark));
        box-shadow: 0 10px 18px rgba(99, 91, 255, 0.23);
    }

    div[data-testid="stButton"] button[kind="secondary"] {
        border: 1px solid #e4e7ec;
        background: #ffffff;
        color: #344054;
    }

    div[data-testid="stButton"] button:focus-visible {
        outline: 3px solid rgba(99, 91, 255, 0.3);
        outline-offset: 2px;
    }

    .char-counter {
        display: flex;
        justify-content: flex-end;
        margin: 0.45rem 0 0;
        color: #98a2b3;
        font-size: 0.73rem;
        font-weight: 600;
    }

    .helper-copy {
        margin: 0.65rem 0 0;
        color: #98a2b3;
        font-size: 0.75rem;
    }

    .history-title {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin: 2.2rem 0 0.9rem;
    }

    .history-title h2 {
        margin: 0;
        color: #101828;
        font-size: 1.2rem;
        letter-spacing: -0.02em;
    }

    .history-title span {
        color: #98a2b3;
        font-size: 0.78rem;
    }

    .history-card {
        padding: 0.95rem 1rem;
        border: 1px solid #eaecf0;
        border-radius: 0.95rem;
        background: rgba(255, 255, 255, 0.75);
        margin-bottom: 0.7rem;
    }

    .history-route {
        color: #5147e8;
        font-size: 0.75rem;
        font-weight: 760;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .history-preview {
        overflow: hidden;
        margin: 0.35rem 0 0.7rem;
        color: #475467;
        font-size: 0.9rem;
        line-height: 1.45;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .footer {
        margin-top: 2rem;
        padding-top: 1.2rem;
        border-top: 1px solid #e4e7ec;
        color: #98a2b3;
        font-size: 0.75rem;
        line-height: 1.6;
    }

    @media (max-width: 720px) {
        .block-container { padding: 1.5rem 1rem 3rem; }
        .hero { margin-bottom: 1.5rem; }
        .hero h1 { font-size: 2.45rem; }
        .hero p { font-size: 0.95rem; }
        .editor-panel { padding: 0.85rem 0.85rem 0.7rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state - Streamlit reruns this whole script on every interaction,
# so anything that needs to survive between reruns (typed text, results,
# history, ...) has to live in st.session_state instead of a normal variable.
# ---------------------------------------------------------------------------
defaults = {
    "source_lang": "English",
    "target_lang": "Urdu",
    "input_text": "",
    "output_text": "",
    "error_message": "",
    "is_translating": False,
    "history": [],  # list of dicts: source, target, original, translated
    "just_copied_output": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def copy_button(text_to_copy: str, key: str, label: str = "Copy"):
    """
    Renders a small button that copies `text_to_copy` to the clipboard
    using the browser's Clipboard API, and briefly shows "Copied ✓".

    Streamlit doesn't have a built-in "copy to clipboard" widget for
    arbitrary text, so this uses a tiny embedded HTML/JS snippet instead.
    """
    safe_text = json.dumps(text_to_copy)  # safely escape text for JS
    html_code = f"""
    <button id="copy-btn-{key}" style="
        width: 100%;
        padding: 0.62rem 0.75rem;
        border-radius: 10px;
        border: 1px solid #dedcff;
        background: #f5f4ff;
        color: #5147e8;
        cursor: pointer;
        font-family: sans-serif;
        font-size: 0.82rem;
        font-weight: 700;
    ">{label}</button>
    <script>
    const btn = document.getElementById("copy-btn-{key}");
    btn.addEventListener("click", async () => {{
        try {{
            await navigator.clipboard.writeText({safe_text});
            btn.innerText = "Copied \\u2713";
            setTimeout(() => {{ btn.innerText = "{label}"; }}, 1500);
        }} catch (err) {{
            btn.innerText = "Copy failed";
            setTimeout(() => {{ btn.innerText = "{label}"; }}, 1500);
        }}
    }});
    </script>
    """
    components.html(html_code, height=44)


def add_to_history(source_name, target_name, original, translated):
    st.session_state.history.insert(
        0,
        {
            "source": source_name,
            "target": target_name,
            "original": original,
            "translated": translated,
        },
    )
    st.session_state.history = st.session_state.history[:MAX_HISTORY_ITEMS]


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-copy">
            <h1>Say it in any language.</h1>
            <p>Translate ideas clearly and naturally between 12 languages, with a clean workspace built for getting words right.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Language selectors + swap button
# ---------------------------------------------------------------------------
st.markdown('<div class="section-label">Choose your languages</div>', unsafe_allow_html=True)
with st.container(border=True):
    col_source, col_swap, col_target = st.columns([5, 1, 5])

    with col_source:
        st.selectbox(
            "From",
            options=LANGUAGE_NAMES,
            key="source_lang",
        )

    with col_swap:
        st.markdown("<div style='height: 1.8rem'></div>", unsafe_allow_html=True)
        if st.button("⇄", help="Swap source and target languages", use_container_width=True):
            st.session_state.source_lang, st.session_state.target_lang = (
                st.session_state.target_lang,
                st.session_state.source_lang,
            )
            # If we already have a translation, move it into the input box so
            # the user can translate it back the other way.
            if st.session_state.output_text:
                st.session_state.input_text = st.session_state.output_text
                st.session_state.output_text = ""
            st.rerun()

    with col_target:
        st.selectbox(
            "To",
            options=LANGUAGE_NAMES,
            key="target_lang",
        )

if st.session_state.source_lang == st.session_state.target_lang:
    st.warning("Choose two different languages to translate.")

# ---------------------------------------------------------------------------
# Input / output text areas
# ---------------------------------------------------------------------------
st.markdown('<div class="section-label">Translate your text</div>', unsafe_allow_html=True)
col_input, col_output = st.columns(2)

with col_input:
    st.markdown(
        '<div class="editor-heading"><strong>Original text</strong><span>Input</span></div>',
        unsafe_allow_html=True,
    )
    st.text_area(
        "Text to translate",
        height=200,
        max_chars=MAX_TEXT_LENGTH,
        placeholder="Write or paste your text here...",
        key="input_text",
        label_visibility="collapsed",
    )
    st.markdown(
        f'<div class="char-counter">{len(st.session_state.input_text)} / {MAX_TEXT_LENGTH} characters</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="helper-copy">Tip: preserve line breaks to keep the same rhythm in your translation.</p>',
        unsafe_allow_html=True,
    )

with col_output:
    st.markdown(
        '<div class="editor-heading"><strong>Translation</strong><span>Output</span></div>',
        unsafe_allow_html=True,
    )
    st.text_area(
        "Translation",
        value=st.session_state.output_text,
        height=200,
        disabled=True,
        placeholder="Your translation will appear here.",
        label_visibility="collapsed",
    )
    if st.session_state.output_text:
        copy_button(st.session_state.output_text, key="output")
    else:
        st.markdown(
            '<p class="helper-copy">Your translated text will appear here.</p>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Action buttons
# ---------------------------------------------------------------------------
st.markdown("<div style='height: 0.35rem'></div>", unsafe_allow_html=True)
col_translate, col_clear = st.columns([3, 1])

with col_translate:
    translate_clicked = st.button(
        "✦  Translate" if not st.session_state.is_translating else "Translating...",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.is_translating,
    )

with col_clear:
    if st.button("Clear text", use_container_width=True):
        st.session_state.input_text = ""
        st.session_state.output_text = ""
        st.session_state.error_message = ""
        st.rerun()

# ---------------------------------------------------------------------------
# Translation logic
#
# This runs in two steps across two reruns:
#   1. The button is clicked -> we validate input, set is_translating=True,
#      and rerun. On this rerun the button re-renders as disabled, which is
#      what gives the visible "loading" state.
#   2. On that rerun, is_translating is True, so we actually call the API
#      inside a spinner, store the result (or error), reset the flag, and
#      rerun once more to show the final state.
# ---------------------------------------------------------------------------
if translate_clicked and not st.session_state.is_translating:
    st.session_state.error_message = ""
    text = st.session_state.input_text

    if not text or not text.strip():
        st.session_state.error_message = "Please enter some text to translate."
    elif st.session_state.source_lang == st.session_state.target_lang:
        st.session_state.error_message = "Please choose two different languages."
    else:
        st.session_state.is_translating = True
        st.rerun()

if st.session_state.is_translating:
    with st.spinner("Translating..."):
        try:
            source_code = code_for(st.session_state.source_lang)
            target_code = code_for(st.session_state.target_lang)
            result = translate_text(
                st.session_state.input_text, source_code, target_code
            )
            st.session_state.output_text = result
            add_to_history(
                st.session_state.source_lang,
                st.session_state.target_lang,
                st.session_state.input_text,
                result,
            )
        except (EmptyTextError, TextTooLongError, TranslationError) as exc:
            # All of our custom exceptions already carry a friendly,
            # user-safe message - never show raw Python/API errors.
            st.session_state.error_message = str(exc)
        finally:
            st.session_state.is_translating = False
    st.rerun()

if st.session_state.error_message:
    st.error(st.session_state.error_message)

# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------
if st.session_state.history:
    st.markdown(
        f"""
        <div class="history-title">
            <h2>Recent translations</h2>
            <span>{len(st.session_state.history)} saved in this session</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for i, item in enumerate(st.session_state.history):
        preview = (
            item["original"]
            if len(item["original"]) <= 110
            else item["original"][:110] + "…"
        )
        with st.container(border=True):
            history_copy, history_action = st.columns([5, 1])
            with history_copy:
                st.markdown(
                    f'<div class="history-route">{item["source"]} <span style="color:#98a2b3">→</span> {item["target"]}</div>'
                    f'<div class="history-preview">{preview}</div>',
                    unsafe_allow_html=True,
                )
            with history_action:
                if st.button("Reuse", key=f"history_{i}", use_container_width=True):
                    st.session_state.source_lang = item["source"]
                    st.session_state.target_lang = item["target"]
                    st.session_state.input_text = item["original"]
                    st.session_state.output_text = item["translated"]
                    st.session_state.error_message = ""
                    st.rerun()

