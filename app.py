"""
app.py — VidNote AI
=====================
Main Streamlit application entry point.
Phase 1: Core transcript extraction + AI notes generation with error handling.
"""

import streamlit as st
from utils.transcript import extract_video_id, get_transcript
from utils.gemini import generate_text
from utils.prompts import get_notes_prompt

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="VidNote AI — YouTube Learning Assistant",
    page_icon="🎬",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Minimal CSS (Phase 6 will add full Glassmorphism theme)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Centre the hero section */
    .hero { text-align: center; padding: 2rem 0 1rem; }
    .hero h1 { font-size: 2.4rem; }
    .hero p  { color: #888; font-size: 1.1rem; }

    /* Nicer button */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; border-radius: 10px;
        padding: 0.6rem 2rem; font-weight: 600;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(102,126,234,0.45);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Hero section
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>🎬 VidNote AI</h1>
    <p>Paste a YouTube URL and get comprehensive AI-powered study notes instantly.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# URL input
# ---------------------------------------------------------------------------
youtube_url = st.text_input(
    "🔗 YouTube Video URL",
    placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
)

generate_clicked = st.button("✨ Generate Notes", use_container_width=True)

# ---------------------------------------------------------------------------
# Processing pipeline
# ---------------------------------------------------------------------------
if generate_clicked:
    # 1 — Validate URL -------------------------------------------------------
    if not youtube_url or not youtube_url.strip():
        st.error("⚠️ Please enter a YouTube URL.")
        st.stop()

    video_id = extract_video_id(youtube_url)

    if not video_id:
        st.error(
            "❌ Invalid YouTube URL. Please use a link like "
            "`https://www.youtube.com/watch?v=VIDEO_ID` or `https://youtu.be/VIDEO_ID`."
        )
        st.stop()

    # Show video thumbnail
    st.image(
        f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        use_container_width=True,
    )

    # 2 — Fetch transcript ---------------------------------------------------
    with st.spinner("📥 Fetching transcript…"):
        result = get_transcript(video_id)

    if result["error"]:
        st.error(f"🚫 {result['error']}")
        st.stop()

    transcript_text = result["text"]
    transcript_lang = result["language"]

    if not transcript_text or not transcript_text.strip():
        st.error("⚠️ The transcript is empty. Cannot generate notes.")
        st.stop()

    st.success(
        f"✅ Transcript fetched successfully! "
        f"(Language: **{transcript_lang}** · "
        f"{len(transcript_text.split())} words)"
    )

    # Show raw transcript in an expander
    with st.expander("📜 View Raw Transcript"):
        st.text(transcript_text[:5000] + ("…" if len(transcript_text) > 5000 else ""))

    # 3 — Generate notes via Gemini ------------------------------------------
    prompt = get_notes_prompt(
        transcript=transcript_text,
        language="English",
        transcript_language=transcript_lang,
        length="Detailed",
    )

    with st.spinner("🤖 Generating AI notes — this may take a moment…"):
        ai_result = generate_text(prompt)

    if ai_result["error"]:
        st.error(f"🚫 {ai_result['error']}")
        st.stop()

    notes = ai_result["text"]

    # 4 — Display notes ------------------------------------------------------
    st.divider()
    st.subheader("📘 AI-Generated Study Notes")
    st.markdown(notes)

    # Quick download as .txt (Phase 3 will add PDF & DOCX)
    st.download_button(
        label="📥 Download Notes (.txt)",
        data=notes,
        file_name="vidnote_ai_notes.txt",
        mime="text/plain",
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#888; font-size:0.85rem;'>"
    "VidNote AI · Built with Streamlit & Gemini"
    "</p>",
    unsafe_allow_html=True,
)