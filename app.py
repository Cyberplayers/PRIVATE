import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time as t

# 1. Page Config & JavaScript for Chrome Notifications
st.set_page_config(page_title="Official Friend Portal", layout="centered")

# This script asks for Chrome permission and triggers the System Pop-up
def trigger_chrome_notification(sender, message):
    js_code = f"""
    <script>
    if (Notification.permission === "granted") {{
        new Notification("New Message from {sender}", {{
            body: "{message}",
            icon: "https://streamlit.io/images/brand/streamlit-mark-color.png"
        }});
    }} else if (Notification.permission !== "denied") {{
        Notification.requestPermission();
    }}
    </script>
    """
    st.components.v1.html(js_code, height=0)

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    .security-msg { color: #ffffff; font-weight: bold; border: 2px solid #ff4b4b; padding: 10px; border-radius: 5px; background: #ff4b4b; text-align: center; margin-bottom: 10px; }
    .notif-msg { color: #000000; font-weight: bold; border: 1px solid #00ff41; padding: 8px; border-radius: 5px; background: #00ff41; text-align: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Setup
users = {"PANTHER": "SOURCER", "SCORPION": "MASTERMIND", "PRIVATE": "HIDDEN"}
if not os.path.exists("uploads"): os.makedirs("uploads")
CHAT_FILE = "chat_log.txt"

def save_message(user, content, msg_type="text"):
    ts = datetime.now().strftime("%H:%M")
    uid = str(t.time())
    with open(CHAT_FILE, "a") as f:
        f.write(f"{uid}|{ts}|{user}|{msg_type}|{content}\n")

# 3. Auth Logic
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login")
    u_in = st.text_input("User").upper()
    p_in = st.text_input("Pass", type="password")
    if st.button("Enter"):
        if u_in in users and users[u_in] == p_in:
            st.session_state.authenticated = True
            st.session_state.current_
