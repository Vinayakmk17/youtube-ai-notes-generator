"""
pages/Quiz.py
--------------
Quiz tab renderer — 10 MCQ questions with answer reveal,
regenerate, copy, and export to PDF/DOCX.
"""

import streamlit as st
import json
from utils.gemini import generate_json
from utils.prompts import get_quiz_prompt
from utils.db import update_session_content


def render_quiz(transcript_text: str):
    st.subheader("❓ AI Quiz Generator")
    st.markdown("Test your understanding with 10 auto-generated multiple-choice questions.")

    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None

    if st.session_state.quiz_data is None:
        col_gen, col_info = st.columns([2, 3])
        with col_gen:
            if st.button("✨ Generate Quiz", key="btn_gen_quiz", type="primary", use_container_width=True):
                with st.spinner("🤖 Generating 10 multiple-choice questions…"):
                    prompt = get_quiz_prompt(transcript_text)
                    result = generate_json(prompt)

                if result["error"]:
                    st.error(f"🚫 {result['error']}")
                else:
                    try:
                        raw = result["data"] or ""
                        # Strip markdown code fences if present
                        if "```" in raw:
                            raw = raw.split("```")[1]
                            if raw.startswith("json"):
                                raw = raw[4:]
                        quiz_json = json.loads(raw.strip())
                        st.session_state.quiz_data = quiz_json

                        # Persist to DB if session exists
                        db_id = st.session_state.get("_session_db_id")
                        if db_id:
                            update_session_content(db_id, "quiz", quiz_json)

                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to parse AI output: {e}")
                        with st.expander("🔍 Raw Output (debug)"):
                            st.code(result["data"])
        with col_info:
            st.info("💡 Quiz generates 10 MCQ questions with explanations. Click **Generate Quiz** to start.")
    else:
        # Controls
        col_regen, col_count, col_export_pdf, col_export_docx = st.columns([2, 2, 1, 1])
        with col_regen:
            if st.button("🔄 Regenerate Quiz", key="btn_regen_quiz", use_container_width=True):
                st.session_state.quiz_data = None
                st.rerun()
        with col_count:
            st.success(f"✅ {len(st.session_state.quiz_data)} questions generated")

        from utils.export import export_pdf, export_docx
        with col_export_pdf:
            try:
                pdf_bytes = export_pdf("VidNote AI - Quiz", st.session_state.quiz_data, "quiz")
                st.download_button(
                    "📕 PDF", data=pdf_bytes,
                    file_name="vidnote_quiz.pdf", mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PDF: {e}")
        with col_export_docx:
            try:
                docx_bytes = export_docx("VidNote AI - Quiz", st.session_state.quiz_data, "quiz")
                st.download_button(
                    "📘 DOCX", data=docx_bytes,
                    file_name="vidnote_quiz.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"DOCX: {e}")

        st.divider()

        # Render questions
        score_tracker = {}
        for i, q in enumerate(st.session_state.quiz_data):
            question = q.get("question", "")
            options  = q.get("options", [])
            answer   = q.get("answer", "")
            explanation = q.get("explanation", "")

            with st.container():
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                            border-radius:14px;padding:1.2rem 1.4rem;margin-bottom:0.5rem">
                    <div style="font-weight:700;color:#e8e8f0;margin-bottom:0.8rem">
                        Q{i+1}: {question}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                user_answer = st.radio(
                    f"Q{i+1} options",
                    options,
                    key=f"quiz_q_{i}",
                    label_visibility="collapsed",
                )

                col_check, col_reveal = st.columns([1, 2])
                with col_check:
                    if st.button("✅ Check Answer", key=f"check_{i}", use_container_width=True):
                        if user_answer == answer:
                            st.success("🎉 Correct!")
                        else:
                            st.error(f"❌ Incorrect. Correct: **{answer}**")
                with col_reveal:
                    with st.expander("💡 Show Explanation"):
                        st.success(f"**Correct Answer:** {answer}")
                        if explanation:
                            st.info(f"**Explanation:** {explanation}")

                st.divider()
