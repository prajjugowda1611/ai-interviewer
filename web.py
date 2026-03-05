import streamlit as st
import PyPDF2
import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Page Setup
st.set_page_config(page_title="AI Interviewer Pro", page_icon="🤖", layout="wide")
st.title("🤖 AI Mock Interviewer")
st.write("---")

# 2. Give the Web App a "Memory"
if "messages" not in st.session_state:
    st.session_state.messages = [] # Remembers the chat UI
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None # Remembers the AI's brain
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "MEDIUM" # Remembers the difficulty

# 3. The Sidebar
with st.sidebar:
    st.header("⚙️ Interview Settings")
    uploaded_file = st.file_uploader("Drop your Resume here (PDF)", type=["pdf"])
    
    selected_diff = st.selectbox(
        "Select Difficulty Level",
        ["1. Easy (Friendly)", "2. Medium (Professional)", "3. Hard (Strict)", "4. Brutal (No Empathy)"],
        index=1
    )
    
    start_btn = st.button("Start Interview", use_container_width=True)

# 4. Booting up the Engine (Only runs when you click Start)
if start_btn:
    if uploaded_file is not None:
        with st.spinner("Scanning resume and preparing the interview..."):
            
            # Read PDF
            reader = PyPDF2.PdfReader(uploaded_file)
            resume_text = ""
            for page in reader.pages:
                resume_text += page.extract_text() + "\n"
            
            # Setup AI
            load_dotenv()
            genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Start Chat and save it to memory
            st.session_state.chat_session = model.start_chat(history=[])
            st.session_state.difficulty = selected_diff
            
            fusion_prompt = f"""
            You are an interviewer at a top tech company.
            The candidate sitting in front of you is a 3rd-year BE student. Here is their resume:
            {resume_text}
            
            Task: 
            1. Find one specific project or technical skill listed on this resume.
            2. The difficulty of this interview must be: {selected_diff}
            3. Ask ONE single question based on that skill and difficulty.
            4. Keep the question under 3 sentences. Do not provide the answer.
            """
            
            # Get first question and save to message history
            response = st.session_state.chat_session.send_message(fusion_prompt)
            st.session_state.messages = [{"role": "assistant", "content": response.text}]
            
    else:
        st.error("⚠️ Please upload a PDF resume first!")

# 5. Display the Chat History on the Screen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. The Chat Input Box (Where you type your answers!)
if prompt := st.chat_input("Type your answer here..."):
    
    # Show user message on screen
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Generate AI Feedback
    with st.chat_message("assistant"):
        grading_prompt = f"""
        STRICT RULE: Only evaluate the exact words the user typed. Do not assume or invent concepts they did not explicitly write. If they type gibberish, give them a 0/10.
        
        The student just provided this exact answer: "{prompt}"
        
        First, grade the answer out of 10.
        
        If the score is 7 or below:
        1. Tell them the score.
        2. Act as a supportive mentor and explain the correct answer.
        3. Then, ask a COMPLETELY NEW QUESTION at the same difficulty level.
        
        If the score is 8 or above:
        1. Tell them the score and congratulate them.
        2. Tell them what detail would have made it a perfect 10.
        3. Then, ask a COMPLETELY NEW QUESTION at the same difficulty level.
        """
        
        response = st.session_state.chat_session.send_message(grading_prompt)
        st.markdown(response.text)
        
        # Save AI response to memory
        st.session_state.messages.append({"role": "assistant", "content": response.text})