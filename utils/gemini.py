"""
utils/gemini.py
----------------
Gemini API wrapper using the modern google-genai SDK.
Centralises model configuration and provides helper functions
for text generation and (later) structured JSON generation.
"""

import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_API_KEY = os.getenv("GEMINI_API_KEY")

if not _API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY is not set. "
        "Create a .env file with GEMINI_API_KEY=your_key_here"
    )

_client = genai.Client(api_key=_API_KEY)

# Primary and fallback models
_PRIMARY_MODEL = "gemini-2.5-flash"
_FALLBACK_MODEL = "gemini-2.0-flash"

_MAX_RETRIES = 3
_INITIAL_BACKOFF_SECS = 5


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def generate_text(prompt: str) -> dict:
    """
    Sends a text prompt to Gemini and returns the result.
    Includes retry with exponential backoff for rate-limit (429) errors,
    and falls back to a secondary model if the primary model quota is exhausted.

    Returns a dict with:
        - text (str | None):  The generated content.
        - error (str | None): An error message, or None on success.
    """
    models_to_try = [_PRIMARY_MODEL, _FALLBACK_MODEL]

    for model_id in models_to_try:
        for attempt in range(_MAX_RETRIES):
            try:
                response = _client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                )
                return {"text": response.text, "error": None}
            except Exception as exc:
                error_str = str(exc)
                # Retry on rate-limit errors with exponential backoff
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait = _INITIAL_BACKOFF_SECS * (2 ** attempt)
                    if attempt < _MAX_RETRIES - 1:
                        time.sleep(wait)
                        continue
                    # Exhausted retries for this model — try fallback
                    break
                else:
                    # Non-rate-limit error — return immediately
                    return {"text": None, "error": f"Gemini API error: {exc}"}

    return {
        "text": None,
        "error": (
            "Gemini API quota exhausted. Please wait a minute and try again, "
            "or check your API plan at https://ai.google.dev."
        ),
    }

def generate_json(prompt: str) -> dict:
    """
    Sends a text prompt to Gemini and requests JSON output format.
    Returns a dict with:
        - data (str | None):  The generated JSON string.
        - error (str | None): An error message, or None on success.
    """
    models_to_try = [_PRIMARY_MODEL, _FALLBACK_MODEL]

    for model_id in models_to_try:
        for attempt in range(_MAX_RETRIES):
            try:
                response = _client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                return {"data": response.text, "error": None}
            except Exception as exc:
                error_str = str(exc)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait = _INITIAL_BACKOFF_SECS * (2 ** attempt)
                    if attempt < _MAX_RETRIES - 1:
                        time.sleep(wait)
                        continue
                    break
                else:
                    return {"data": None, "error": f"Gemini API error: {exc}"}

    return {
        "data": None,
        "error": (
            "Gemini API quota exhausted. Please wait a minute and try again."
        ),
    }
