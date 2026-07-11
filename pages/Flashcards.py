"""
pages/Flashcards.py
--------------------
Flashcards tab renderer — 15 flip-style flashcards with
regenerate, DB persistence, and export to PDF/DOCX.
"""

import streamlit as st
import json
from utils.gemini import generate_json
from utils.prompts import get_flashcards_prompt
from utils.db import update_session_content
from utils.export import export_pdf, export_docx


def _inject_css():
    st.markdown("""
    <style>
    .flashcard-container {
        perspective: 1000px;
        margin-bottom: 1rem;
    }
    .flashcard {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        transition: border-color 0.3s;
        position: relative;
    }
    .flashcard:hover { border-color: rgba(102,126,234,0.45); }
    .fc-number {
        font-size: 0.72rem;
        color: #666;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.4rem;
    }
    .fc-question {
        font-size: 1rem;
        font-weight: 700;
        color: #e8e8f0;
        line-height: 1.5;
        margin-bottom: 0.8rem;
    }
    .fc-answer {
        font-size: 0.92rem;
        color: #a0aec0;
        line-height: 1.6;
        border-top: 1px solid rgba(255,255,255,0.07);
        padding-top: 0.8rem;
        margin-top: 0.4rem;
    }
    .fc-badge {
        display: inline-block;
        background: rgba(102,126,234,0.18);
        border: 1px solid rgba(102,126,234,0.3);
        color: #a78bfa;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-bottom: 0.7rem;
    }
    </style>
    """, unsafe_allow_html=True)


def render_flashcards(transcript_text: str):
    _inject_css()
    st.subheader("🗂️ AI Flashcards")
    st.markdown("15 spaced-repetition flashcards generated from the video transcript.")

    if "flashcards_data" not in st.session_state:
        st.session_state.flashcards_data = None

    if st.session_state.flashcards_data is None:
        col_gen, col_info = st.columns([2, 3])
        with col_gen:
            if st.button("✨ Generate Flashcards", key="btn_gen_flash", type="primary", use_container_width=True):
                with st.spinner("🤖 Generating 15 flashcards…"):
                    prompt = get_flashcards_prompt(transcript_text)
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
                        fc_json = json.loads(raw.strip())
                        st.session_state.flashcards_data = fc_json

                        # Persist to DB
                        db_id = st.session_state.get("_session_db_id")
                        if db_id:
                            update_session_content(db_id, "flashcards", fc_json)

                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to parse AI output: {e}")
                        with st.expander("🔍 Raw Output (debug)"):
                            st.code(result["data"])
        with col_info:
            st.info("💡 Flashcards use a question/answer format ideal for spaced repetition. Click **Generate Flashcards** to start.")
    else:
        # ── Controls ──────────────────────────────────────────────────────────
        col_regen, col_count, col_pdf, col_docx = st.columns([2, 2, 1, 1])
        with col_regen:
            if st.button("🔄 Regenerate Flashcards", key="btn_regen_flash", use_container_width=True):
                st.session_state.flashcards_data = None
                st.rerun()
        with col_count:
            st.success(f"✅ {len(st.session_state.flashcards_data)} flashcards generated")
        with col_pdf:
            try:
                pdf_bytes = export_pdf("VidNote AI - Flashcards", st.session_state.flashcards_data, "flashcards")
                st.download_button(
                    "📕 PDF", data=pdf_bytes,
                    file_name="vidnote_flashcards.pdf", mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PDF: {e}")
        with col_docx:
            try:
                docx_bytes = export_docx("VidNote AI - Flashcards", st.session_state.flashcards_data, "flashcards")
                st.download_button(
                    "📘 DOCX", data=docx_bytes,
                    file_name="vidnote_flashcards.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"DOCX: {e}")

        st.divider()

        # Toggle: show all answers
        show_all = st.toggle("👁️ Reveal all answers", key="fc_show_all", value=False)

        st.divider()

        # ── Flashcards grid ───────────────────────────────────────────────────
        cards = st.session_state.flashcards_data
        for i, card in enumerate(cards):
            question = card.get("question", "")
            answer   = card.get("answer", "")

            with st.container():
                st.markdown(f"""
                <div class="flashcard">
                    <div class="fc-badge">Card {i + 1} of {len(cards)}</div>
                    <div class="fc-question">🤔 {question}</div>
                </div>
                """, unsafe_allow_html=True)

                if show_all:
                    st.success(f"💡 **Answer:** {answer}")
                else:
                    with st.expander("Show Answer"):
                        st.success(f"💡 **Answer:** {answer}")
