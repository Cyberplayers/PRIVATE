import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

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
    timestamp = datetime.now().strftime("%H:%M")
    with open(CHAT_FILE, "a") as f:
        f.write(f"[{timestamp}] {user}: {text}\n")

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
    # AUTO-REFRESH: Keeps the chat live every 5 seconds
    st_autorefresh(interval=5000, key="chatupdate")

    st.title(f"Welcome, Agent {st.session_state.current_user}")
    
    # SOS SECTION
    if st.button("🚨 TRIGGER SOS 🚨"):
        save_message("SYSTEM", f"🚨 SOS TRIGGERED BY {st.session_state.current_user} 🚨")
        st.error("EMERGENCY SIGNAL SENT!")

    st.divider()

    # GLOBAL CHAT SECTION
    st.subheader("💬 Global Mission Chat")
    
    # NEW: Auto-Scrolling HTML Chat Box
    chat_data = get_messages()
    chat_html = ""
    for msg in chat_data:
        chat_html += f"<p style='margin:5px; font-family:monospace;'>{msg.strip()}</p>"

    # This CSS creates the scrolling window and forces it to the bottom
    st.markdown(
        f"""
        <div id="chat-container" style="height:300px; overflow-y:auto; border:1px solid #444; padding:10px; border-radius:5px; background-color:#111; color:#0f0;">
            {chat_html}
            <div id="end"></div>
        </div>
        <script>
            var element = document.getElementById("chat-container");
            element.scrollTop = element.scrollHeight;
        </script>
        """,
        unsafe_allow_html=True
    )

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
