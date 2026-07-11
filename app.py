"""
app.py — VidNote AI v2.0
=========================
Main Streamlit application entry point.
Phase 7: Premium dark glassmorphism SaaS UI with all features integrated.
"""

import streamlit as st
import json
import pyperclip

from utils.transcript import extract_video_id, get_transcript
from utils.gemini import generate_text
from utils.prompts import (
    get_notes_prompt,
    get_study_planner_prompt,
    get_mind_map_prompt,
    get_revision_notes_prompt,
)
from utils.db import (
    init_db, save_session, update_session_content,
    get_all_sessions, get_setting, get_statistics,
)

# ---------------------------------------------------------------------------
# Streamlit page config (must be first)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="VidNote AI — YouTube Learning Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com",
        "Report a bug": "https://github.com",
        "About": "VidNote AI v2.0 — AI-powered YouTube learning assistant",
    },
)

# Ensure DB is initialised
init_db()

# ---------------------------------------------------------------------------
# Premium CSS — Dark Glassmorphism Theme
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Root variables ───────────────────────────────────────────── */
:root {
    --primary:    #667eea;
    --secondary:  #764ba2;
    --accent:     #f093fb;
    --bg-dark:    #0d0d1a;
    --bg-card:    rgba(255,255,255,0.04);
    --border:     rgba(255,255,255,0.09);
    --text:       #e8e8f0;
    --text-muted: #888;
    --success:    #34d399;
    --warning:    #fbbf24;
    --error:      #f87171;
    --radius:     16px;
}

/* ── Global ───────────────────────────────────────────────────── */
* { font-family: 'Inter', sans-serif !important; }

.stApp { background: var(--bg-dark) !important; }

/* Animated gradient background */
.stApp::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at 20% 20%, rgba(102,126,234,0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(118,75,162,0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 50%, rgba(240,147,251,0.04) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ──────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(13,13,26,0.95) !important;
    border-right: 1px solid rgba(102,126,234,0.2) !important;
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--text) !important;
}

/* ── Hero section ─────────────────────────────────────────────── */
.hero {
    text-align: center;
    padding: 1.5rem 0 0.5rem;
    position: relative;
}
.hero-title {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 0.5rem;
}
.hero-sub {
    color: var(--text-muted);
    font-size: 1.05rem;
    max-width: 540px;
    margin: 0 auto 0.5rem;
    line-height: 1.6;
}
.hero-badges {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin: 0.5rem 0;
}
.badge {
    background: rgba(102,126,234,0.15);
    border: 1px solid rgba(102,126,234,0.3);
    color: #a78bfa;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.78rem;
    font-weight: 600;
}

/* ── URL Input ────────────────────────────────────────────────── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(102,126,234,0.3) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-size: 1rem !important;
    padding: 0.8rem 1rem !important;
    transition: border-color 0.3s, box-shadow 0.3s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(102,126,234,0.15) !important;
}

/* ── Buttons ──────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s !important;
    position: relative;
    overflow: hidden;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(102,126,234,0.4) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Secondary buttons */
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: var(--text) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.1) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
}

/* ── Download buttons ─────────────────────────────────────────── */
.stDownloadButton > button {
    background: rgba(52,211,153,0.15) !important;
    border: 1px solid rgba(52,211,153,0.3) !important;
    color: var(--success) !important;
    border-radius: 12px !important;
    transition: all 0.3s !important;
}
.stDownloadButton > button:hover {
    background: rgba(52,211,153,0.25) !important;
    transform: translateY(-1px) !important;
}

/* ── Tabs ─────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 14px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 10px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    font-weight: 700 !important;
}

/* ── Cards ────────────────────────────────────────────────────── */
.glass-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    backdrop-filter: blur(12px);
    transition: border-color 0.3s, transform 0.2s;
    margin-bottom: 1rem;
}
.glass-card:hover {
    border-color: rgba(102,126,234,0.4);
}

