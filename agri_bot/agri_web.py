import streamlit as st
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_title="AgriBot Nepal", page_icon="🌱", layout="centered")
st.title("🌱 AgriBot Nepal Dashboard")
st.markdown("### Interactive AI Solutions Console for Local Enterprise")
st.write("Secure client-facing engine for localized agriculturalconsulting")

user_query = st.text_area("Describe your crop issues,disease sysmptoms, or pricing query here:", height=150)
if st.button("Ask AgriBot"):
    client = Groq()
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "Your name is AgriBot Nepal. Help users with crop cultivation, diseases, and pricing in clear, concise English."},
            {"role": "user", "content": user_query}
        ]
    )
    st.write(f"**AgriBot Response:**\n\n{completion.choices[0].message.content}")
    