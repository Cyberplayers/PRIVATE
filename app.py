import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Official Friend Portal", layout="centered")

# 1. Database of Users
users = {
    "PANTHER": "SOURCER",
    "SCORPION": "MASTERMIND",
    "PRIVATE": "HIDDEN"
}

# 2. Setup Directories & Session State
if not os.path.exists("uploads"):
    os.makedirs("uploads")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""

# 3. Global Chat Functions
CHAT_FILE = "chat_log.txt"

def save_message(user, text, msg_type="text"):
    timestamp = datetime.now().strftime("%H:%M")
    with open(CHAT_FILE, "a") as f:
        # We use a | separator to tell the difference between text and images
        f.write(f"{timestamp}|{user}|{msg_type}|{text}\n")

def get_messages():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            return f.readlines()
    return []

# 4. Login Screen
if not st.session_state.authenticated:
    st.title("🔐 Official Login Portal")
    name = st.text_input("Username").upper()
    word = st.text_input("Password", type="password")
    
    if st.button("Enter Portal"):
        if name in users and users[name] == word:
            st.session_state.authenticated = True
            st.session_state.current_user = name
            st.rerun()
        else:
            st.error("Invalid Credentials")

# 5. The Main Portal (After Login)
else:
    st_autorefresh(interval=5000, key="chatupdate")
    st.title(f"Welcome, Agent {st.session_state.current_user}")
    
    # SOS SECTION
    if st.button("🚨 TRIGGER SOS 🚨"):
        save_message("SYSTEM", f"SOS TRIGGERED BY {st.session_state.current_user}", "text")
        st.error("EMERGENCY SIGNAL SENT!")

    st.divider()

    # GLOBAL CHAT DISPLAY
    st.subheader("💬 Global Mission Chat")
    
    chat_data = get_messages()
    
    # Create a scrollable container for messages
    with st.container():
        for line in chat_data:
            try:
                time, user, mtype, content = line.strip().split("|")
                if mtype == "text":
                    st.markdown(f"**[{time}] {user}:** {content}")
                elif mtype == "image":
                    st.markdown(f"**[{time}] {user} sent a photo:**")
                    st.image(content, width=250)
            except:
                continue

    st.divider()

    # MESSAGE & IMAGE INPUT
    # Text Input
    with st.form("chat_form", clear_on_submit=True):
        text = st.text_input("Type mission report...")
        submitted = st.form_submit_button("Send Text")
        if submitted and text:
            save_message(st.session_state.current_user, text, "text")
            st.rerun()

    # Image Upload
    img_file = st.file_uploader("Upload Intel (Image)", type=['png', 'jpg', 'jpeg'])
    if img_file is not None:
        if st.button("Deploy Image"):
            file_path = os.path.join("uploads", img_file.name)
            with open(file_path, "wb") as f:
                f.write(img_file.getbuffer())
            save_message(st.session_state.current_user, file_path, "image")
            st.success("Image Sent!")
            st.rerun()

    if st.button("Log Out"):
        st.session_state.authenticated = False
        st.rerun()