/* ── Stats mini cards ─────────────────────────────────────────── */
.mini-stat {
    background: linear-gradient(135deg, rgba(102,126,234,0.12), rgba(118,75,162,0.08));
    border: 1px solid rgba(102,126,234,0.2);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.mini-stat .num {
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.mini-stat .lbl { color: var(--text-muted); font-size: 0.78rem; margin-top: 0.2rem; }

/* ── Success / Info / Error boxes ─────────────────────────────── */
.stSuccess { border-radius: 12px !important; }
.stError   { border-radius: 12px !important; }
.stInfo    { border-radius: 12px !important; }
.stWarning { border-radius: 12px !important; }

/* ── Spinner ──────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--primary) !important; }

/* ── Expander ─────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}

/* ── Copy button ──────────────────────────────────────────────── */
.copy-btn {
    display: inline-block;
    background: rgba(102,126,234,0.15);
    border: 1px solid rgba(102,126,234,0.3);
    color: #a78bfa;
    border-radius: 8px;
    padding: 3px 10px;
    font-size: 0.78rem;
    cursor: pointer;
    transition: all 0.2s;
}
.copy-btn:hover { background: rgba(102,126,234,0.3); }

/* ── Footer ───────────────────────────────────────────────────── */
.footer {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.82rem;
    padding: 1.5rem 0 0.5rem;
    border-top: 1px solid var(--border);
    margin-top: 2rem;
}
.footer a { color: var(--primary); text-decoration: none; }

/* ── Loading skeleton animation ───────────────────────────────── */
@keyframes shimmer {
    0%   { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}
.skeleton {
    background: linear-gradient(90deg,
        rgba(255,255,255,0.04) 25%,
        rgba(255,255,255,0.08) 50%,
        rgba(255,255,255,0.04) 75%);
    background-size: 1000px 100%;
    animation: shimmer 2s infinite;
    border-radius: 8px;
    height: 16px;
    margin-bottom: 8px;
}

/* ── Progress bar ─────────────────────────────────────────────── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:1rem 0 0.5rem">
        <div style="font-size:2.2rem">🎬</div>
        <div style="font-size:1.15rem; font-weight:800; background:linear-gradient(135deg,#667eea,#764ba2);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">VidNote AI</div>
        <div style="color:#666; font-size:0.75rem; margin-top:2px">v2.0 · Powered by Gemini</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("**🧭 Navigation**")
    st.page_link("app.py",              label="🏠 Home / Generate Notes")
    st.page_link("pages/Chat.py",       label="💬 AI Chat Tutor")
    st.page_link("pages/History.py",    label="🗃️ Learning History")
    st.page_link("pages/Settings.py",   label="⚙️ Settings")
    st.page_link("pages/About.py",      label="ℹ️ About")

    st.divider()

    # Quick stats
    try:
        stats = get_statistics()
        st.markdown("**📊 Your Stats**")
        c1, c2 = st.columns(2)
        c1.markdown(f"""
        <div class="mini-stat">
            <div class="num">{stats['total_sessions']}</div>
            <div class="lbl">Sessions</div>
        </div>""", unsafe_allow_html=True)
        c2.markdown(f"""
        <div class="mini-stat">
            <div class="num">{stats['favorites']}</div>
            <div class="lbl">Favorites</div>
        </div>""", unsafe_allow_html=True)
    except Exception:
        pass

    # Recently viewed
    try:
        recent = get_all_sessions(limit=3)
        if recent:
            st.divider()
            st.markdown("**🕐 Recently Viewed**")
            for s in recent:
                title = s.get("video_title") or s["video_id"]
                short = title[:28] + "…" if len(title) > 28 else title
                fav   = "⭐ " if s["favorite"] else ""
                st.caption(f"{fav}{short}")
    except Exception:
        pass

    st.divider()
    st.markdown("""
    <div style="font-size:0.72rem; color:#444; text-align:center;">
        Made with ❤️ using Streamlit<br>& Google Gemini
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
defaults = {
    "transcript_text":   None,
    "transcript_lang":   None,
    "video_id":          None,
    "video_title":       "",
    "youtube_url":       "",
    "notes_text":        None,
    "quiz_data":         None,
    "flashcards_data":   None,
    "interview_data":    None,
    "practice_data":     None,
    "study_plan":        None,
    "mind_map":          None,
    "revision_notes":    None,
    "_session_db_id":    None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ---------------------------------------------------------------------------
# Hero Section
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="hero-title">🎬 VidNote AI</div>
    <div class="hero-sub">
        Paste any YouTube URL and instantly get AI-powered study notes,
        quizzes, flashcards, interview prep & more.
    </div>
    <div class="hero-badges">
        <span class="badge">⚡ Powered by Gemini 2.5</span>
        <span class="badge">📚 10+ Learning Tools</span>
        <span class="badge">📥 PDF / DOCX / TXT Export</span>
        <span class="badge">💬 AI Chat Tutor</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()


# ---------------------------------------------------------------------------
# URL Input section
# ---------------------------------------------------------------------------
col_url, col_btn = st.columns([5, 1])
with col_url:
    youtube_url = st.text_input(
        "🔗 YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        label_visibility="collapsed",
        key="url_input",
        value=st.session_state.youtube_url or "",
    )
with col_btn:
    generate_clicked = st.button("✨ Generate", type="primary", use_container_width=True)


# ---------------------------------------------------------------------------
# Processing pipeline
# ---------------------------------------------------------------------------
from pages.Quiz       import render_quiz
from pages.Flashcards import render_flashcards
from pages.Interview  import render_interview
from pages.Practice   import render_practice
from utils.export     import export_txt, export_pdf, export_docx

if generate_clicked:
    # 1 — Validate URL
    if not youtube_url or not youtube_url.strip():
        st.error("⚠️ Please enter a YouTube URL.")
        st.stop()

    video_id = extract_video_id(youtube_url)
    if not video_id:
        st.error(
            "❌ Invalid YouTube URL. Use a link like "
            "`https://www.youtube.com/watch?v=VIDEO_ID` or `https://youtu.be/VIDEO_ID`."
        )
        st.stop()

    st.session_state.video_id   = video_id
    st.session_state.youtube_url = youtube_url

    # 2 — Fetch transcript
    progress_bar = st.progress(0, text="📥 Fetching transcript…")

    with st.spinner("📥 Fetching transcript…"):
        result = get_transcript(video_id)

    if result["error"]:
        st.error(f"🚫 {result['error']}")
        st.stop()

    transcript_text = result["text"]
    transcript_lang = result["language"]
    progress_bar.progress(30, text="✅ Transcript fetched")

    if not transcript_text or not transcript_text.strip():
        st.error("⚠️ The transcript is empty. Cannot generate notes.")
        st.stop()

    st.success(
        f"✅ Transcript ready · Language: **{transcript_lang.upper()}** · "
        f"{len(transcript_text.split()):,} words"
    )

    # Store transcript
    st.session_state.transcript_text = transcript_text
    st.session_state.transcript_lang = transcript_lang

    # Reset generated content
    for k in ["notes_text", "quiz_data", "flashcards_data", "interview_data",
              "practice_data", "study_plan", "mind_map", "revision_notes", "_session_db_id"]:
        st.session_state[k] = None

    # 3 — Load settings
    lang   = get_setting("output_language", "English")
    length = get_setting("summary_length", "Detailed")

    # 4 — Generate notes
    progress_bar.progress(40, text="🤖 Generating AI notes…")
    prompt = get_notes_prompt(
        transcript=transcript_text,
        language=lang,
        transcript_language=transcript_lang,
        length=length,
    )

    with st.spinner("🤖 Generating AI-powered study notes…"):
        ai_result = generate_text(prompt)

    if ai_result["error"]:
        st.error(f"🚫 {ai_result['error']}")
        st.stop()

    st.session_state.notes_text = ai_result["text"]
    progress_bar.progress(80, text="💾 Saving session…")

    # 5 — Extract video title from notes (first line or video_id)
    notes_lines = (ai_result["text"] or "").split("\n")
    video_title = ""
    for line in notes_lines:
        stripped = line.strip().lstrip("#").strip()
        if stripped and len(stripped) > 5:
            video_title = stripped[:80]
            break
    if not video_title:
        video_title = f"Video: {video_id}"
    st.session_state.video_title = video_title

    # 6 — Auto-save to DB
    auto_save = get_setting("auto_save", "true") == "true"
    if auto_save:
        try:
            db_result = save_session(
                youtube_url=youtube_url,
                video_id=video_id,
                video_title=video_title,
                transcript_language=transcript_lang,
                notes=ai_result["text"] or "",
                quiz=[],
                flashcards=[],
                interview_questions={},
                practice_questions={},
            )
            st.session_state._session_db_id = db_result.get("id")
        except Exception as e:
            pass  # DB errors are non-fatal

    progress_bar.progress(100, text="✅ All done!")
    st.balloons()


# ---------------------------------------------------------------------------
# Content tabs (shown when notes exist)
# ---------------------------------------------------------------------------
if st.session_state.transcript_text:
    video_id = st.session_state.video_id

    # Video thumbnail
    col_thumb, col_info = st.columns([2, 3])
    with col_thumb:
        st.image(
            f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            use_container_width=True,
        )
    with col_info:
        st.markdown(f"""
        <div style="padding:0.5rem 0">
            <div style="font-size:1.2rem; font-weight:700; color:#e8e8f0; margin-bottom:0.5rem">
                🎬 {st.session_state.video_title or "Generated Notes"}
            </div>
            <div style="color:#888; font-size:0.88rem; margin-bottom:0.8rem">
                📌 {st.session_state.youtube_url}<br>
                🌐 Language: {(st.session_state.transcript_lang or 'en').upper()}
                &nbsp;|&nbsp;
                📝 {len((st.session_state.transcript_text or '').split()):,} words transcribed
            </div>
        </div>
        """, unsafe_allow_html=True)

        open_url = st.session_state.youtube_url
        if open_url:
            st.link_button("▶️ Watch on YouTube", url=open_url, use_container_width=False)

    with st.expander("📜 View Raw Transcript"):
        t_text = st.session_state.transcript_text
        st.text(t_text[:5000] + ("…" if len(t_text) > 5000 else ""))

    st.divider()

    # ── Main Tabs ─────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "📝 Notes",
        "❓ Quiz",
        "🗂️ Flashcards",
        "👔 Interview",
        "🏋️ Practice",
        "🗺️ Study Planner",
        "🧠 Mind Map",
        "⚡ Revision",
    ])

    # ── TAB: Notes ────────────────────────────────────────────────────────────
    with tabs[0]:
        if st.session_state.notes_text:
            col_head, col_regen = st.columns([4, 1])
            with col_head:
                st.subheader("📘 AI-Generated Study Notes")
            with col_regen:
                if st.button("🔄 Regenerate", key="regen_notes", use_container_width=True):
                    lang   = get_setting("output_language", "English")
                    length = get_setting("summary_length", "Detailed")
                    with st.spinner("🤖 Regenerating notes…"):
                        r = generate_text(get_notes_prompt(
                            st.session_state.transcript_text, lang,
                            st.session_state.transcript_lang, length,
                        ))
                    if not r["error"]:
                        st.session_state.notes_text = r["text"]
                        if st.session_state._session_db_id:
                            update_session_content(st.session_state._session_db_id, "notes", r["text"])
                        st.rerun()
                    else:
                        st.error(r["error"])

            st.markdown(st.session_state.notes_text)

            # Copy to clipboard button
            st.divider()
            col_copy, col_exp = st.columns([1, 3])
            with col_copy:
                if st.button("📋 Copy Notes", key="copy_notes", use_container_width=True):
                    try:
                        pyperclip.copy(st.session_state.notes_text)
                        st.success("✅ Copied!")
                    except Exception:
                        st.info("💡 Use the download buttons below to get the text.")

            # Export
            st.markdown("### 📥 Export Notes")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.download_button(
                    "📄 Download TXT", data=export_txt(st.session_state.notes_text),
                    file_name="vidnote_notes.txt", mime="text/plain",
                    use_container_width=True,
                )
            with c2:
                try:
                    st.download_button(
                        "📕 Download PDF",
                        data=export_pdf("VidNote AI - Study Notes", st.session_state.notes_text, "notes"),
                        file_name="vidnote_notes.pdf", mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"PDF error: {e}")
            with c3:
                try:
                    st.download_button(
                        "📘 Download DOCX",
                        data=export_docx("VidNote AI - Study Notes", st.session_state.notes_text, "notes"),
                        file_name="vidnote_notes.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"DOCX error: {e}")
        else:
            st.info("Notes will appear here after generation.")

    # ── TAB: Quiz ─────────────────────────────────────────────────────────────
    with tabs[1]:
        render_quiz(st.session_state.transcript_text)

    # ── TAB: Flashcards ───────────────────────────────────────────────────────
    with tabs[2]:
        render_flashcards(st.session_state.transcript_text)

    # ── TAB: Interview ────────────────────────────────────────────────────────
    with tabs[3]:
        render_interview(st.session_state.transcript_text)

    # ── TAB: Practice ─────────────────────────────────────────────────────────
    with tabs[4]:
        render_practice(st.session_state.transcript_text)

    # ── TAB: Study Planner ────────────────────────────────────────────────────
    with tabs[5]:
        st.subheader("🗺️ AI Study Planner")
        st.markdown("Get a personalised learning roadmap, next topics, and study schedule.")

        col_gen, col_regen = st.columns([3, 1])
        with col_gen:
            if st.session_state.study_plan is None:
                if st.button("🗺️ Generate Study Plan", key="gen_plan", type="primary", use_container_width=True):
                    with st.spinner("🧠 Building your personalised study plan…"):
                        r = generate_text(get_study_planner_prompt(
                            st.session_state.notes_text or st.session_state.transcript_text,
                            st.session_state.video_title,
                        ))
                    if r["error"]:
                        st.error(r["error"])
                    else:
                        st.session_state.study_plan = r["text"]
                        st.rerun()

        if st.session_state.study_plan:
            with col_regen:
                if st.button("🔄 Regenerate", key="regen_plan", use_container_width=True):
                    with st.spinner("🧠 Regenerating…"):
                        r = generate_text(get_study_planner_prompt(
                            st.session_state.notes_text or st.session_state.transcript_text,
                            st.session_state.video_title,
                        ))
                    if not r["error"]:
                        st.session_state.study_plan = r["text"]
                        st.rerun()

            st.divider()
            st.markdown(st.session_state.study_plan)

            st.divider()
            col_cp, col_dl = st.columns(2)
            with col_dl:
                st.download_button(
                    "📄 Download Plan (TXT)",
                    data=export_txt(st.session_state.study_plan),
                    file_name="vidnote_study_plan.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

    # ── TAB: Mind Map ─────────────────────────────────────────────────────────
    with tabs[6]:
        st.subheader("🧠 AI Mind Map Generator")
        st.markdown("Visualise key concepts as a hierarchical mind map.")

        if st.session_state.mind_map is None:
            if st.button("🧠 Generate Mind Map", key="gen_mindmap", type="primary", use_container_width=True):
                with st.spinner("🧠 Generating mind map structure…"):
                    r = generate_text(get_mind_map_prompt(
                        st.session_state.notes_text or st.session_state.transcript_text
                    ))
                if r["error"]:
                    st.error(r["error"])
                else:
                    st.session_state.mind_map = r["text"]
                    st.rerun()

        if st.session_state.mind_map:
            col_regen_mm, col_dl_mm = st.columns([1, 1])
            with col_regen_mm:
                if st.button("🔄 Regenerate Mind Map", key="regen_mm", use_container_width=True):
                    with st.spinner("Regenerating…"):
                        r = generate_text(get_mind_map_prompt(
                            st.session_state.notes_text or st.session_state.transcript_text
                        ))
                    if not r["error"]:
                        st.session_state.mind_map = r["text"]
                        st.rerun()
            with col_dl_mm:
                st.download_button(
                    "📄 Download Mind Map (TXT)",
                    data=export_txt(st.session_state.mind_map),
                    file_name="vidnote_mindmap.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            st.divider()
            st.markdown(st.session_state.mind_map)

    # ── TAB: Revision Notes ───────────────────────────────────────────────────
    with tabs[7]:
        st.subheader("⚡ AI Revision Notes")
        st.markdown("Ultra-concise, exam-ready revision sheet generated from your notes.")

        if st.session_state.revision_notes is None:
            if st.button("⚡ Generate Revision Notes", key="gen_revision", type="primary", use_container_width=True):
                with st.spinner("⚡ Generating exam-ready revision sheet…"):
                    from utils.prompts import get_revision_notes_prompt
                    r = generate_text(get_revision_notes_prompt(
                        st.session_state.notes_text or st.session_state.transcript_text
                    ))
                if r["error"]:
                    st.error(r["error"])
                else:
                    st.session_state.revision_notes = r["text"]
                    st.rerun()

        if st.session_state.revision_notes:
            col_regen_rev, col_dl_rev = st.columns([1, 1])
            with col_regen_rev:
                if st.button("🔄 Regenerate", key="regen_rev", use_container_width=True):
                    from utils.prompts import get_revision_notes_prompt
                    with st.spinner("Regenerating…"):
                        r = generate_text(get_revision_notes_prompt(
                            st.session_state.notes_text or st.session_state.transcript_text
                        ))
                    if not r["error"]:
                        st.session_state.revision_notes = r["text"]
                        st.rerun()
            with col_dl_rev:
                st.download_button(
                    "📄 Download Revision Sheet",
                    data=export_txt(st.session_state.revision_notes),
                    file_name="vidnote_revision.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            st.divider()
            st.markdown(st.session_state.revision_notes)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("""
<div class="footer">
    🎬 <strong>VidNote AI v2.0</strong> &nbsp;·&nbsp;
    Built with Streamlit & Google Gemini &nbsp;·&nbsp;
    <a href="https://ai.google.dev" target="_blank">Gemini API</a> &nbsp;·&nbsp;
    MIT License
</div>
""", unsafe_allow_html=True)