import streamlit as st
import json
from utils.gemini import generate_json
from utils.prompts import get_interview_prompt

def render_interview(transcript_text: str):
    st.subheader("👔 AI Interview Questions")
    
    if "interview_data" not in st.session_state:
        st.session_state.interview_data = None

    if st.session_state.interview_data is None:
        if st.button("Generate Interview Questions ✨", key="btn_gen_interview"):
            with st.spinner("🤖 Generating Beginner, Intermediate, and Advanced questions..."):
                prompt = get_interview_prompt(transcript_text)
                result = generate_json(prompt)
                
                if result["error"]:
                    st.error(f"🚫 {result['error']}")
                else:
                    try:
                        int_json = json.loads(result["data"])
                        st.session_state.interview_data = int_json
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to parse AI output: {e}")
                        with st.expander("Raw Output"):
                            st.text(result["data"])
    else:
        if st.button("🔄 Regenerate Interview Questions", key="btn_regen_interview"):
            st.session_state.interview_data = None
            st.rerun()

        for difficulty in ["Beginner", "Intermediate", "Advanced"]:
            questions = st.session_state.interview_data.get(difficulty, [])
            if questions:
                st.markdown(f"### {difficulty} Level")
                for i, q in enumerate(questions):
                    st.markdown(f"**Q{i+1}: {q.get('question', '')}**")
                    with st.expander("Suggested Answer"):
                        st.markdown(q.get('answer', ''))
                st.divider()

        from utils.export import export_pdf, export_docx
        st.markdown("### 📥 Export Interview Questions")
        col1, col2 = st.columns(2)
        with col1:
            try:
                pdf_bytes = export_pdf("VidNote AI - Interview Questions", st.session_state.interview_data, "interview")
                st.download_button(
                    label="📕 Download PDF",
                    data=pdf_bytes,
                    file_name="vidnote_interview.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Failed to generate PDF: {e}")
        with col2:
            try:
                docx_bytes = export_docx("VidNote AI - Interview Questions", st.session_state.interview_data, "interview")
                st.download_button(
                    label="📘 Download DOCX",
                    data=docx_bytes,
                    file_name="vidnote_interview.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Failed to generate DOCX: {e}")
