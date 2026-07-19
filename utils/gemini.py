"""
utils/gemini.py
----------------
Gemini API wrapper using the modern google-genai SDK.
Centralises model configuration and provides helper functions
for text generation and structured JSON generation.
Supports dynamic model selection from app settings.
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

# Primary and fallback models (overridable via get_model_from_settings)
_PRIMARY_MODEL  = "gemini-2.5-flash"
_FALLBACK_MODEL = "gemini-2.0-flash"

_MAX_RETRIES          = 3
_INITIAL_BACKOFF_SECS = 5


# ---------------------------------------------------------------------------
# Dynamic model resolution
# ---------------------------------------------------------------------------

def _resolve_models() -> list[str]:
    """
    Returns an ordered list of models to try.
    Reads from app settings if available; falls back to defaults.
    """
    try:
        from utils.db import get_setting
        primary = get_setting("ai_model", _PRIMARY_MODEL)
    except Exception:
        primary = _PRIMARY_MODEL

    models = [primary]
    # Add fallback only if it's different from primary
    if _FALLBACK_MODEL != primary:
        models.append(_FALLBACK_MODEL)
    return models


def _resolve_temperature() -> float:
    """Reads temperature from settings."""
    try:
        from utils.db import get_setting
        return float(get_setting("temperature", "1.0"))
    except Exception:
        return 1.0


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def generate_text(prompt: str, temperature: float | None = None) -> dict:
    """
    Sends a text prompt to Gemini and returns the result.
    Includes retry with exponential backoff for rate-limit (429) errors,
    and falls back to a secondary model if the primary model quota is exhausted.

    Args:
        prompt:      The text prompt.
        temperature: Override temperature (default: reads from settings).

    Returns a dict with:
        - text (str | None):  The generated content.
        - error (str | None): An error message, or None on success.
    """
    models_to_try = _resolve_models()
    temp = temperature if temperature is not None else _resolve_temperature()

    for model_id in models_to_try:
        for attempt in range(_MAX_RETRIES):
            try:
                response = _client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        temperature=temp,
                    ),
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

def generate_text_stream(prompt: str):
    """
    Yields chunks of text from the Gemini model.
    Yields a dict with {"text": chunk} on success.
    Yields {"error": msg} on failure.
    """
    models_to_try = _resolve_models()
    temp = _resolve_temperature()
    
    for model_id in models_to_try:
        try:
            response = _client.models.generate_content_stream(
                model=model_id,
                contents=prompt,
                config=genai.types.GenerateContentConfig(temperature=temp),
            )
            for chunk in response:
                yield {"text": chunk.text, "error": None}
            return
        except Exception as exc:
            pass
            
    yield {"text": None, "error": "Gemini API exhausted or failed."}

def generate_json(prompt: str) -> dict:
    """
    Sends a text prompt to Gemini and requests JSON output format.
    Returns a dict with:
        - data (str | None):  The generated JSON string.
        - error (str | None): An error message, or None on success.
    """
    models_to_try = _resolve_models()
    temp = _resolve_temperature()

    for model_id in models_to_try:
        for attempt in range(_MAX_RETRIES):
            try:
                response = _client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=temp,
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
