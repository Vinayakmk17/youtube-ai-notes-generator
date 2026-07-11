"""
pages/Interview.py
-------------------
Interview Questions tab renderer — Beginner / Intermediate / Advanced questions
with regenerate, DB persistence, styled cards, and export to PDF/DOCX.
"""

import streamlit as st
import json
from utils.gemini import generate_json
from utils.prompts import get_interview_prompt
from utils.db import update_session_content
from utils.export import export_pdf, export_docx


_LEVEL_META = {
    "Beginner":     ("🟢", "rgba(52,211,153,0.1)",  "rgba(52,211,153,0.25)"),
    "Intermediate": ("🟡", "rgba(251,191,36,0.1)",  "rgba(251,191,36,0.25)"),
    "Advanced":     ("🔴", "rgba(248,113,113,0.1)", "rgba(248,113,113,0.25)"),
}


def _inject_css():
    st.markdown("""
    <style>
    .iq-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.7rem;
        transition: border-color 0.25s;
    }
    .iq-card:hover { border-color: rgba(102,126,234,0.4); }
    .iq-level-badge {
        display: inline-block;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.74rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }
    .iq-question {
        font-size: 0.98rem;
        font-weight: 700;
        color: #e8e8f0;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)


def render_interview(transcript_text: str):
    _inject_css()
    st.subheader("👔 AI Interview Questions")
    st.markdown("Prepare for technical and conceptual interviews with AI-generated questions at three difficulty tiers.")

    if "interview_data" not in st.session_state:
        st.session_state.interview_data = None

    if st.session_state.interview_data is None:
        col_gen, col_info = st.columns([2, 3])
        with col_gen:
            if st.button("✨ Generate Interview Questions", key="btn_gen_interview", type="primary", use_container_width=True):
                with st.spinner("🤖 Generating Beginner, Intermediate & Advanced questions…"):
                    prompt = get_interview_prompt(transcript_text)
                    result = generate_json(prompt)

                if result["error"]:
                    st.error(f"🚫 {result['error']}")
                else:
                    try:
                        raw = result["data"] or ""
                        if "```" in raw:
                            raw = raw.split("```")[1]
                            if raw.startswith("json"):
                                raw = raw[4:]
                        int_json = json.loads(raw.strip())
                        st.session_state.interview_data = int_json

                        # Persist to DB
                        db_id = st.session_state.get("_session_db_id")
                        if db_id:
                            update_session_content(db_id, "interview_questions", int_json)

                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to parse AI output: {e}")
                        with st.expander("🔍 Raw Output (debug)"):
                            st.code(result["data"])
        with col_info:
            st.info("💡 15 interview questions (5 Beginner · 5 Intermediate · 5 Advanced) with suggested answers. Click **Generate** to start.")
    else:
        data = st.session_state.interview_data

        # ── Controls ──────────────────────────────────────────────────────────
        total_q = sum(len(data.get(l, [])) for l in ["Beginner", "Intermediate", "Advanced"])
        col_regen, col_count, col_pdf, col_docx = st.columns([2, 2, 1, 1])
        with col_regen:
            if st.button("🔄 Regenerate Questions", key="btn_regen_interview", use_container_width=True):
                st.session_state.interview_data = None
                st.rerun()
        with col_count:
            st.success(f"✅ {total_q} questions generated")
        with col_pdf:
            try:
                pdf_bytes = export_pdf("VidNote AI - Interview Questions", data, "interview")
                st.download_button(
                    "📕 PDF", data=pdf_bytes,
                    file_name="vidnote_interview.pdf", mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PDF: {e}")
        with col_docx:
            try:
                docx_bytes = export_docx("VidNote AI - Interview Questions", data, "interview")
                st.download_button(
                    "📘 DOCX", data=docx_bytes,
                    file_name="vidnote_interview.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"DOCX: {e}")

        st.divider()

        # ── Questions by level ────────────────────────────────────────────────
        for difficulty in ["Beginner", "Intermediate", "Advanced"]:
            questions = data.get(difficulty, [])
            if not questions:
                continue

            emoji, bg_col, badge_col = _LEVEL_META[difficulty]
            st.markdown(f"### {emoji} {difficulty} Level &nbsp; <small style='color:#666;font-size:0.78rem;'>({len(questions)} questions)</small>", unsafe_allow_html=True)

            for i, q in enumerate(questions):
                question = q.get("question", "")
                answer   = q.get("answer", "")

                with st.container():
                    st.markdown(f"""
                    <div class="iq-card">
                        <div class="iq-level-badge" style="background:{bg_col};border:1px solid {badge_col};color:#e0e0f0;">
                            {emoji} {difficulty}
                        </div>
                        <div class="iq-question">Q{i+1}: {question}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("💬 Suggested Answer"):
                        st.markdown(answer)

            st.divider()
