import streamlit as st
from groq import Groq
from gtts import gTTS
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AgriBot Nepal Pro", layout="wide", page_icon="🌱")

st.markdown("""
<style>
.main {background-color: #f0fff4;}
.stButton>button {background-color: #22c55e; color: white; border-radius: 12px; font-size: 16px; height: 60px;}
.card {background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);}
    h1 {color: #166534;}
</style>
""", unsafe_allow_html=True)

st.title("🌱 AgriBot Nepal Pro")
st.caption("AI Krishi Salahakar - Nepali + Pure English Voice")

if 'response' not in st.session_state:
    st.session_state.response = ""
if 'english_response' not in st.session_state:
    st.session_state.english_response = ""

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📸 Step 1: Upload Photo")
    uploaded_file = st.file_uploader("Upload Crop Photo", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Your Crop", width=300)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💬 Step 2: Ask Question")
    user_query = st.text_area("Ask in Nepali or English:", placeholder="e.g. Mero dhan ko paat pahenlo bhayo", height=150)
    st.markdown('</div>', unsafe_allow_html=True)

if st.button("🔊 Ask AgriBot Pro Now", use_container_width=True):
    if user_query:
        with st.spinner("AgriBot sochdai cha..."):
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            # 1. Get main mixed answer
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "You are AgriBot Nepal Pro. Answer in simple Nepali + English mix. Give 3 steps: 1. Problem, 2. Solution, 3. Medicine name in Nepal. Keep it short."},
                    {"role": "user", "content": user_query}
                ]
            )
            st.session_state.response = completion.choices[0].message.content
            
            # 2. Get pure English version for UK voice
            english_prompt = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "You are AgriBot Nepal Pro. Reply in ONLY clear standard English. No Nepali words at all."},
                    {"role": "user", "content": user_query}
                ]
            )
            st.session_state.english_response = english_prompt.choices[0].message.content

if st.session_state.response:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.success("✅ AgriBot Ready!")
    st.info(st.session_state.response)
    st.download_button("📥 Download Answer", st.session_state.response, file_name="AgriBot_Advice.txt")
    
    st.markdown("### **Step 3: Choose Voice**")
    colv1, colv2 = st.columns(2) # ONLY 2 BUTTONS
    
    with colv1:
        if st.button("🇳🇵 Nepali Dai/Didi Voice", use_container_width=True):
            tts_ne = gTTS(text=st.session_state.response, lang='ne')
            tts_ne.save("response_ne.mp3")
            st.audio("response_ne.mp3")
    
    with colv2:
        if st.button("🇬🇧 Pure UK English Voice", use_container_width=True):
            tts_uk = gTTS(text=st.session_state.english_response, lang='en', tld='co.uk') # co.uk = British accent
            tts_uk.save("response_uk.mp3")
            st.audio("response_uk.mp3")
    
    st.markdown('</div>', unsafe_allow_html=True)