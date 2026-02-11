import streamlit as st
import os

st.set_page_config(page_title="Official Friend Portal", layout="centered")

# 1. Database of Users
users = {
    "PANTHER": "SOURCER",
    "SCORPION": "MASTERMIND",
    "PRIVATE": "HIDDEN"
}

# 2. Setup Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""

# 3. Global Chat Functions
CHAT_FILE = "chat_log.txt"

def save_message(user, text):
    with open(CHAT_FILE, "a") as f:
        f.write(f"{user}: {text}\n")

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
    st.title(f"Welcome, Agent {st.session_state.current_user}")
    
    # SOS SECTION
    if st.button("🚨 TRIGGER SOS 🚨"):
        st.error("EMERGENCY SIGNAL SENT TO ALL AGENTS!")
        save_message("SYSTEM", f"🚨 SOS TRIGGERED BY {st.session_state.current_user} 🚨")

    st.divider()

    # GLOBAL CHAT SECTION
    st.subheader("💬 Global Mission Chat")
    
    # Container for messages
    chat_data = get_messages()
    for msg in chat_data[-15:]: # Shows last 15 messages
        st.text(msg.strip())

    # Message Input
    with st.form("chat_form", clear_on_submit=True):
        text = st.text_input("Type mission report...")
        submitted = st.form_submit_button("Send to Team")
        if submitted and text:
            save_message(st.session_state.current_user, text)
            st.rerun()

    if st.button("Log Out"):
        st.session_state.authenticated = False
        st.rerun()
        
