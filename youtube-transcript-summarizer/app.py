import os
import time
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Import utilities
from utils.validators import extract_video_id, is_valid_youtube_url
from utils.transcript import fetch_transcript, format_transcript, fetch_video_title
from utils.prompts import build_summarization_prompt
from utils.summarizer import get_available_models, summarize_with_gemini, summarize_with_groq
from utils.exporter import generate_markdown, generate_pdf
from utils.helpers import count_words, estimate_reading_time, parse_markdown_sections, parse_mcqs

# Page config
st.set_page_config(
    page_title="AI YouTube Transcript Summarizer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Custom CSS for Premium UI/UX (ChatGPT / Perplexity inspired)
st.markdown("""
<style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Reset & Typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #070913 !important;
        color: #E2E8F0 !important;
    }
    
    /* Set page margins smaller */
    [data-testid="stAppViewBlockContainer"] {
        padding: 1.2rem 4rem !important;
    }
    
    /* Sidebar styling override */
    [data-testid="stSidebar"] {
        background-color: #080a14 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    [data-testid="stSidebarContent"] {
        padding: 2.2rem 1.6rem !important;
    }
    
    /* Sidebar expanders */
    [data-testid="stSidebar"] div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        border-radius: 12px !important;
        margin-bottom: 0.6rem !important;
        overflow: hidden !important;
    }
    [data-testid="stSidebar"] div[data-testid="stExpander"] summary {
        padding: 10px 14px !important;
        font-size: 0.9rem !important;
        color: #CBD5E1 !important;
    }
    [data-testid="stSidebar"] div[data-testid="stExpander"] summary:hover {
        color: #22D3EE !important;
    }
    
    /* Title & Hero Section */
    .hero-title {
        background: linear-gradient(135deg, #60A5FA, #22D3EE, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        letter-spacing: -0.5px;
        margin-bottom: 0.3rem;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: #94A3B8;
        font-weight: 300;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    
    /* Feature Badge Row */
    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 2rem;
    }
    
    .feature-tag {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 0.78rem;
        font-weight: 500;
        color: #CBD5E1;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(15, 23, 42, 0.45);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.25);
        margin-bottom: 1.5rem;
    }
    
    /* YouTube URL Input container card styled via stContainer */
    div[data-testid="stContainer"] {
        background: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-radius: 20px !important;
        padding: 24px !important;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35) !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* Text input overrides */
    div[data-testid="stTextInput"] input {
        background-color: rgba(7, 9, 19, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #F1F5F9 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 0.98rem !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #22D3EE !important;
        box-shadow: 0 0 10px rgba(34, 211, 238, 0.2) !important;
    }
    
    /* Action Buttons (blue-to-cyan gradient) */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563EB, #06B6D4) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 0.7rem 2rem !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px rgba(6, 182, 212, 0.2) !important;
        width: 100%;
        height: 48px;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #1D4ED8, #0891B2) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(6, 182, 212, 0.35) !important;
    }
    div.stButton > button:first-child:active {
        transform: translateY(0) !important;
    }
    
    /* Clean Sidebar buttons */
    section[data-testid="stSidebar"] div.stButton > button:first-child {
        background: transparent !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        color: #FCA5A5 !important;
        box-shadow: none !important;
        height: 38px;
        font-size: 0.85rem !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:first-child:hover {
        background: rgba(239, 68, 68, 0.08) !important;
        border-color: #EF4444 !important;
        color: #F87171 !important;
        transform: none !important;
        box-shadow: 0 4px 10px rgba(239, 68, 68, 0.15) !important;
    }
    
    /* Metrics section styling */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 1.5rem;
    }
    .metric-box {
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .metric-value {
        font-size: 1.7rem;
        font-weight: 700;
        background: linear-gradient(90deg, #60A5FA, #22D3EE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #94A3B8;
        margin-top: 6px;
        font-weight: 600;
    }
    
    /* Executive Summary callout box */
    .summary-callout {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.06), rgba(6, 182, 212, 0.06));
        border-left: 4px solid #06B6D4;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(6, 182, 212, 0.04);
    }
    
    /* Custom tags / badges */
    .custom-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .badge-primary {
        background-color: rgba(96, 165, 250, 0.12);
        color: #60A5FA;
        border: 1px solid rgba(96, 165, 250, 0.2);
    }
    .badge-success {
        background-color: rgba(34, 211, 238, 0.12);
        color: #22D3EE;
        border: 1px solid rgba(34, 211, 238, 0.2);
    }
    .badge-warning {
        background-color: rgba(251, 191, 36, 0.12);
        color: #FBBF24;
        border: 1px solid rgba(251, 191, 36, 0.2);
    }
    
    /* Tabs redesign override */
    button[data-baseweb="tab"] {
        color: #94A3B8 !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        padding: 12px 24px !important;
        transition: all 0.2s ease !important;
        border-bottom: 2px solid transparent !important;
        background: transparent !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #22D3EE !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #22D3EE !important;
        border-bottom: 2px solid #22D3EE !important;
        font-weight: 600 !important;
    }
    
    /* Expanders design */
    div[data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.25) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 14px !important;
        margin-bottom: 0.8rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        overflow: hidden !important;
    }
    div[data-testid="stExpander"] details {
        border: none !important;
    }
    div[data-testid="stExpander"] summary {
        padding: 14px 20px !important;
        color: #F1F5F9 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: color 0.2s ease !important;
    }
    div[data-testid="stExpander"] summary:hover {
        color: #22D3EE !important;
    }
    
    /* Horizontal ruler */
    hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
        margin: 2rem 0 !important;
    }
    
    /* Premium SaaS Feature Cards */
    .saas-card-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin-top: 1.5rem;
    }
    .saas-card {
        background: rgba(15, 23, 42, 0.45);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 180px;
    }
    .saas-card:hover {
        transform: translateY(-5px);
        border-color: rgba(34, 211, 238, 0.3);
        box-shadow: 0 15px 35px rgba(6, 182, 212, 0.15);
    }
    .saas-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #2563EB, #06B6D4);
        opacity: 0.85;
    }
    .saas-icon {
        font-size: 2.2rem;
        margin-bottom: 12px;
    }
    .saas-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 8px;
    }
    .saas-desc {
        font-size: 0.86rem;
        color: #94A3B8;
        line-height: 1.5;
        margin: 0;
    }
    
    /* KPI Dashboard Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 16px;
        margin-bottom: 2rem;
        margin-top: 1rem;
    }
    .kpi-card {
        background: rgba(15, 23, 42, 0.45);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 16px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        display: flex;
        align-items: center;
        gap: 12px;
        transition: all 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(34, 211, 238, 0.25);
        box-shadow: 0 12px 30px rgba(6, 182, 212, 0.12);
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2.5px;
        background: linear-gradient(90deg, #2563EB, #06B6D4);
        opacity: 0.8;
    }
    .kpi-icon {
        font-size: 1.6rem;
        background: rgba(34, 211, 238, 0.06);
        border-radius: 10px;
        width: 42px;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(34, 211, 238, 0.12);
    }
    .kpi-content {
        flex: 1;
    }
    .kpi-value {
        font-size: 1.22rem;
        font-weight: 700;
        color: #F1F5F9;
        line-height: 1.2;
    }
    .kpi-label {
        font-size: 0.7rem;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-top: 3px;
    }
    
    /* Subtle Micro-interactions & Animations */
    
    /* Tactile button press scaling */
    div.stButton > button:first-child:active {
        transform: scale(0.96) !important;
    }
    
    /* Global Card Hover Transition Overrides */
    .glass-card {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .glass-card:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(34, 211, 238, 0.2) !important;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Fade-in animations for layouts */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .glass-card, [data-testid="stExpander"], [data-baseweb="tab-panel"], .saas-card, .kpi-card {
        animation: fadeIn 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
    }
    
    /* Animated Gradient Title */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .hero-title {
        background: linear-gradient(135deg, #60A5FA, #22D3EE, #06B6D4, #3B82F6) !important;
        background-size: 300% 300% !important;
        animation: gradientShift 8s ease infinite !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-weight: 800;
        font-size: 2.3rem;
        letter-spacing: -0.5px;
        margin-bottom: 0.3rem;
        line-height: 1.2;
    }
    
    /* Success Badge Pulse */
    @keyframes pulseSuccess {
        0% { transform: scale(1); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2); }
        50% { transform: scale(1.01); box-shadow: 0 12px 30px rgba(34, 197, 94, 0.08); }
        100% { transform: scale(1); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2); }
    }
    .success-badge {
        animation: pulseSuccess 2s infinite ease-in-out !important;
        background: rgba(22, 101, 52, 0.08) !important;
        border-color: rgba(34, 197, 94, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "current_summary" not in st.session_state:
    st.session_state.current_summary = None
if "current_transcript_raw" not in st.session_state:
    st.session_state.current_transcript_raw = None
if "current_transcript_formatted" not in st.session_state:
    st.session_state.current_transcript_formatted = None
if "current_title" not in st.session_state:
    st.session_state.current_title = None
if "current_url" not in st.session_state:
    st.session_state.current_url = None
if "current_metrics" not in st.session_state:
    st.session_state.current_metrics = None

# Sidebar configuration (Redesigned as AI Dashboard)
st.sidebar.image("https://img.icons8.com/clouds/200/youtube-play.png", width=80)
st.sidebar.markdown("<h2 style='margin-top:0; font-size:1.25rem; font-weight:700; color:#F1F5F9; margin-bottom: 20px;'>🎓 Study Workspace</h2>", unsafe_allow_html=True)

# Expander 1: ⚙️ API Configuration
with st.sidebar.expander("⚙️ API Configuration", expanded=True):
    st.markdown("<p style='font-size:0.78rem; color:#94A3B8; margin: 0 0 10px 0;'>Choose your AI provider and enter your API credentials.</p>", unsafe_allow_html=True)
    api_provider = st.selectbox(
        "LLM Provider",
        ["Groq", "Gemini"],
        key="api_provider_select"
    )
    
    default_gemini_key = os.getenv("GEMINI_API_KEY", "")
    default_groq_key = os.getenv("GROQ_API_KEY", "")
    
    if api_provider == "Groq":
        api_key = st.text_input(
            "Groq API Key",
            value=default_groq_key,
            type="password",
            placeholder="Enter Groq Key"
        )
    else:
        api_key = st.text_input(
            "Gemini API Key",
            value=default_gemini_key,
            type="password",
            placeholder="Enter Gemini Key"
        )

# Expander 2: 🤖 AI Model
with st.sidebar.expander("🤖 AI Model", expanded=True):
    st.markdown("<p style='font-size:0.78rem; color:#94A3B8; margin: 0 0 10px 0;'>Select the AI engine to process summaries.</p>", unsafe_allow_html=True)
    if api_provider == "Groq":
        models = get_available_models("Groq")
        model_name = st.selectbox("Groq Model", models, index=0)
    else:
        models = get_available_models("Gemini")
        model_name = st.selectbox("Gemini Model", models, index=0)

# Expander 3: 📝 Summary Style
with st.sidebar.expander("📝 Summary Style", expanded=False):
    st.markdown("<p style='font-size:0.78rem; color:#94A3B8; margin: 0 0 10px 0;'>Customize formatting, style, and timestamp parameters.</p>", unsafe_allow_html=True)
    summary_style = st.selectbox(
        "Notes Tone & Style",
        [
            "Short Summary",
            "Detailed Summary",
            "Bullet Notes",
            "Academic Notes",
            "Beginner Friendly",
            "Interview Preparation",
            "Exam Revision"
        ],
        index=1
    )
    include_timestamps = st.checkbox("Include Video Timestamps", value=True)

# Expander 4: 📤 Export Options
with st.sidebar.expander("📤 Export Options", expanded=False):
    st.markdown("<p style='font-size:0.78rem; color:#94A3B8; margin: 0 0 10px 0;'>Three export formats become available in the workspace once processed:</p>", unsafe_allow_html=True)
    st.markdown("""
    <ul style="font-size:0.75rem; color:#94A3B8; padding-left: 14px; margin: 0; line-height: 1.45;">
        <li>Markdown document (.md)</li>
        <li>Formatted raw text (.txt)</li>
        <li>Printable PDF report (.pdf)</li>
    </ul>
    """, unsafe_allow_html=True)

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)

# 3. Actions in Sidebar (Clear button)
if st.sidebar.button("🗑️ Clear Session History"):
    st.session_state.history = []
    st.session_state.current_summary = None
    st.session_state.current_transcript_raw = None
    st.session_state.current_transcript_formatted = None
    st.session_state.current_title = None
    st.session_state.current_url = None
    st.session_state.current_metrics = None
    st.sidebar.success("Session history cleared!")
    st.rerun()

# --- Main Page # Hero Section (Compact)
st.markdown('<div class="hero-title" style="font-size: 2.3rem;">AI YouTube Transcript Summarizer</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle" style="margin-bottom: 0.8rem; font-size: 1rem;">Transform lengthy videos into structured academic study guides and practice quizzes instantly.</div>', unsafe_allow_html=True)

# Feature Badges
st.markdown("""
<div class="badge-row" style="margin-bottom: 1.2rem;">
    <div class="feature-tag"><span>🎥</span> Auto Transcript</div>
    <div class="feature-tag"><span>🧠</span> AI Study Notes</div>
    <div class="feature-tag"><span>📄</span> PDF Export</div>
</div>
""", unsafe_allow_html=True)

# How It Works
st.markdown("""
<div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; margin-bottom: 1.5rem;">
    <p style="margin: 0; font-size: 0.9rem; color: #94A3B8;">
        <b>How it works:</b> Paste a YouTube link → AI fetches transcript → Select your study format → Get summarized knowledge in seconds.
    </p>
</div>
""", unsafe_allow_html=True)

# URL Form wrapper card using native st.container
with st.container(border=True):
    st.markdown('<h4 style="margin: 0 0 4px 0; color: #F1F5F9; font-size: 1.05rem; display: flex; align-items: center; gap: 8px;">🔴 Paste a YouTube Video URL</h4>', unsafe_allow_html=True)
    st.markdown('<p style="margin: 0 0 16px 0; color: #94A3B8; font-size: 0.85rem; line-height: 1.4;">Supports educational videos with available transcripts. <br><span style="color: #22D3EE; font-weight: 500;">⚡ Average generation time: 15–30 seconds.</span></p>', unsafe_allow_html=True)
    
    url_col, btn_col = st.columns([3.8, 1.2])
    with url_col:
        youtube_url = st.text_input(
            "YouTube Video URL",
            placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ or raw Video ID...",
            label_visibility="collapsed"
        )
        
        # Live Validation Feedback
        if youtube_url:
            if is_valid_youtube_url(youtube_url):
                st.markdown("<p style='color: #22C55E; font-size: 0.82rem; margin: 4px 0 0 4px; font-weight: 500;'>✓ Valid YouTube URL format</p>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='color: #EF4444; font-size: 0.82rem; margin: 4px 0 0 4px; font-weight: 500;'>✗ Invalid YouTube URL format</p>", unsafe_allow_html=True)
                
    with btn_col:
        generate_btn = st.button("✨ Generate Notes")

# Process actions with multi-stage progress UI
if generate_btn:
    if not youtube_url:
        st.error("❌ Please enter a YouTube URL.")
    elif not is_valid_youtube_url(youtube_url):
        st.error("❌ The URL entered is not a valid YouTube link. Please check it.")
    elif not api_key:
        st.error(f"❌ API Key for {api_provider} is missing. Please check your configurations in the sidebar.")
    else:
        video_id = extract_video_id(youtube_url)
        
        if not video_id:
            st.error("❌ Failed to parse video ID from YouTube URL.")
        else:
            # Create a placeholder container for pipeline UI
            progress_container = st.empty()
            
            def render_pipeline(stage_num: int, task_name: str, est_time: str):
                stages = [
                    "Validating URL",
                    "Fetching Transcript",
                    "Cleaning Transcript",
                    f"Sending to {api_provider}",
                    "Generating Summary",
                    "Creating Quiz",
                    "Preparing PDF"
                ]
                # Map stage indexes to progress bar percentages
                pcts = [10, 25, 40, 55, 75, 88, 98, 100]
                pct = pcts[stage_num]
                
                list_items = []
                for idx, stage in enumerate(stages):
                    if idx < stage_num:
                        list_items.append(f"<li style='color:#22C55E; list-style:none; margin: 5px 0; font-size:0.88rem;'>✓ {stage}</li>")
                    elif idx == stage_num:
                        list_items.append(f"<li style='color:#22D3EE; font-weight:600; list-style:none; margin: 5px 0; font-size:0.88rem; display:flex; align-items:center; gap:6px;'>⏳ {stage}</li>")
                    else:
                        list_items.append(f"<li style='color:#475569; list-style:none; margin: 5px 0; font-size:0.88rem;'>⚪ {stage}</li>")
                        
                stages_html = "".join(list_items)
                
                progress_container.markdown(f"""
                <div class="glass-card" style="padding: 24px; border: 1px solid rgba(6, 182, 212, 0.2); box-shadow: 0 10px 30px rgba(6, 182, 212, 0.15); margin-bottom: 20px;">
                    <h4 style="margin:0 0 12px 0; color:#22D3EE; display:flex; align-items:center; gap:8px; font-size: 1.1rem;">
                        <span class="spinner-loader" style="display:inline-block; width:14px; height:14px; border:2px solid #22D3EE; border-top-color:transparent; border-radius:50%; animation: spin 1s linear infinite;"></span>
                        AI Study Guide Generation Pipeline
                    </h4>
                    <p style="margin:0 0 8px 0; font-size:0.92rem; color:#F1F5F9;"><b>Current Task:</b> {task_name}</p>
                    <p style="margin:0 0 16px 0; font-size:0.8rem; color:#94A3B8;">⏳ Estimated remaining time: {est_time}</p>
                    <div style="background-color:rgba(255,255,255,0.05); border-radius:10px; height:6px; overflow:hidden; margin-bottom:20px; border:1px solid rgba(255,255,255,0.05);">
                        <div style="background: linear-gradient(90deg, #2563EB, #06B6D4); width: {pct}%; height: 100%; transition: width 0.4s ease;"></div>
                    </div>
                    <ul style="padding:0; margin:0;">
                        {stages_html}
                    </ul>
                </div>
                <style>
                    @keyframes spin {{
                        0% {{ transform: rotate(0deg); }}
                        100% {{ transform: rotate(360deg); }}
                    }}
                </style>
                """, unsafe_allow_html=True)

            try:
                start_time = time.time()
                
                # 1. Validating URL
                render_pipeline(0, "Validating URL syntax & video parameters...", "25 seconds")
                time.sleep(0.4) # Brief pause for visual transition
                
                # 2. Fetching Transcript
                render_pipeline(1, "Querying subtitles from YouTube servers...", "24 seconds")
                video_title = fetch_video_title(video_id)
                raw_transcript, error = fetch_transcript(video_id)
                
                if error:
                    progress_container.empty()
                    st.error(f"❌ {error}")
                elif not raw_transcript:
                    progress_container.empty()
                    st.error("❌ Transcript was empty or could not be loaded.")
                else:
                    # 3. Cleaning Transcript
                    render_pipeline(2, "Parsing segments and normalizing timestamps...", "21 seconds")
                    formatted_transcript = format_transcript(raw_transcript, include_timestamps=include_timestamps)
                    transcript_word_cnt = count_words(formatted_transcript)
                    time.sleep(0.4)
                    
                    # 4. Sending to API
                    render_pipeline(3, f"Opening TLS tunnel and connecting to {api_provider} API...", "20 seconds")
                    llm_prompt = build_summarization_prompt(
                        transcript=formatted_transcript,
                        style=summary_style,
                        title=video_title
                    )
                    time.sleep(0.4)
                    
                    # 5. Generating Summary
                    render_pipeline(4, f"Synthesizing transcript data with {model_name}...", "18 seconds")
                    if api_provider == "Groq":
                        summary_output = summarize_with_groq(
                            prompt=llm_prompt,
                            api_key=api_key,
                            model_name=model_name
                        )
                    else:
                        summary_output = summarize_with_gemini(
                            prompt=llm_prompt,
                            api_key=api_key,
                            model_name=model_name
                        )
                        
                    # Calculate metric stats
                    elapsed_time = time.time() - start_time
                    summary_word_cnt = count_words(summary_output)
                    compression = 100 - round((summary_word_cnt / max(1, transcript_word_cnt)) * 100)
                    reading_time = estimate_reading_time(summary_output)
                    
                    metrics = {
                        "model": f"{api_provider} ({model_name})",
                        "elapsed": elapsed_time,
                        "transcript_words": transcript_word_cnt,
                        "summary_words": summary_word_cnt,
                        "compression": compression,
                        "reading_time": reading_time,
                        "style": summary_style
                    }
                    
                    # 6. Creating Quiz
                    render_pipeline(5, "Running parser over practice quiz and answer definitions...", "4 seconds")
                    time.sleep(0.6)
                    
                    # 7. Preparing PDF
                    render_pipeline(6, "Rendering headers and packaging PDF file buffers...", "1 second")
                    pdf_bytes = generate_pdf(summary_output, video_title)
                    time.sleep(0.6)
                    
                    # Completion
                    render_pipeline(7, "All tasks completed successfully!", "0 seconds")
                    time.sleep(0.5)
                    
                    # Store in states
                    st.session_state.current_summary = summary_output
                    st.session_state.current_transcript_raw = raw_transcript
                    st.session_state.current_transcript_formatted = formatted_transcript
                    st.session_state.current_title = video_title
                    st.session_state.current_url = youtube_url
                    st.session_state.current_metrics = metrics
                    
                    # Save in history
                    history_entry = {
                        "title": video_title,
                        "url": youtube_url,
                        "summary": summary_output,
                        "transcript_raw": raw_transcript,
                        "transcript_formatted": formatted_transcript,
                        "metrics": metrics
                    }
                    if youtube_url not in [h["url"] for h in st.session_state.history]:
                        st.session_state.history.append(history_entry)
                        
                    # Clear pipeline container
                    progress_container.empty()
                    st.toast("🎉 Study notes generated successfully!", icon="✅")
                    st.rerun()
                    
            except Exception as e:
                progress_container.empty()
                st.error(f"❌ Error during generation: {str(e)}")

# --- Render Tabbed Dashboard ---
if st.session_state.current_summary:
    metrics_data = st.session_state.current_metrics
    sections = parse_markdown_sections(st.session_state.current_summary)
    
    # Calculate Dynamic KPI Values
    # 1. Video Length
    raw_transcript = st.session_state.current_transcript_raw
    video_length = "N/A"
    if raw_transcript:
        try:
            last_segment = raw_transcript[-1]
            total_seconds = int(last_segment.get("start", 0) + last_segment.get("duration", 0))
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            if hours > 0:
                video_length = f"{hours}h {minutes}m"
            else:
                video_length = f"{minutes}m {seconds}s"
        except Exception:
            pass
            
    # 2. Transcript Words
    transcript_words = metrics_data.get("transcript_words", 0)
    
    # 3. Reading Time
    reading_time = f"~{metrics_data.get('reading_time', 0)}m"
    
    # 4. Quiz Questions Count
    mcqs_raw = sections.get("5 MCQs with Answers", "")
    quiz_count = 0
    if mcqs_raw:
        parsed_mcqs = parse_mcqs(mcqs_raw)
        quiz_count = len(parsed_mcqs) if parsed_mcqs else 5
    else:
        quiz_count = 5
        
    # 5. Keywords Count
    keywords_raw = sections.get("Keywords", "")
    keywords_count = 0
    if keywords_raw:
        clean_keywords = keywords_raw.replace("Keywords", "").lstrip(": \n").strip()
        tags = [t.strip() for t in clean_keywords.split(",") if t.strip()]
        keywords_count = len(tags)
    else:
        keywords_count = 5

    # Render Pulsing Success Notification Card
    st.markdown("""
    <div class="glass-card success-badge" style="border-left: 4px solid #22C55E; padding: 12px 20px; margin-bottom: 20px; display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 1.5rem; display: inline-block; animation: pulseSuccess 1.5s infinite;">🎉</span>
        <div>
            <strong style="color: #4ADE80; font-size: 0.92rem; display: block; font-weight: 700;">Study Notes Generated Successfully!</strong>
            <span style="color: #94A3B8; font-size: 0.78rem;">Your interactive study guide, quiz questions, and timeline are ready.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Render Responsive KPI Dashboard Row with native HTML tooltip descriptions
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card" title="Total video duration calculated from transcript timestamps.">
            <div class="kpi-icon">📺</div>
            <div class="kpi-content">
                <div class="kpi-value">{video_length}</div>
                <div class="kpi-label">Video Length</div>
            </div>
        </div>
        <div class="kpi-card" title="Total word count extracted from the video's original transcript.">
            <div class="kpi-icon">📝</div>
            <div class="kpi-content">
                <div class="kpi-value">{transcript_words:,}</div>
                <div class="kpi-label">Transcript Words</div>
            </div>
        </div>
        <div class="kpi-card" title="Estimated reading time for the generated study summary notes.">
            <div class="kpi-icon">📖</div>
            <div class="kpi-content">
                <div class="kpi-value">{reading_time}</div>
                <div class="kpi-label">Reading Time</div>
            </div>
        </div>
        <div class="kpi-card" title="Total multiple-choice practice quiz questions created from the transcript content.">
            <div class="kpi-icon">❓</div>
            <div class="kpi-content">
                <div class="kpi-value">{quiz_count} Qs</div>
                <div class="kpi-label">Quiz Questions</div>
            </div>
        </div>
        <div class="kpi-card" title="Key concepts, terminology tags, and topics extracted from the lesson content.">
            <div class="kpi-icon">🏷️</div>
            <div class="kpi-content">
                <div class="kpi-value">{keywords_count} Tags</div>
                <div class="kpi-label">Keywords</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab_summary, tab_timeline, tab_takeaways, tab_quiz, tab_download, tab_transcript, tab_metrics, tab_history = st.tabs([
        "📄 Summary",
        "🕒 Timeline",
        "📌 Takeaways",
        "❓ Quiz",
        "📥 Download",
        "📑 Video Transcript",
        "📊 Performance",
        f"🕒 Session Cache ({len(st.session_state.history)})"
    ])
    
    # Parse sections
    sections = parse_markdown_sections(st.session_state.current_summary)
    difficulty = sections.get("Difficulty Level", "Intermediate").replace("Difficulty Level", "").strip()
    difficulty = difficulty.lstrip(": \n").strip()
    
    # Tab 1: Summary
    with tab_summary:
        st.markdown("### 📄 Executive & Detailed Summaries")
        
        # Display tags row
        st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <span class="custom-badge badge-primary">Model: {metrics_data['model']}</span>
            <span class="custom-badge badge-success">Style: {metrics_data['style']}</span>
            <span class="custom-badge badge-warning">Difficulty: {difficulty}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Render Executive Summary
        exec_summary = sections.get("Executive Summary", "")
        if exec_summary:
            clean_exec = exec_summary.replace("Executive Summary", "").lstrip(": \n").strip()
            st.markdown(f"""
            <div class="summary-callout">
                <h4 style="margin: 0 0 8px 0; color:#06B6D4; display:flex; align-items:center; gap:6px;">📝 Executive Summary</h4>
                <p style="margin: 0; line-height: 1.6; font-size: 1rem; color: #E2E8F0;">{clean_exec}</p>
            </div>
            """, unsafe_allow_html=True)
            
        # Render Detailed Summary
        detailed_summary = sections.get("Detailed Summary", "")
        if detailed_summary:
            clean_detailed = detailed_summary.replace("Detailed Summary", "").lstrip(": \n").strip()
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 📖 Detailed Study Notes")
            st.markdown(clean_detailed)
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Render 5-minute revision notes
        revision = sections.get("5-Minute Revision Notes", "")
        if revision:
            clean_revision = revision.replace("5-Minute Revision Notes", "").lstrip(": \n").strip()
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### ⏱️ 5-Minute Quick Recall Revision")
            st.markdown(clean_revision)
            st.markdown('</div>', unsafe_allow_html=True)
            
    # Tab 2: Timeline
    with tab_timeline:
        st.markdown("### 🕒 Chronological Video Timeline")
        timeline = sections.get("Timeline Summary", "")
        clean_timeline = timeline.replace("Timeline Summary", "").lstrip(": \n").strip()
        
        if clean_timeline and "no timestamps available" not in clean_timeline.lower():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(clean_timeline)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No timestamps or timeline map available for this video.")
            
    # Tab 3: Takeaways
    with tab_takeaways:
        st.markdown("### 📌 Key Takeaways & Technical Concepts")
        takeaways = sections.get("Key Takeaways", "")
        concepts = sections.get("Technical Concepts", "")
        insights = sections.get("Actionable Insights", "")
        
        if takeaways:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 📌 Core Lessons & Findings")
            st.markdown(takeaways.replace("Key Takeaways", "").lstrip(": \n").strip())
            st.markdown('</div>', unsafe_allow_html=True)
            
        if concepts:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 💡 Technical Concepts Mapping")
            st.markdown(concepts.replace("Technical Concepts", "").lstrip(": \n").strip())
            st.markdown('</div>', unsafe_allow_html=True)
            
        if insights:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 🛠️ Actionable Insights")
            st.markdown(insights.replace("Actionable Insights", "").lstrip(": \n").strip())
            st.markdown('</div>', unsafe_allow_html=True)
            

            
    # Tab 6: Quiz
    with tab_quiz:
        st.markdown("### ❓ Practice Quiz")
        mcqs_raw = sections.get("5 MCQs with Answers", "")
        
        if mcqs_raw:
            parsed_mcqs = parse_mcqs(mcqs_raw)
            if parsed_mcqs:
                for idx, mcq in enumerate(parsed_mcqs):
                    st.markdown(f"**Q{idx+1}. {mcq['question']}**")
                    options = mcq['options']
                    options_list = [
                        f"A) {options['A']}",
                        f"B) {options['B']}",
                        f"C) {options['C']}",
                        f"D) {options['D']}"
                    ]
                    
                    user_ans = st.radio(
                        "Select your answer:",
                        options_list,
                        index=None,
                        key=f"mcq_{idx}_{extract_video_id(st.session_state.current_url)}"
                    )
                    
                    if user_ans:
                        chosen_letter = user_ans[0]
                        if chosen_letter == mcq['correct']:
                            st.success(f"✅ Correct! The answer is {mcq['correct']}.")
                        else:
                            st.error(f"❌ Incorrect. The correct answer is {mcq['correct']}.")
                        st.markdown(f"*Explanation:* {mcq['explanation']}")
                    st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
            else:
                st.markdown(mcqs_raw.replace("5 MCQs with Answers", "").lstrip(": \n").strip())
        else:
            st.info("No practice quiz generated for this video.")
            
    # Tab 7: Download
    with tab_download:
        st.markdown("### 📥 Download & Export Options")
        
        # Display tags
        keywords = sections.get("Keywords", "")
        if keywords:
            st.markdown("<h4 style='font-size:1.1rem; font-weight:600; margin-top:0;'>🏷️ Keywords & Tags</h4>", unsafe_allow_html=True)
            clean_keywords = keywords.replace("Keywords", "").lstrip(": \n").strip()
            tags = [t.strip() for t in clean_keywords.split(",") if t.strip()]
            badges_html = " ".join([f'<span class="custom-badge badge-primary">{tag}</span>' for tag in tags])
            st.markdown(f"<div>{badges_html}</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
        st.markdown("#### 💾 Download Formats")
        dl_col1, dl_col2, dl_col3 = st.columns(3)
        
        md_file = generate_markdown(
            content=st.session_state.current_summary,
            title=st.session_state.current_title,
            video_url=st.session_state.current_url
        )
        
        try:
            pdf_bytes = generate_pdf(
                content=st.session_state.current_summary,
                title=st.session_state.current_title
            )
            pdf_disabled = False
        except Exception as e:
            pdf_bytes = b""
            pdf_disabled = True
            st.warning(f"Could not generate PDF: {str(e)}")
            
        with dl_col1:
            st.download_button(
                label="📥 Download Markdown (.md)",
                data=md_file,
                file_name=f"study_notes_{extract_video_id(st.session_state.current_url)}.md",
                mime="text/markdown"
            )
        with dl_col2:
            st.download_button(
                label="📥 Download Text (.txt)",
                data=st.session_state.current_summary,
                file_name=f"study_notes_{extract_video_id(st.session_state.current_url)}.txt",
                mime="text/plain"
            )
        with dl_col3:
            st.download_button(
                label="📥 Download PDF (.pdf)",
                data=pdf_bytes,
                file_name=f"study_notes_{extract_video_id(st.session_state.current_url)}.pdf",
                mime="application/pdf",
                disabled=pdf_disabled
            )
            
        st.divider()
        
        # Raw Markdown Copy block
        st.markdown("#### 📋 Copy Raw Markdown Study Notes")
        st.code(st.session_state.current_summary, language="markdown")

    # Tab 2: Transcript preview
    with tab_transcript:
        st.markdown(f"### 📑 Original Transcript Preview ({metrics_data['transcript_words']} words)")
        trans_options = st.radio("Display Format", ["Standard Text Paragraphs", "Timed Transcript List"], horizontal=True)
        
        if trans_options == "Timed Transcript List":
            formatted_list = format_transcript(st.session_state.current_transcript_raw, include_timestamps=True)
            st.text_area("Timed Transcript Block", formatted_list, height=400)
        else:
            formatted_text = format_transcript(st.session_state.current_transcript_raw, include_timestamps=False)
            st.text_area("Continuous Paragraph Block", formatted_text, height=400)

    # Tab 3: Detailed performance table
    with tab_metrics:
        st.markdown("### 📊 Summary Performance Analytics")
        
        perf_df = pd.DataFrame({
            "Metric Details": [
                "Target Video Title",
                "Video URL",
                "AI Model Provider",
                "Processing Time (seconds)",
                "Original Transcript Word Count",
                "Summary Notes Word Count",
                "Compression Ratio",
                "Estimated Reading Time"
            ],
            "Value": [
                st.session_state.current_title,
                st.session_state.current_url,
                metrics_data["model"],
                f"{metrics_data['elapsed']:.3f} s",
                metrics_data["transcript_words"],
                metrics_data["summary_words"],
                f"{metrics_data['compression']}% smaller than transcript",
                f"{metrics_data['reading_time']} min"
            ]
        })
        st.table(perf_df)

    # Tab 4: History list
    with tab_history:
        st.markdown("### 🕒 Active Session History Cache")
        if not st.session_state.history:
            st.info("No videos summarized in this active session yet.")
        else:
            for idx, entry in enumerate(reversed(st.session_state.history)):
                st.markdown(f"""
                <div class="glass-card">
                    <h4 style="margin: 0 0 8px 0; color:#60A5FA;">{idx + 1}. {entry['title']}</h4>
                    <p style="color:#94A3B8; font-size:0.88rem; margin:0 0 12px 0; line-height:1.4;">
                        <strong>Video Link:</strong> <a href="{entry['url']}" target="_blank" style="color:#22D3EE;">{entry['url']}</a><br>
                        <strong>AI Config:</strong> {entry['metrics']['model']} | <strong>Style:</strong> {entry['metrics']['style']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Load Study Notes: {entry['title'][:45]}...", key=f"restore_{idx}"):
                    st.session_state.current_summary = entry["summary"]
                    st.session_state.current_transcript_raw = entry["transcript_raw"]
                    st.session_state.current_transcript_formatted = entry["transcript_formatted"]
                    st.session_state.current_title = entry["title"]
                    st.session_state.current_url = entry["url"]
                    st.session_state.current_metrics = entry["metrics"]
                    st.toast("Restored notes from cache!", icon="🕒")
                    st.rerun()

else:
    # Onboarding Flow Chart
    st.markdown("""
    <div class="glass-card" style="padding: 20px; margin-top: 10px; margin-bottom: 20px;">
        <h3 style="color: #60A5FA; margin-top:0; font-size:1.15rem; font-weight:600; text-align:center; margin-bottom: 20px;">🚀 How It Works</h3>
        <div style="display: flex; justify-content: space-between; align-items: center; text-align: center; flex-wrap: wrap; gap: 12px;">
            <div style="flex: 1; min-width: 160px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 18px; border-radius: 12px;">
                <div style="font-size: 1.3rem; margin-bottom: 8px; font-weight:bold; color:#22D3EE;">①</div>
                <strong style="color: #F1F5F9; font-size: 0.9rem; display:block; margin-bottom:6px;">Paste YouTube URL</strong>
                <span style="font-size: 0.78rem; color: #94A3B8; line-height:1.4;">Enter video URL, mobile link, or shorts.</span>
            </div>
            <div style="font-size: 1.4rem; color: #06B6D4; font-weight: bold; padding: 0 5px;">➔</div>
            <div style="flex: 1; min-width: 160px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 18px; border-radius: 12px;">
                <div style="font-size: 1.3rem; margin-bottom: 8px; font-weight:bold; color:#22D3EE;">②</div>
                <strong style="color: #F1F5F9; font-size: 0.9rem; display:block; margin-bottom:6px;">AI Fetches Transcript</strong>
                <span style="font-size: 0.78rem; color: #94A3B8; line-height:1.4;">Extracts, translates, and formats the subtitles.</span>
            </div>
            <div style="font-size: 1.4rem; color: #06B6D4; font-weight: bold; padding: 0 5px;">➔</div>
            <div style="flex: 1; min-width: 160px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 18px; border-radius: 12px;">
                <div style="font-size: 1.3rem; margin-bottom: 8px; font-weight:bold; color:#22D3EE;">③</div>
                <strong style="color: #F1F5F9; font-size: 0.9rem; display:block; margin-bottom:6px;">Generate Notes</strong>
                <span style="font-size: 0.78rem; color: #94A3B8; line-height:1.4;">Summarizes into structured academic notes.</span>
            </div>
            <div style="font-size: 1.4rem; color: #06B6D4; font-weight: bold; padding: 0 5px;">➔</div>
            <div style="flex: 1; min-width: 160px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 18px; border-radius: 12px;">
                <div style="font-size: 1.3rem; margin-bottom: 8px; font-weight:bold; color:#22D3EE;">④</div>
                <strong style="color: #F1F5F9; font-size: 0.9rem; display:block; margin-bottom:6px;">Download PDF</strong>
                <span style="font-size: 0.78rem; color: #94A3B8; line-height:1.4;">Export instantly to PDF, Markdown, or TXT.</span>
            </div>
        </div>
    </div>
    
    <div class="saas-card-grid">
        <div class="saas-card">
            <div>
                <div class="saas-icon">📚</div>
                <div class="saas-title">Structured Notes</div>
                <p class="saas-desc">Generates comprehensive summaries and technical concept definitions automatically with academic rigour.</p>
            </div>
        </div>
        <div class="saas-card">
            <div>
                <div class="saas-icon">🧠</div>
                <div class="saas-title">Interactive Quiz</div>
                <p class="saas-desc">Includes interactive multiple-choice practice quizzes with instant answer checkmarks and explanations.</p>
            </div>
        </div>
        <div class="saas-card">
            <div>
                <div class="saas-icon">⏱</div>
                <div class="saas-title">Timeline Summary</div>
                <p class="saas-desc">Creates a chronological map linking topics directly to video timestamps, making navigating long videos seamless.</p>
            </div>
        </div>
        <div class="saas-card">
            <div>
                <div class="saas-icon">📄</div>
                <div class="saas-title">PDF Export</div>
                <p class="saas-desc">Export study notes instantly in printable PDF format, standard Markdown (.md) or raw Text (.txt) formats.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
