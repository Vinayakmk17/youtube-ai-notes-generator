"""
utils/db.py
-----------
SQLite database layer for VidNote AI.
Handles:
  - learning_history  — auto-saved sessions with notes / quiz / flashcards / etc.
  - app_settings      — persistent user preferences
"""

import sqlite3
import json
import csv
import io
import os
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Database path — stored alongside the project
# ---------------------------------------------------------------------------
_DB_PATH = Path(__file__).parent.parent / "vidnote_ai.db"


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def _get_conn() -> sqlite3.Connection:
    """Returns a thread-safe SQLite connection with row factory."""
    conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Schema initialisation (called once at import time)
# ---------------------------------------------------------------------------

def init_db():
    """Creates tables if they don't exist."""
    conn = _get_conn()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS learning_history (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            youtube_url         TEXT    NOT NULL,
            video_id            TEXT    NOT NULL,
            video_title         TEXT    DEFAULT '',
            transcript_language TEXT    DEFAULT 'en',
            notes               TEXT    DEFAULT '',
            quiz                TEXT    DEFAULT '[]',
            flashcards          TEXT    DEFAULT '[]',
            interview_questions TEXT    DEFAULT '{}',
            practice_questions  TEXT    DEFAULT '{}',
            created_at          TEXT    NOT NULL,
            favorite            INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS app_settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)

    # Seed default settings if table is empty
    cur.execute("SELECT COUNT(*) FROM app_settings")
    if cur.fetchone()[0] == 0:
        defaults = {
            "output_language":   "English",
            "summary_length":    "Detailed",
            "ai_model":          "gemini-2.5-flash",
            "temperature":       "1.0",
            "export_format":     "PDF",
            "theme":             "Dark",
        }
        cur.executemany(
            "INSERT OR IGNORE INTO app_settings (key, value) VALUES (?, ?)",
            list(defaults.items()),
        )

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# History CRUD
# ---------------------------------------------------------------------------

def save_session(
    youtube_url: str,
    video_id: str,
    video_title: str,
    transcript_language: str,
    notes: str,
    quiz: list,
    flashcards: list,
    interview_questions: dict,
    practice_questions: dict,
) -> dict:
    """
    Saves a learning session.  Prevents exact duplicate (same video_id +
    created on same calendar day).
    Returns {'id': int, 'error': str|None}.
    """
    conn = _get_conn()
    cur = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute(
        "SELECT id FROM learning_history WHERE video_id=? AND created_at LIKE ?",
        (video_id, f"{today}%"),
    )
    existing = cur.fetchone()
    if existing:
        conn.close()
        return {"id": existing["id"], "error": None}

    now = datetime.now().isoformat(timespec="seconds")
    try:
        cur.execute(
            """INSERT INTO learning_history
               (youtube_url, video_id, video_title, transcript_language,
                notes, quiz, flashcards, interview_questions, practice_questions,
                created_at, favorite)
               VALUES (?,?,?,?,?,?,?,?,?,?,0)""",
            (
                youtube_url,
                video_id,
                video_title,
                transcript_language,
                notes,
                json.dumps(quiz or []),
                json.dumps(flashcards or []),
                json.dumps(interview_questions or {}),
                json.dumps(practice_questions or {}),
                now,
            ),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return {"id": new_id, "error": None}
    except Exception as exc:
        conn.close()
        return {"id": None, "error": str(exc)}


def update_session_content(session_id: int, field: str, value) -> bool:
    """Updates a single JSON field (quiz/flashcards/interview_questions/practice_questions/notes)."""
    allowed = {"notes", "quiz", "flashcards", "interview_questions", "practice_questions", "video_title"}
    if field not in allowed:
        return False
    conn = _get_conn()
    if field in {"quiz", "flashcards", "interview_questions", "practice_questions"}:
        value = json.dumps(value)
    conn.execute(f"UPDATE learning_history SET {field}=? WHERE id=?", (value, session_id))
    conn.commit()
    conn.close()
    return True


def get_all_sessions(search: str = "", favorite_only: bool = False, limit: int = 200) -> list[dict]:
    """Returns sessions matching search/filter, newest first."""
    conn = _get_conn()
    cur = conn.cursor()

    query = "SELECT * FROM learning_history WHERE 1=1"
    params: list = []

    if favorite_only:
        query += " AND favorite=1"
    if search:
        query += " AND (video_title LIKE ? OR youtube_url LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like])

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    rows = cur.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_session_by_id(session_id: int) -> dict | None:
    """Returns a single session or None."""
    conn = _get_conn()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM learning_history WHERE id=?", (session_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def toggle_favorite(session_id: int) -> bool:
    """Toggles the favorite flag. Returns the new state."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE learning_history SET favorite = 1-favorite WHERE id=?", (session_id,))
    conn.commit()
    new_val = cur.execute("SELECT favorite FROM learning_history WHERE id=?", (session_id,)).fetchone()
    conn.close()
    return bool(new_val["favorite"]) if new_val else False


def delete_session(session_id: int):
    """Deletes a single session."""
    conn = _get_conn()
    conn.execute("DELETE FROM learning_history WHERE id=?", (session_id,))
    conn.commit()
    conn.close()


def delete_all_sessions():
    """Deletes all sessions."""
    conn = _get_conn()
    conn.execute("DELETE FROM learning_history")
    conn.commit()
    conn.close()


def get_statistics() -> dict:
    """Returns aggregate statistics for the dashboard."""
    conn = _get_conn()
    cur = conn.cursor()

    total     = cur.execute("SELECT COUNT(*) FROM learning_history").fetchone()[0]
    favorites = cur.execute("SELECT COUNT(*) FROM learning_history WHERE favorite=1").fetchone()[0]
    langs     = cur.execute(
        "SELECT transcript_language, COUNT(*) as cnt FROM learning_history GROUP BY transcript_language"
    ).fetchall()
    recent_7d = cur.execute(
        "SELECT COUNT(*) FROM learning_history WHERE created_at >= date('now','-7 days')"
    ).fetchone()[0]
    conn.close()

    return {
        "total_sessions":   total,
        "favorites":        favorites,
        "recent_7_days":    recent_7d,
        "language_breakdown": {r["transcript_language"]: r["cnt"] for r in langs},
    }


def export_history_csv() -> bytes:
    """Exports history table as CSV bytes."""
    sessions = get_all_sessions(limit=10000)
    if not sessions:
        return b""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=sessions[0].keys())
    writer.writeheader()
    writer.writerows(sessions)
    return buf.getvalue().encode("utf-8")


# ---------------------------------------------------------------------------
# Settings CRUD
# ---------------------------------------------------------------------------

def get_setting(key: str, default: str = "") -> str:
    """Returns a setting value."""
    conn = _get_conn()
    row = conn.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value: str):
    """Upserts a setting."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO app_settings (key, value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )
    conn.commit()
    conn.close()


def get_all_settings() -> dict:
    """Returns all settings as a dict."""
    conn = _get_conn()
    rows = conn.execute("SELECT key, value FROM app_settings").fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}


# ---------------------------------------------------------------------------
# Module initialisation
# ---------------------------------------------------------------------------
init_db()
