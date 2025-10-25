import streamlit as st
import markdown_it as md
from utils.api_keys import update_keys, update_path
from agents.intern_agent import interact
import base64
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="Chatbot UI", layout="centered")
st.title("🎥 CinephileGPT")

# --- SESSION STATE ---
# Keeps message history between reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UPDATE API KEYS ---
AVN_PASSWORD = st.secrets["AVN_PASSWORD"]
QDRANT_API_KEY = st.secrets["QDRANT_API_KEY"]
QDRANT_URL = st.secrets["QDRANT_URL"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

update_keys(AVN_PASSWORD, QDRANT_API_KEY, QDRANT_URL, OPENAI_API_KEY)

# --- CERTIFICATE FOR SQL ---
os.makedirs("certificates", exist_ok=True)
with open("certificates/ca.pem", "wb") as f:
    f.write(base64.b64decode(st.secrets["CA_PEM_B64"]))

# Certificate path
CA_CERT_PATH = "certificates/ca.pem"
update_path(CA_CERT_PATH)


# --- DISPLAY CHAT HISTORY ---

st.markdown("""
<style>
/* Overall background */
body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
    background-color: #0B0C10;
    color: #FFFFFF;
}

/* Title */
h1, h2, h3 {
    color: #FFFFFF;
    font-family: 'Segoe UI', sans-serif;
}

/* User message (right) */
.user-msg {
    text-align: right;
    background-color: #2B2D42;
    color: #FFFFFF;
    padding: 10px 14px;
    border-radius: 12px;
    margin: 8px 0;
    max-width: 80%;
    float: right;
    clear: both;
}

/* AI message (left) */
.ai-msg {
    text-align: left;
    background-color: #8D99AE;
    color: #0B0C10;
    padding: 10px 14px;
    border-radius: 12px;
    margin: 8px 0;
    max-width: 80%;
    float: left;
    clear: both;
}
</style>
""", unsafe_allow_html=True)


for msg in st.session_state.messages:
    # User messages on the right
    if msg["role"] == "user":
        st.markdown(
            f"<div class='user-msg'>{msg['content']}</div>",
            unsafe_allow_html=True
        )
    # AI messages on the left
    else:
        st.markdown(
            f"<div class='ai-msg'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

# --- USER INPUT ---
if prompt := st.chat_input("Type your message..."):
    # Save user input
    st.session_state.messages.append({"role": "user", "content": prompt})

    st.session_state.show_spinner = True
    st.session_state.pending_prompt = prompt
    st.rerun()


# --- RUN AI + SPINNER ---
if st.session_state.get("show_spinner", False):

    with st.spinner("🎬 CinephileGPT is thinking..."):
        ai_reply = interact(st.session_state.pending_prompt)


    st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    st.session_state.show_spinner = False
    st.session_state.pending_prompt = None
    st.rerun()