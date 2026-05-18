import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, parse_qs

# Load API key
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

# Extract video ID
def extract_video_id(url):
    parsed_url = urlparse(url)

    if parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]

    if parsed_url.hostname in ("www.youtube.com", "youtube.com"):
        return parse_qs(parsed_url.query).get("v", [None])[0]

    return None

# Get transcript
def get_transcript(video_id):

    api = YouTubeTranscriptApi()

    transcript = api.fetch(video_id, languages=['en', 'hi'])

    text = " ".join([item.text for item in transcript])

    return text

# Generate summary
def generate_notes(transcript):
    prompt = f"""
    Summarize the following YouTube video transcript into clean study notes.

    Transcript:
    {transcript}
    """

    response = model.generate_content(prompt)

    return response.text

# Streamlit UI
import streamlit as st

# Page config
st.set_page_config(
    page_title="AI YouTube Notes",
    page_icon="🎥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }
    
    /* Hero section */
    .hero-section {
        text-align: center;
        padding: 3rem 0 2rem 0;
        margin-bottom: 2rem;
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Input container */
    .input-container {
        max-width: 700px;
        margin: 0 auto 3rem auto;
        padding: 2rem;
        background: white;
        border-radius: 16px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    /* Streamlit input customization */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 1.5px solid #e0e0e0;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4285f4;
        box-shadow: 0 0 0 3px rgba(66, 133, 244, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 500;
        cursor: pointer;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Feature cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        max-width: 900px;
        margin: 0 auto 3rem auto;
    }
    
    .feature-card {
        text-align: center;
        padding: 1.5rem;
        background: #f8f9fa;
        border-radius: 12px;
        border: 1px solid #e9ecef;
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-title {
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.25rem;
    }
    
    .feature-desc {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Hero section
st.markdown("""
<div class="hero-section">
    <div class="hero-title">🎥 AI YouTube Notes Generator</div>
    <div class="hero-subtitle">Transform any YouTube video into comprehensive notes with AI</div>
</div>
""", unsafe_allow_html=True)

# Input container
st.markdown('<div class="input-container">', unsafe_allow_html=True)

# Input field with better label
youtube_url = st.text_input(
    "YouTube Video URL",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="visible"
)

# Generate button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_button = st.button("✨ Generate Notes", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Feature cards
st.markdown("""
<div class="feature-grid">
    <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <div class="feature-title">Lightning Fast</div>
        <div class="feature-desc">Get notes in seconds</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">🎯</div>
        <div class="feature-title">AI Powered</div>
        <div class="feature-desc">Smart summarization</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📝</div>
        <div class="feature-title">Comprehensive</div>
        <div class="feature-desc">Detailed breakdowns</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">💾</div>
        <div class="feature-title">Easy Export</div>
        <div class="feature-desc">Download as text</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Your processing logic would go here
if generate_button and youtube_url:
    st.success("Processing video...")
    # Add your video processing code here

if st.button("Generate Notes"):

    video_id = extract_video_id(youtube_url)

    if video_id:

        with st.spinner("Fetching transcript..."):
            transcript = get_transcript(video_id)

        with st.spinner("Generating AI notes..."):
            notes = generate_notes(transcript)

        st.subheader("📘 AI Generated Notes")

        st.write(notes)

    else:
        st.error("Invalid YouTube URL")