import streamlit as st
import json
from utils.gemini import generate_json
from utils.prompts import get_practice_prompt

def render_practice(transcript_text: str):
    st.subheader("🏋️ AI Practice Questions")
    
    if "practice_data" not in st.session_state:
        st.session_state.practice_data = None

    if st.session_state.practice_data is None:
        if st.button("Generate Practice Questions ✨", key="btn_gen_practice"):
            with st.spinner("🤖 Generating Easy, Medium, and Hard practice questions..."):
                prompt = get_practice_prompt(transcript_text)
                result = generate_json(prompt)
                
                if result["error"]:
                    st.error(f"🚫 {result['error']}")
                else:
                    try:
                        prac_json = json.loads(result["data"])
                        st.session_state.practice_data = prac_json
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to parse AI output: {e}")
                        with st.expander("Raw Output"):
                            st.text(result["data"])
    else:
        if st.button("🔄 Regenerate Practice Questions", key="btn_regen_practice"):
            st.session_state.practice_data = None
            st.rerun()

        for difficulty in ["Easy", "Medium", "Hard"]:
            questions = st.session_state.practice_data.get(difficulty, [])
            if questions:
                st.markdown(f"### {difficulty} Level")
                for i, q in enumerate(questions):
                    st.markdown(f"**Q{i+1}: {q.get('question', '')}**")
                    with st.expander("View Solution"):
                        st.markdown(q.get('solution', ''))
                st.divider()

        from utils.export import export_pdf, export_docx
        st.markdown("### 📥 Export Practice Questions")
        col1, col2 = st.columns(2)
        with col1:
            try:
                pdf_bytes = export_pdf("VidNote AI - Practice Questions", st.session_state.practice_data, "practice")
                st.download_button(
                    label="📕 Download PDF",
                    data=pdf_bytes,
                    file_name="vidnote_practice.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Failed to generate PDF: {e}")
        with col2:
            try:
                docx_bytes = export_docx("VidNote AI - Practice Questions", st.session_state.practice_data, "practice")
                st.download_button(
                    label="📘 Download DOCX",
                    data=docx_bytes,
                    file_name="vidnote_practice.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Failed to generate DOCX: {e}")
