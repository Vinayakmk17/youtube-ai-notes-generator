"""
pages/Settings.py
------------------
User settings page — output language, summary length, AI model,
temperature, and export preferences. All persisted via SQLite.
"""

import streamlit as st
from utils.db import get_all_settings, set_setting

def _inject_css():
    st.markdown("""
    <style>
    .settings-section {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
    }
    .settings-section h4 {
        color: #a78bfa;
        margin-bottom: 1rem;
        font-size: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .save-banner {
        background: linear-gradient(135deg, rgba(34,197,94,0.15), rgba(16,185,129,0.1));
        border: 1px solid rgba(34,197,94,0.3);
        border-radius: 12px;
        padding: 0.7rem 1rem;
        color: #6ee7b7;
        text-align: center;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)


def render_settings():
    _inject_css()

    st.markdown("## ⚙️ Settings")
    st.markdown("Customise how VidNote AI generates and exports your study materials.")
    st.divider()

    current = get_all_settings()

    # ── Helper ────────────────────────────────────────────────────────────────
    def _val(key, default=""):
        return current.get(key, default)

    changed = {}

    # ── 1. Language & Output ──────────────────────────────────────────────────
    st.markdown('<div class="settings-section"><h4>🌐 Language & Output</h4>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        lang = st.selectbox(
            "Output Language",
            ["English", "Hindi", "Kannada", "Spanish", "French", "German", "Arabic", "Japanese"],
            index=["English", "Hindi", "Kannada", "Spanish", "French", "German", "Arabic", "Japanese"].index(
                _val("output_language", "English")
            ),
            key="set_lang",
        )
        changed["output_language"] = lang

    with col2:
        length = st.selectbox(
            "Summary Length",
            ["Brief", "Standard", "Detailed"],
            index=["Brief", "Standard", "Detailed"].index(_val("summary_length", "Detailed")),
            key="set_length",
        )
        changed["summary_length"] = length
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 2. AI Model ───────────────────────────────────────────────────────────
    st.markdown('<div class="settings-section"><h4>🤖 AI Model</h4>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        model = st.selectbox(
            "Gemini Model",
            ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
            index=["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"].index(
                _val("ai_model", "gemini-2.5-flash")
            )
            if _val("ai_model", "gemini-2.5-flash") in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
            else 0,
            key="set_model",
        )
        changed["ai_model"] = model
        st.caption("gemini-2.5-flash is fastest and most cost-efficient.")

    with col4:
        try:
            temp_val = float(_val("temperature", "1.0"))
        except ValueError:
            temp_val = 1.0
        temp = st.slider(
            "Temperature (Creativity)",
            min_value=0.0, max_value=2.0, step=0.1,
            value=temp_val,
            key="set_temp",
        )
        changed["temperature"] = str(temp)
        if temp < 0.5:
            st.caption("🧊 More focused and factual")
        elif temp < 1.2:
            st.caption("⚖️ Balanced")
        else:
            st.caption("🔥 More creative and varied")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 3. Export Preferences ─────────────────────────────────────────────────
    st.markdown('<div class="settings-section"><h4>📥 Export Preferences</h4>', unsafe_allow_html=True)
    col5, col6 = st.columns(2)
    with col5:
        export_fmt = st.selectbox(
            "Default Export Format",
            ["PDF", "DOCX", "TXT"],
            index=["PDF", "DOCX", "TXT"].index(_val("export_format", "PDF")),
            key="set_export",
        )
        changed["export_format"] = export_fmt
    with col6:
        theme = st.selectbox(
            "Theme",
            ["Dark", "Light"],
            index=["Dark", "Light"].index(_val("theme", "Dark")) if _val("theme", "Dark") in ["Dark", "Light"] else 0,
            key="set_theme",
            help="Theme setting (visual reference — Streamlit theme set via config.toml)",
        )
        changed["theme"] = theme
    st.markdown("</div>", unsafe_allow_html=True)

    # ── 4. Advanced ───────────────────────────────────────────────────────────
    st.markdown('<div class="settings-section"><h4>⚡ Advanced</h4>', unsafe_allow_html=True)
    col7, col8 = st.columns(2)
    with col7:
        auto_save = st.toggle(
            "Auto-save sessions to history",
            value=_val("auto_save", "true") == "true",
            key="set_autosave",
        )
        changed["auto_save"] = "true" if auto_save else "false"
    with col8:
        show_transcript = st.toggle(
            "Show raw transcript by default",
            value=_val("show_transcript", "false") == "true",
            key="set_show_transcript",
        )
        changed["show_transcript"] = "true" if show_transcript else "false"
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Save button ───────────────────────────────────────────────────────────
    st.divider()
    col_save, col_reset = st.columns([2, 1])
    with col_save:
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            for k, v in changed.items():
                set_setting(k, v)
            # Also update session state so other pages pick up changes immediately
            for k, v in changed.items():
                st.session_state[f"_setting_{k}"] = v
            st.markdown('<div class="save-banner">✅ Settings saved successfully!</div>', unsafe_allow_html=True)
            st.balloons()

    with col_reset:
        if st.button("↺ Reset Defaults", use_container_width=True, type="secondary"):
            defaults = {
                "output_language": "English",
                "summary_length":  "Detailed",
                "ai_model":        "gemini-2.5-flash",
                "temperature":     "1.0",
                "export_format":   "PDF",
                "theme":           "Dark",
                "auto_save":       "true",
                "show_transcript": "false",
            }
            for k, v in defaults.items():
                set_setting(k, v)
            st.success("↺ Settings reset to defaults.")
            st.rerun()

    # ── Info ──────────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("""
    > 💡 **Tips**
    > - Settings are saved to a local SQLite database and persist across sessions.
    > - Change the AI model to balance speed vs quality.
    > - Increase temperature for more creative outputs; decrease for more precise answers.
    """)


# ── Standalone page entry ─────────────────────────────────────────────────────
render_settings()
