"""
pages/Chat.py
--------------
AI Chat with Video — ask questions about the generated notes using Gemini.
Supports conversation history, regenerate, clear, and contextual answers.
"""

import streamlit as st
from utils.gemini import generate_text
from utils.db import get_setting

# ── CSS ───────────────────────────────────────────────────────────────────────
def _inject_css():
    st.markdown("""
    <style>
    .chat-container {
        max-height: 520px;
        overflow-y: auto;
        padding: 1rem;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        margin-bottom: 1rem;
    }
    .msg-user {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 0.8rem;
    }
    .msg-user .bubble {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.7rem 1rem;
        border-radius: 18px 18px 4px 18px;
        max-width: 72%;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .msg-ai {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 0.8rem;
    }
    .msg-ai .bubble {
        background: rgba(102,126,234,0.12);
        border: 1px solid rgba(102,126,234,0.2);
        color: #e0e0f0;
        padding: 0.7rem 1rem;
        border-radius: 18px 18px 18px 4px;
        max-width: 80%;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .avatar {
        width: 32px; height: 32px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem;
        margin: 0 0.5rem;
        flex-shrink: 0;
    }
    .avatar-user { background: linear-gradient(135deg,#667eea,#764ba2); }
    .avatar-ai   { background: rgba(118,75,162,0.3); border: 1px solid rgba(118,75,162,0.4); }
    .quick-btn-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }
    .suggestion-chip {
        background: rgba(102,126,234,0.15);
        border: 1px solid rgba(102,126,234,0.3);
        color: #a0aec0;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.82rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .suggestion-chip:hover { background: rgba(102,126,234,0.3); color: #fff; }
    </style>
    """, unsafe_allow_html=True)


# ── Suggested quick prompts ───────────────────────────────────────────────────
QUICK_PROMPTS = [
    "📝 Summarise in simple terms",
    "🔍 Explain the key concept",
    "💡 Give me 3 real-world examples",
    "❓ What are the most important points?",
    "🎯 Give me 5 practice questions",
    "📚 Explain as if I'm a beginner",
    "🔗 How does this relate to real life?",
    "⚡ Give me a quick revision",
]


def _build_system_prompt(notes: str, language: str) -> str:
    return f"""You are an expert AI tutor helping a student understand a YouTube video.
You have access to the detailed study notes from the video below.
Answer all questions in a clear, helpful, and engaging manner.
Output language: {language}
Keep answers concise but complete. Use bullet points, examples, and analogies where helpful.

=== STUDY NOTES FROM THE VIDEO ===
{notes[:8000]}
=== END OF NOTES ===

Now respond to the student's question below:"""


def _chat_message_html(role: str, content: str) -> str:
    if role == "user":
        return f"""
        <div class="msg-user">
            <div class="bubble">{content}</div>
            <div class="avatar avatar-user">👤</div>
        </div>"""
    else:
        # AI — render markdown-like but safe
        safe = content.replace("<", "&lt;").replace(">", "&gt;")
        return f"""
        <div class="msg-ai">
            <div class="avatar avatar-ai">🤖</div>
            <div class="bubble">{safe}</div>
        </div>"""


def render_chat():
    _inject_css()

    st.markdown("## 💬 Chat with Your Notes")
    st.markdown("Ask anything about the video — your AI tutor is ready.")

    # ── Guard — need notes ────────────────────────────────────────────────────
    notes = st.session_state.get("notes_text", "")
    if not notes:
        st.info("📭 Please generate notes first from the **Home** page, then come back to chat.")
        return

    # ── Init session state ────────────────────────────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ── Video info ────────────────────────────────────────────────────────────
    video_id = st.session_state.get("video_id", "")
    title    = st.session_state.get("video_title", "Current Video")
    lang     = get_setting("output_language", "English")

    if video_id:
        col_img, col_title = st.columns([1, 3])
        with col_img:
            st.image(f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg", use_container_width=True)
        with col_title:
            st.markdown(f"### 🎬 {title or 'Video'}")
            st.caption(f"Language: {lang} | Messages: {len(st.session_state.chat_history)//2}")
    else:
        st.info("💡 Notes loaded. Start chatting!")

    st.divider()

    # ── Quick prompts ─────────────────────────────────────────────────────────
    st.markdown("**💡 Quick Prompts:**")
    cols = st.columns(4)
    for i, prompt in enumerate(QUICK_PROMPTS):
        if cols[i % 4].button(prompt, key=f"quick_{i}", use_container_width=True):
            st.session_state["_pending_chat"] = prompt.split(" ", 1)[1] if " " in prompt else prompt

    st.divider()

    # ── Chat history display ──────────────────────────────────────────────────
    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            chat_html += _chat_message_html(msg["role"], msg["content"])
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)

        # Regenerate last response
        col_regen, col_clear = st.columns([2, 1])
        with col_regen:
            if st.button("🔄 Regenerate Last Response", use_container_width=True):
                # Find last user message
                last_user = next(
                    (m["content"] for m in reversed(st.session_state.chat_history) if m["role"] == "user"),
                    None
                )
                if last_user:
                    # Remove last AI response
                    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "assistant":
                        st.session_state.chat_history.pop()
                    st.session_state["_pending_chat"] = last_user
                    st.rerun()
        with col_clear:
            if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
                st.session_state.chat_history = []
                st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center; padding:3rem; opacity:0.5;">
            <div style="font-size:3rem">💬</div>
            <p>No messages yet. Ask a question below or use a quick prompt above!</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Input ─────────────────────────────────────────────────────────────────
    pending = st.session_state.pop("_pending_chat", "")
    user_input = st.chat_input("Ask anything about the video…", key="chat_input")
    question = pending or user_input

    if question:
        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": question})

        # Build full prompt with conversation history
        system = _build_system_prompt(notes, lang)

        history_text = ""
        for msg in st.session_state.chat_history[:-1]:  # exclude the just-added question
            prefix = "Student" if msg["role"] == "user" else "AI Tutor"
            history_text += f"{prefix}: {msg['content']}\n"

        full_prompt = f"{system}\n\n{history_text}Student: {question}\nAI Tutor:"

        with st.spinner("🤖 Thinking…"):
            result = generate_text(full_prompt)

        if result["error"]:
            st.error(f"❌ {result['error']}")
        else:
            ai_reply = result["text"] or "I couldn't generate a response. Please try again."
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})

        st.rerun()


# ── Standalone page entry ─────────────────────────────────────────────────────
render_chat()
