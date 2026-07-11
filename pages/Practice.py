"""
pages/Practice.py
------------------
Practice Questions tab renderer — Easy / Medium / Hard problems
with step-by-step solutions, DB persistence, styled cards, and PDF/DOCX export.
"""

import streamlit as st
import json
from utils.gemini import generate_json
from utils.prompts import get_practice_prompt
from utils.db import update_session_content
from utils.export import export_pdf, export_docx


_LEVEL_META = {
    "Easy":   ("🟢", "rgba(52,211,153,0.1)",  "rgba(52,211,153,0.3)"),
    "Medium": ("🟡", "rgba(251,191,36,0.1)",  "rgba(251,191,36,0.3)"),
    "Hard":   ("🔴", "rgba(248,113,113,0.1)", "rgba(248,113,113,0.3)"),
}


def _inject_css():
    st.markdown("""
    <style>
    .pq-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.7rem;
        transition: border-color 0.25s;
    }
    .pq-card:hover { border-color: rgba(102,126,234,0.4); }
    .pq-level-badge {
        display: inline-block;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.74rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }
    .pq-question {
        font-size: 0.98rem;
        font-weight: 700;
        color: #e8e8f0;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)


def render_practice(transcript_text: str):
    _inject_css()
    st.subheader("🏋️ AI Practice Questions")
    st.markdown("Develop hands-on problem-solving skills with Easy, Medium, and Hard practice questions.")

    if "practice_data" not in st.session_state:
        st.session_state.practice_data = None

    if st.session_state.practice_data is None:
        col_gen, col_info = st.columns([2, 3])
        with col_gen:
            if st.button("✨ Generate Practice Questions", key="btn_gen_practice", type="primary", use_container_width=True):
                with st.spinner("🤖 Generating Easy, Medium & Hard practice questions…"):
                    prompt = get_practice_prompt(transcript_text)
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
                        prac_json = json.loads(raw.strip())
                        st.session_state.practice_data = prac_json

                        # Persist to DB
                        db_id = st.session_state.get("_session_db_id")
                        if db_id:
                            update_session_content(db_id, "practice_questions", prac_json)

                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to parse AI output: {e}")
                        with st.expander("🔍 Raw Output (debug)"):
                            st.code(result["data"])
        with col_info:
            st.info("💡 9 practice questions (3 Easy · 3 Medium · 3 Hard) with detailed step-by-step solutions. Click **Generate** to start.")
    else:
        data = st.session_state.practice_data

        # ── Controls ──────────────────────────────────────────────────────────
        total_q = sum(len(data.get(l, [])) for l in ["Easy", "Medium", "Hard"])
        col_regen, col_count, col_pdf, col_docx = st.columns([2, 2, 1, 1])
        with col_regen:
            if st.button("🔄 Regenerate Questions", key="btn_regen_practice", use_container_width=True):
                st.session_state.practice_data = None
                st.rerun()
        with col_count:
            st.success(f"✅ {total_q} questions generated")
        with col_pdf:
            try:
                pdf_bytes = export_pdf("VidNote AI - Practice Questions", data, "practice")
                st.download_button(
                    "📕 PDF", data=pdf_bytes,
                    file_name="vidnote_practice.pdf", mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PDF: {e}")
        with col_docx:
            try:
                docx_bytes = export_docx("VidNote AI - Practice Questions", data, "practice")
                st.download_button(
                    "📘 DOCX", data=docx_bytes,
                    file_name="vidnote_practice.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"DOCX: {e}")

        st.divider()

        # ── Questions by difficulty ───────────────────────────────────────────
        for difficulty in ["Easy", "Medium", "Hard"]:
            questions = data.get(difficulty, [])
            if not questions:
                continue

            emoji, bg_col, badge_col = _LEVEL_META[difficulty]
            st.markdown(f"### {emoji} {difficulty} Level &nbsp; <small style='color:#666;font-size:0.78rem;'>({len(questions)} questions)</small>", unsafe_allow_html=True)

            for i, q in enumerate(questions):
                question = q.get("question", "")
                solution = q.get("solution", "")

                with st.container():
                    st.markdown(f"""
                    <div class="pq-card">
                        <div class="pq-level-badge" style="background:{bg_col};border:1px solid {badge_col};color:#e0e0f0;">
                            {emoji} {difficulty}
                        </div>
                        <div class="pq-question">Q{i+1}: {question}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("🔍 View Step-by-Step Solution"):
                        st.markdown(solution)

            st.divider()
