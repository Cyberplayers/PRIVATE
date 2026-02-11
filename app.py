import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time as t

# 1. Page Config & CSS
st.set_page_config(page_title="Official Friend Portal", layout="centered")

# JavaScript for Chrome/Android/Tablet Notifications
def trigger_alert(sender, message):
    js = f"""
    <script>
    if (Notification.permission === "granted") {{
        new Notification("New Intel: {sender}", {{
            body: "{message}",
            vibrate: [200, 100, 200]
        }});
    }}
    </script>
    """
    st.components.v1.html(js, height=0)

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    .security-msg { color: #ffffff; font-weight: bold; border: 2px solid #ff4b4b; padding: 10px; border-radius: 5px; background: #ff4b4b; text-align: center; margin-bottom: 10px; }
    .notif-msg { color: #000000; font-weight: bold; border: 1px solid #00ff41; padding: 8px; border-radius: 5px; background: #00ff41; text-align: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Database & Folder Initialization
users = {"PANTHER": "SOURCER", "SCORPION": "MASTERMIND", "PRIVATE": "HIDDEN"}
if not os.path.exists("uploads"): os.makedirs("uploads")
CHAT_FILE = "chat_log.txt"

def save_message(user, content, msg_type="text"):
    ts = datetime.now().strftime("%H:%M")
    uid = str(t.time())
    with open(CHAT_FILE, "a") as f:
        f.write(f"{uid}|{ts}|{user}|{msg_type}|{content}\n")

# 3. CRITICAL: Initialize session_state to fix AttributeErrors
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = "GUEST"
if "last_notified_id" not in st.session_state:
    st.session_state.last_notified_id = None

# 4. Auth Logic
if not st.session_state.authenticated:
    st.title("🔐 Agent Login")
    u_in = st.text_input("User").upper()
    p_in = st.text_input("Key", type="password")
    if st.button("Enter Portal"):
        if u_in in users and users[u_in] == p_in:
            st.session_state.authenticated = True
            st.session_state.current_user = u_in
            # This triggers the prompt on phone/PC to Allow Notifications
            st.components.v1.html("<script>Notification.requestPermission();</script>", height=0)
            st.rerun()
        else:
            st.error("Access Denied")
else:
    # 5. Multi-Device Notification Engine
    st_autorefresh(interval=3000, key="portal_sync") 

    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip().split("|")
                last_id = last_line[0]
                
                if st.session_state.last_notified_id is None:
                    st.session_state.last_notified_id = last_id
                
                if last_id != st.session_state.last_notified_id:
                    sender, msg_txt = last_line[2], last_line
