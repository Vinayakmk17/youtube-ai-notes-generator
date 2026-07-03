"""
utils/transcript.py
--------------------
Robust YouTube transcript extraction.
Handles English, Hindi, auto-generated, and fallback to any available language.
Designed for easy migration to FastAPI later.
"""

from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    InvalidVideoId,
)


# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------

def extract_video_id(url: str) -> str | None:
    """
    Extracts the YouTube video ID from various URL formats.

    Supported formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://youtube.com/watch?v=VIDEO_ID
    
    Returns None if the URL is not a recognised YouTube link.
    """
    if not url or not url.strip():
        return None

    url = url.strip()
    parsed = urlparse(url)

    if parsed.hostname == "youtu.be":
        video_id = parsed.path.lstrip("/")
        return video_id if video_id else None

    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        return parse_qs(parsed.query).get("v", [None])[0]

    return None


# ---------------------------------------------------------------------------
# Transcript fetching
# ---------------------------------------------------------------------------

def get_transcript(video_id: str) -> dict:
    """
    Fetches the transcript for a YouTube video.

    Strategy (in order of priority):
        1. English transcript (manual or auto-generated).
        2. Hindi transcript.
        3. Kannada transcript.
        4. Any other available transcript (first found).

    Returns a dict with:
        - text (str | None):     The joined transcript text.
        - language (str | None): The language code of the fetched transcript.
        - error (str | None):    A user-friendly error message, or None on success.
    """
    api = YouTubeTranscriptApi()

    # --- Step 1: Try direct fetch with preferred language priority ----------
    preferred_languages = ["en", "hi", "kn"]

    for lang in preferred_languages:
        try:
            transcript = api.fetch(video_id, languages=[lang])
            text = " ".join(snippet.text for snippet in transcript)
            if text.strip():
                return {"text": text, "language": lang, "error": None}
        except (NoTranscriptFound, TranscriptsDisabled):
            continue  # try next language
        except InvalidVideoId:
            return {
                "text": None,
                "language": None,
                "error": "Invalid YouTube video ID. Please check the URL.",
            }
        except VideoUnavailable:
            return {
                "text": None,
                "language": None,
                "error": "This video is unavailable (private, deleted, or region-blocked).",
            }
        except Exception as exc:
            # Network or unexpected errors — stop immediately
            return {
                "text": None,
                "language": None,
                "error": f"Could not fetch transcript: {exc}",
            }

    # --- Step 2: Fallback — list all transcripts and pick the first one -----
    try:
        transcript_list = api.list(video_id)

        for t in transcript_list:
            fetched = t.fetch()
            text = " ".join(snippet.text for snippet in fetched)
            if text.strip():
                return {
                    "text": text,
                    "language": t.language_code,
                    "error": None,
                }

        # All transcripts were empty
        return {
            "text": None,
            "language": None,
            "error": "Transcripts exist but are empty for this video.",
        }

    except TranscriptsDisabled:
        return {
            "text": None,
            "language": None,
            "error": "Subtitles are disabled for this video.",
        }
    except Exception as exc:
        return {
            "text": None,
            "language": None,
            "error": f"Could not retrieve transcripts: {exc}",
        }
