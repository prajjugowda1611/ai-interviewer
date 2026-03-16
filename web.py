import streamlit as st
import PyPDF2
import docx
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
import io
from supabase import create_client, Client

# 1. Page Setup
st.set_page_config(page_title="Fusion AI - Enterprise", page_icon="💼", layout="centered")
load_dotenv()

# --- DATABASE CONNECTION ---
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# 2. Advanced State Management
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True

# Progression Engine States
if "current_round" not in st.session_state:
    st.session_state.current_round = 1
if "question_in_round" not in st.session_state:
    st.session_state.question_in_round = 1
if "round_scores" not in st.session_state:
    st.session_state.round_scores = []
if "interview_status" not in st.session_state:
    st.session_state.interview_status = "ACTIVE"

THEMES = {
    1: "ROUND 1: Easy aptitude, basic definitions based on their resume and skills.",
    2: "ROUND 2: Applications of their skills, importance, characteristics, and differences between technologies.",
    3: "ROUND 3: Managerial skills, group discussion, project management, and final tech interview questions."
}

def play_audio(text):
    if st.session_state.voice_enabled:
        try:
            tts = gTTS(text=text, lang='en', tld='com') 
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        except:
            pass 

def extract_text(file):
    text = ""
    if file.name.endswith('.pdf'):
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    elif file.name.endswith('.docx'):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file.name.endswith('.txt'):
        text = file.getvalue().decode("utf-8")
    return text

# ==========================================
# 🔐 THE AUTHENTICATION WALL
# ==========================================
if not st.session_state.user_authenticated:
    st.title("🔐 Welcome to Fusion AI")
    st.write("Please log in or create an account to access the Interview Gauntlet.")
    st.divider()
    
    auth_mode = st.radio("Select Action:", ["Login", "Sign Up"], horizontal=True)
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    
    if st.button(auth_mode, use_container_width=True):
        if not email or not password:
            st.error("⚠️ Please enter both email and password.")
        elif auth_mode == "Sign Up":
            try:
                response = supabase.auth.sign_up({"email": email, "password": password})
                st.success("🎉 Account created successfully! You can now switch to Login.")
            except Exception as e:
                st.error(f"Signup failed. Error: {e}")
        else:
            try:
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user_authenticated = True
                st.session_state.user_email = email
                st.rerun()
            except Exception as e:
                st.error("❌ Login failed: Invalid email or password.")

# ==========================================
# 💼 THE ENTERPRISE APPLICATION (Only visible if logged in)
# ==========================================
else:
    # Sidebar Logout
    st.sidebar.write(f"👤 Logged in as: **{st.session_state.user_email}**")
    if st.sidebar.button("Log Out"):
        st.session_state.user_authenticated = False
        st.session_state.messages = []
        st.session_state.interview_started = False
        st.rerun()

    st.title("💼 AI Mock Interviewer V5")
    st.markdown("*The 15-Question Technical Gauntlet.*")
    st.divider()
    
    # ... (THE REST OF YOUR EXISTING V5 UI AND CHAT LOGIC GOES EXACTLY HERE) ...