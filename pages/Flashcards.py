import streamlit as st
import json
from utils.gemini import generate_json
from utils.prompts import get_flashcards_prompt

def render_flashcards(transcript_text: str):
    st.subheader("🗂️ AI Flashcards")
    
    if "flashcards_data" not in st.session_state:
        st.session_state.flashcards_data = None

    if st.session_state.flashcards_data is None:
        if st.button("Generate Flashcards ✨", key="btn_gen_flash"):
            with st.spinner("🤖 Generating 15 flashcards..."):
                prompt = get_flashcards_prompt(transcript_text)
                result = generate_json(prompt)
                
                if result["error"]:
                    st.error(f"🚫 {result['error']}")
                else:
                    try:
                        fc_json = json.loads(result["data"])
                        st.session_state.flashcards_data = fc_json
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to parse AI output: {e}")
                        with st.expander("Raw Output"):
                            st.text(result["data"])
    else:
        if st.button("🔄 Regenerate Flashcards", key="btn_regen_flash"):
            st.session_state.flashcards_data = None
            st.rerun()

        for i, card in enumerate(st.session_state.flashcards_data):
            st.markdown(f"**Card {i+1}**")
            st.info(f"🤔 **Question:** {card.get('question', '')}")
            with st.expander("Show Answer"):
                st.success(f"💡 **Answer:** {card.get('answer', '')}")
            st.divider()

        from utils.export import export_pdf, export_docx
        st.markdown("### 📥 Export Flashcards")
        col1, col2 = st.columns(2)
        with col1:
            try:
                pdf_bytes = export_pdf("VidNote AI - Flashcards", st.session_state.flashcards_data, "flashcards")
                st.download_button(
                    label="📕 Download PDF",
                    data=pdf_bytes,
                    file_name="vidnote_flashcards.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Failed to generate PDF: {e}")
        with col2:
            try:
                docx_bytes = export_docx("VidNote AI - Flashcards", st.session_state.flashcards_data, "flashcards")
                st.download_button(
                    label="📘 Download DOCX",
                    data=docx_bytes,
                    file_name="vidnote_flashcards.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Failed to generate DOCX: {e}")
