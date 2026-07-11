"""
pages/History.py
-----------------
Learning History dashboard — search, filter, statistics, favorites,
session restore, CSV export, and delete operations.
"""

import streamlit as st
import json
from utils.db import (
    get_all_sessions, get_session_by_id, toggle_favorite,
    delete_session, delete_all_sessions, get_statistics, export_history_csv,
)

# ── Shared CSS injected once ──────────────────────────────────────────────────
def _inject_css():
    st.markdown("""
    <style>
    .stat-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.15), rgba(118,75,162,0.15));
        border: 1px solid rgba(102,126,234,0.3);
        border-radius: 16px;
        padding: 1.2rem 1rem;
        text-align: center;
        backdrop-filter: blur(12px);
        margin-bottom: 0.5rem;
    }
    .stat-card .stat-number {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-card .stat-label {
        font-size: 0.85rem;
        color: #aaa;
        margin-top: 0.2rem;
    }
    .history-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        transition: border-color 0.2s;
    }
    .history-card:hover { border-color: rgba(102,126,234,0.5); }
    .history-card .card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #e8e8f0;
        margin-bottom: 0.3rem;
    }
    .history-card .card-meta {
        font-size: 0.78rem;
        color: #888;
    }
    .badge {
        display: inline-block;
        background: rgba(102,126,234,0.25);
        color: #a0aec0;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.72rem;
        margin-right: 6px;
    }
    .fav-badge {
        display: inline-block;
        background: rgba(255,193,7,0.2);
        color: #ffc107;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.72rem;
    }
    </style>
    """, unsafe_allow_html=True)


def _stat_card(number, label, icon="📊"):
    return f"""
    <div class="stat-card">
        <div style="font-size:1.6rem">{icon}</div>
        <div class="stat-number">{number}</div>
        <div class="stat-label">{label}</div>
    </div>
    """


def render_history():
    _inject_css()

    st.markdown("## 🗃️ Learning History")
    st.markdown("Browse, restore, and manage your past learning sessions.")
    st.divider()

    # ── Statistics ────────────────────────────────────────────────────────────
    stats = get_statistics()
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(_stat_card(stats["total_sessions"],  "Total Sessions",    "📚"), unsafe_allow_html=True)
    c2.markdown(_stat_card(stats["favorites"],        "Favourites",        "⭐"), unsafe_allow_html=True)
    c3.markdown(_stat_card(stats["recent_7_days"],    "Last 7 Days",       "📅"), unsafe_allow_html=True)
    lang_count = len(stats.get("language_breakdown", {}))
    c4.markdown(_stat_card(lang_count,                "Languages Studied", "🌐"), unsafe_allow_html=True)

    st.divider()

    # ── Filters ───────────────────────────────────────────────────────────────
    col_search, col_fav, col_csv, col_delall = st.columns([3, 1, 1, 1])

    with col_search:
        search_query = st.text_input("🔍 Search by title or URL", placeholder="e.g. Python tutorial", key="hist_search")
    with col_fav:
        favorites_only = st.checkbox("⭐ Favorites only", key="hist_fav")
    with col_csv:
        csv_bytes = export_history_csv()
        if csv_bytes:
            st.download_button(
                "📥 Export CSV",
                data=csv_bytes,
                file_name="vidnote_history.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.button("📥 Export CSV", disabled=True, use_container_width=True)
    with col_delall:
        if st.button("🗑️ Clear All", use_container_width=True, type="secondary"):
            st.session_state["confirm_delete_all"] = True

    # Confirmation dialog for delete all
    if st.session_state.get("confirm_delete_all"):
        st.warning("⚠️ This will permanently delete **all** sessions. Are you sure?")
        yes, no = st.columns(2)
        if yes.button("✅ Yes, Delete All", type="primary"):
            delete_all_sessions()
            st.session_state["confirm_delete_all"] = False
            st.success("All sessions deleted.")
            st.rerun()
        if no.button("❌ Cancel"):
            st.session_state["confirm_delete_all"] = False
            st.rerun()

    st.divider()

    # ── Session list ──────────────────────────────────────────────────────────
    sessions = get_all_sessions(search=search_query or "", favorite_only=favorites_only)

    if not sessions:
        st.info("📭 No sessions found. Generate some notes first!" if not search_query
                else f"No sessions match **{search_query}**.")
        return

    st.markdown(f"**{len(sessions)} session(s) found**")

    for s in sessions:
        fav_icon = "⭐" if s["favorite"] else "☆"
        title     = s["video_title"] or s["video_id"]
        lang      = s.get("transcript_language", "en")
        created   = s["created_at"][:10]
        has_quiz  = bool(json.loads(s.get("quiz", "[]") or "[]"))
        has_flash = bool(json.loads(s.get("flashcards", "[]") or "[]"))

        badges_html = ""
        if has_quiz:  badges_html += '<span class="badge">Quiz</span>'
        if has_flash: badges_html += '<span class="badge">Flashcards</span>'
        if s["favorite"]: badges_html += '<span class="fav-badge">⭐ Favourite</span>'

        with st.container():
            st.markdown(f"""
            <div class="history-card">
                <div class="card-title">🎬 {title}</div>
                <div class="card-meta">
                    📅 {created} &nbsp;|&nbsp; 🌐 {lang.upper()}
                </div>
                <div style="margin-top:0.5rem">{badges_html}</div>
            </div>
            """, unsafe_allow_html=True)

            action_cols = st.columns([2, 1, 1, 1])
            with action_cols[0]:
                st.caption(f"🔗 {s['youtube_url'][:60]}{'…' if len(s['youtube_url'])>60 else ''}")

            with action_cols[1]:
                if st.button(f"📂 Restore", key=f"restore_{s['id']}", use_container_width=True):
                    _restore_session(s)
                    st.success(f"✅ Session **{title}** restored! Switch to the main tab.")

            with action_cols[2]:
                fav_label = "⭐ Unfav" if s["favorite"] else "☆ Fav"
                if st.button(fav_label, key=f"fav_{s['id']}", use_container_width=True):
                    toggle_favorite(s["id"])
                    st.rerun()

            with action_cols[3]:
                if st.button("🗑️", key=f"del_{s['id']}", use_container_width=True):
                    delete_session(s["id"])
                    st.rerun()

            with st.expander(f"📄 Preview notes — {title}"):
                notes = s.get("notes", "")
                if notes:
                    st.markdown(notes[:2000] + ("…" if len(notes) > 2000 else ""))
                else:
                    st.info("No notes stored for this session.")

            st.divider()


def _restore_session(s: dict):
    """Loads a history session back into st.session_state."""
    st.session_state.video_id           = s["video_id"]
    st.session_state.youtube_url        = s["youtube_url"]
    st.session_state.notes_text         = s.get("notes", "")
    st.session_state.transcript_lang    = s.get("transcript_language", "en")
    st.session_state.video_title        = s.get("video_title", "")
    # Reset transcript text so user needs to regenerate (we didn't store full transcript)
    st.session_state.transcript_text    = s.get("notes", "")  # use notes as fallback context

    try:
        st.session_state.quiz_data          = json.loads(s.get("quiz", "[]") or "[]")
        st.session_state.flashcards_data    = json.loads(s.get("flashcards", "[]") or "[]")
        st.session_state.interview_data     = json.loads(s.get("interview_questions", "{}") or "{}")
        st.session_state.practice_data      = json.loads(s.get("practice_questions", "{}") or "{}")
    except Exception:
        pass


# ── Standalone page entry point ───────────────────────────────────────────────
if __name__ != "__main__":
    # Called as a Streamlit page
    render_history()
