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
from pages.Quiz import render_quiz
from pages.Flashcards import render_flashcards
from pages.Interview import render_interview
from pages.Practice import render_practice

# Initialize session state for persistent data
if "transcript_text" not in st.session_state:
    st.session_state.transcript_text = None
if "transcript_lang" not in st.session_state:
    st.session_state.transcript_lang = None
if "video_id" not in st.session_state:
    st.session_state.video_id = None
if "notes_text" not in st.session_state:
    st.session_state.notes_text = None

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
        
    st.session_state.video_id = video_id

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

    # Store in session state
    st.session_state.transcript_text = transcript_text
    st.session_state.transcript_lang = transcript_lang
    
    # Reset AI content
    st.session_state.notes_text = None
    st.session_state.quiz_data = None
    st.session_state.flashcards_data = None
    st.session_state.interview_data = None
    st.session_state.practice_data = None
    
    # 3 — Generate notes via Gemini automatically ----------------------------
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

    st.session_state.notes_text = ai_result["text"]

# ---------------------------------------------------------------------------
# UI Tabs rendering
# ---------------------------------------------------------------------------
if st.session_state.transcript_text:
    # Show video thumbnail
    st.image(
        f"https://img.youtube.com/vi/{st.session_state.video_id}/maxresdefault.jpg",
        use_container_width=True,
    )

    with st.expander("📜 View Raw Transcript"):
        t_text = st.session_state.transcript_text
        st.text(t_text[:5000] + ("…" if len(t_text) > 5000 else ""))

    st.divider()
    
    tab_notes, tab_quiz, tab_flashcards, tab_interview, tab_practice = st.tabs([
        "📝 Notes", "❓ Quiz", "🗂️ Flashcards", "👔 Interview Questions", "🏋️ Practice Questions"
    ])
    
    with tab_notes:
        if st.session_state.notes_text:
            st.subheader("📘 AI-Generated Study Notes")
            st.markdown(st.session_state.notes_text)
            
            from utils.export import export_txt, export_pdf, export_docx
            st.divider()
            st.markdown("### 📥 Export Notes")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    label="📄 Download TXT",
                    data=export_txt(st.session_state.notes_text),
                    file_name="vidnote_notes.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                try:
                    pdf_bytes = export_pdf("VidNote AI - Study Notes", st.session_state.notes_text, "notes")
                    st.download_button(
                        label="📕 Download PDF",
                        data=pdf_bytes,
                        file_name="vidnote_notes.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Failed to generate PDF: {e}")
            with col3:
                try:
                    docx_bytes = export_docx("VidNote AI - Study Notes", st.session_state.notes_text, "notes")
                    st.download_button(
                        label="📘 Download DOCX",
                        data=docx_bytes,
                        file_name="vidnote_notes.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Failed to generate DOCX: {e}")
        else:
            st.info("Notes not available.")
            
    with tab_quiz:
        render_quiz(st.session_state.transcript_text)
        
    with tab_flashcards:
        render_flashcards(st.session_state.transcript_text)
        
    with tab_interview:
        render_interview(st.session_state.transcript_text)
        
    with tab_practice:
        render_practice(st.session_state.transcript_text)

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