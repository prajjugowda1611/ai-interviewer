import streamlit as st
import PyPDF2
import docx
import os
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
import io
import time

# 1. Page Setup
st.set_page_config(page_title="AI Interviewer Pro", page_icon="💼", layout="centered")

# 2. Give the Web App a "Memory"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "MEDIUM"
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True

# --- VOICE ENGINE ---
def play_audio(text):
    if st.session_state.voice_enabled:
        try:
            tts = gTTS(text=text, lang='en', tld='com') 
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        except:
            pass # Fails safely if the audio engine glitches

# --- FILE EXTRACTOR ---
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

# --- FRONTEND UI ---
st.title("💼 AI Mock Interviewer V2")
st.markdown("*Upload your profile. Face the recruiter. Survive the pressure.*")
st.divider()

# Only show the setup controls if the interview hasn't started
if not st.session_state.interview_started:
    
    st.subheader("Step 1: Choose Your Input")
    input_type = st.radio("How do you want to be tested?", ["Upload Resume", "Paste Job Description"], horizontal=True)
    
    context_text = ""
    
    if input_type == "Upload Resume":
        uploaded_file = st.file_uploader("Supports PDF, DOCX, and TXT", type=["pdf", "docx", "txt"])
        if uploaded_file:
            context_text = extract_text(uploaded_file)
    else:
        context_text = st.text_area("Paste the Job Description here:", height=150, placeholder="e.g., Looking for a Junior Python Developer with experience in Pandas and SQL...")

    st.subheader("Step 2: Interview Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        selected_diff = st.selectbox(
            "Difficulty Level:",
            ["1. Easy (Friendly)", "2. Medium (Professional)", "3. Hard (Strict)", "4. Brutal (No Empathy)"],
            index=1
        )
    with col2:
        voice_toggle = st.toggle("🔊 Enable AI Voice", value=True, help="Turn off if you prefer to just read.")

    st.write("") # Spacer
    start_btn = st.button("🚀 Start Interview", use_container_width=True)

    if start_btn:
        if len(context_text.strip()) < 10:
            st.error("⚠️ Please provide a valid Resume or Job Description to begin!")
        else:
            # Fake loading bar to improve user psychology 
            progress_text = "Analyzing data and booting up the AI engine..."
            my_bar = st.progress(0, text=progress_text)
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text=progress_text)
                
            load_dotenv()
            genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            st.session_state.chat_session = model.start_chat(history=[])
            st.session_state.difficulty = selected_diff
            st.session_state.voice_enabled = voice_toggle
            st.session_state.interview_started = True 
            
            if input_type == "Upload Resume":
                fusion_prompt = f"You are a tech recruiter. The candidate is a 3rd-year student. Resume: {context_text}. Task: Find one technical skill. Difficulty: {selected_diff}. Ask ONE question based on that skill. Keep it under 3 sentences."
            else:
                fusion_prompt = f"You are a tech recruiter hiring for this job: {context_text}. The candidate is sitting in front of you. Difficulty: {selected_diff}. Ask ONE specific technical question they must know to get this job. Keep it under 3 sentences."
            
            response = st.session_state.chat_session.send_message(fusion_prompt)
            st.session_state.messages = [{"role": "assistant", "content": response.text}]
            my_bar.empty()
            st.rerun() 

# --- THE CHAT INTERFACE ---
if st.session_state.interview_started:
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "assistant":
        play_audio(st.session_state.messages[-1]["content"])

    if prompt := st.chat_input("Type your answer here..."):
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            grading_prompt = f"""
            STRICT RULE: Only evaluate the exact words typed. 
            Student answer: "{prompt}"
            
            Grade out of 10.
            If 7 or below: Tell the score. Be a mentor, explain the right answer. Ask a NEW question at the same difficulty.
            If 8 or above: Tell the score, congratulate them. Mention what would make it a 10. Ask a NEW question.
            """
            
            response = st.session_state.chat_session.send_message(grading_prompt)
            st.markdown(response.text)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun()