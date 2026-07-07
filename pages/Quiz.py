import streamlit as st
import json
from utils.gemini import generate_json
from utils.prompts import get_quiz_prompt

def render_quiz(transcript_text: str):
    st.subheader("📝 AI Quiz Generator")
    
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = None

    if st.session_state.quiz_data is None:
        if st.button("Generate Quiz ✨", key="btn_gen_quiz"):
            with st.spinner("🤖 Generating 10 multiple-choice questions..."):
                prompt = get_quiz_prompt(transcript_text)
                result = generate_json(prompt)
                
                if result["error"]:
                    st.error(f"🚫 {result['error']}")
                else:
                    try:
                        quiz_json = json.loads(result["data"])
                        st.session_state.quiz_data = quiz_json
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to parse AI output: {e}")
                        with st.expander("Raw Output"):
                            st.text(result["data"])
    else:
        # Render Quiz
        if st.button("🔄 Regenerate Quiz", key="btn_regen_quiz"):
            st.session_state.quiz_data = None
            st.rerun()

        for i, q in enumerate(st.session_state.quiz_data):
            st.markdown(f"**Q{i+1}: {q.get('question', '')}**")
            options = q.get('options', [])
            for opt in options:
                st.markdown(f"- {opt}")
            
            with st.expander("Show Answer"):
                st.success(f"**Correct Answer:** {q.get('answer', '')}")
                st.info(f"**Explanation:** {q.get('explanation', '')}")
            st.divider()

        from utils.export import export_pdf, export_docx
        st.markdown("### 📥 Export Quiz")
        col1, col2 = st.columns(2)
        with col1:
            try:
                pdf_bytes = export_pdf("VidNote AI - Quiz", st.session_state.quiz_data, "quiz")
                st.download_button(
                    label="📕 Download PDF",
                    data=pdf_bytes,
                    file_name="vidnote_quiz.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Failed to generate PDF: {e}")
        with col2:
            try:
                docx_bytes = export_docx("VidNote AI - Quiz", st.session_state.quiz_data, "quiz")
                st.download_button(
                    label="📘 Download DOCX",
                    data=docx_bytes,
                    file_name="vidnote_quiz.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Failed to generate DOCX: {e}")
