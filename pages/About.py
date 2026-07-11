"""
pages/About.py
---------------
About page — features, FAQ, tech stack, and contact section.
"""

import streamlit as st

def _inject_css():
    st.markdown("""
    <style>
    .about-hero {
        text-align: center;
        padding: 2rem 0 1rem;
    }
    .about-hero h1 {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .about-hero p {
        color: #aaa;
        font-size: 1.15rem;
        max-width: 600px;
        margin: 0 auto;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .feature-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 16px;
        padding: 1.4rem;
        transition: border-color 0.3s, transform 0.2s;
    }
    .feature-card:hover {
        border-color: rgba(102,126,234,0.5);
        transform: translateY(-3px);
    }
    .feature-card .icon { font-size: 2.2rem; margin-bottom: 0.5rem; }
    .feature-card h4 { color: #c4b5fd; margin-bottom: 0.3rem; font-size: 1rem; }
    .feature-card p { color: #999; font-size: 0.87rem; line-height: 1.5; }
    .tech-badge {
        display: inline-block;
        background: rgba(102,126,234,0.18);
        border: 1px solid rgba(102,126,234,0.35);
        color: #a78bfa;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.82rem;
        margin: 4px;
        font-weight: 600;
    }
    .faq-item {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.7rem;
    }
    .faq-item .faq-q { color: #c4b5fd; font-weight: 700; margin-bottom: 0.4rem; }
    .faq-item .faq-a { color: #aaa; font-size: 0.9rem; line-height: 1.6; }
    .contact-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.12), rgba(118,75,162,0.12));
        border: 1px solid rgba(102,126,234,0.25);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)


FEATURES = [
    ("🎬", "YouTube Transcript Extraction", "Supports English, Hindi, Kannada, and auto-generated transcripts from any YouTube video."),
    ("🤖", "AI-Powered Study Notes", "Gemini generates structured notes with summaries, key points, definitions, and examples."),
    ("❓", "Interactive Quiz", "10 multiple-choice questions with answers and explanations — test your understanding."),
    ("🗂️", "Smart Flashcards", "15 flip-style flashcards for efficient spaced repetition learning."),
    ("👔", "Interview Questions", "Beginner to Advanced questions to prepare for technical and non-technical interviews."),
    ("🏋️", "Practice Problems", "Easy/Medium/Hard practice questions with step-by-step solutions."),
    ("💬", "AI Chat Tutor", "Ask anything about the video — your AI tutor answers contextually from the notes."),
    ("📊", "Learning History", "Auto-saves every session with search, filter, favorites, and statistics."),
    ("📥", "Multi-format Export", "Download notes, quiz, and flashcards as PDF, DOCX, or TXT instantly."),
    ("⚙️", "Customisable Settings", "Choose output language, AI model, summary length, and export preferences."),
    ("🗺️", "AI Study Planner", "Get a personalised learning roadmap with next topics and recommended videos."),
    ("🧠", "Mind Map Generator", "Visualise key concepts as a structured mind map from your notes."),
]

FAQS = [
    ("What is VidNote AI?",
     "VidNote AI is an AI-powered SaaS tool that extracts YouTube video transcripts and generates comprehensive study notes, quizzes, flashcards, interview questions, and more using Google's Gemini AI."),
    ("Which YouTube videos are supported?",
     "Any public YouTube video that has captions or auto-generated subtitles enabled. Videos with subtitles in English, Hindi, and Kannada are prioritised, with automatic fallback to other available languages."),
    ("Is my data stored anywhere?",
     "All data is stored locally in a SQLite database on your machine (vidnote_ai.db). No data is sent to external servers other than the Gemini API for AI generation."),
    ("What AI model is used?",
     "VidNote AI uses Google's Gemini 2.5 Flash by default, with automatic fallback to Gemini 2.0 Flash. You can change the model in Settings."),
    ("Can I export my notes?",
     "Yes! All content (notes, quiz, flashcards, interview questions, practice questions) can be exported as PDF, DOCX, or TXT files."),
    ("How do I restore a previous session?",
     "Go to the History page, find your session, and click 'Restore'. This reloads all previously generated content into the app."),
    ("Is the Gemini API free?",
     "Google offers a free tier for the Gemini API. For heavy usage, you may need a paid plan. Check ai.google.dev for current pricing."),
    ("Can I use this offline?",
     "The app requires internet access to fetch YouTube transcripts and call the Gemini API. The database and export features work fully offline."),
]

TECH_STACK = [
    "Python 3.11+", "Streamlit", "Google Gemini AI", "SQLite",
    "youtube-transcript-api", "fpdf2", "python-docx",
    "pandas", "Glassmorphism CSS", "Git",
]


def render_about():
    _inject_css()

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="about-hero">
        <h1>🎬 VidNote AI</h1>
        <p>Turn any YouTube video into a complete learning experience with the power of AI.</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Features ──────────────────────────────────────────────────────────────
    st.markdown("## ✨ Features")
    html = '<div class="feature-grid">'
    for icon, title, desc in FEATURES:
        html += f"""
        <div class="feature-card">
            <div class="icon">{icon}</div>
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    st.divider()

    # ── Tech Stack ────────────────────────────────────────────────────────────
    st.markdown("## 🛠️ Tech Stack")
    badges = "".join(f'<span class="tech-badge">{t}</span>' for t in TECH_STACK)
    st.markdown(f'<div style="margin:0.8rem 0">{badges}</div>', unsafe_allow_html=True)

    st.divider()

    # ── How it works ─────────────────────────────────────────────────────────
    st.markdown("## 🔄 How It Works")
    col1, col2, col3, col4 = st.columns(4)
    steps = [
        ("1️⃣", "Paste URL", "Enter any YouTube video link"),
        ("2️⃣", "Extract", "AI fetches the transcript automatically"),
        ("3️⃣", "Generate", "Gemini creates notes, quiz & more"),
        ("4️⃣", "Export", "Download as PDF, DOCX, or TXT"),
    ]
    for col, (num, title, desc) in zip([col1, col2, col3, col4], steps):
        col.markdown(f"""
        <div style="text-align:center; padding:1rem; background:rgba(255,255,255,0.04);
                    border-radius:14px; border:1px solid rgba(255,255,255,0.08);">
            <div style="font-size:2rem">{num}</div>
            <div style="font-weight:700; color:#c4b5fd; margin:0.4rem 0">{title}</div>
            <div style="color:#888; font-size:0.82rem">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── FAQ ───────────────────────────────────────────────────────────────────
    st.markdown("## ❓ Frequently Asked Questions")
    for q, a in FAQS:
        with st.expander(q):
            st.markdown(a)

    st.divider()

    # ── Contact ───────────────────────────────────────────────────────────────
    st.markdown("## 📬 Contact")
    st.markdown("""
    <div class="contact-card">
        <div style="font-size:2.5rem; margin-bottom:0.5rem">👋</div>
        <h3 style="color:#c4b5fd">Built by Vinayak Kudlamath</h3>
        <p style="color:#999; max-width:500px; margin:0.5rem auto">
            This project was built as a full-stack AI SaaS application demonstrating
            real-world use of LLMs, Streamlit, SQLite, and modern Python architecture.
        </p>
        <div style="margin-top:1rem">
            <span class="tech-badge">🐙 GitHub</span>
            <span class="tech-badge">💼 LinkedIn</span>
            <span class="tech-badge">📧 Email</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <p style="text-align:center; color:#555; font-size:0.82rem">
        VidNote AI v2.0 · Built with ❤️ using Streamlit & Google Gemini · MIT License
    </p>
    """, unsafe_allow_html=True)


# ── Standalone page entry ─────────────────────────────────────────────────────
render_about()
