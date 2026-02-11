import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time as t

# 1. Page Config & Security Shield
st.set_page_config(page_title="Official Friend Portal", layout="centered")

st.markdown("""
    <style>
    * { -webkit-user-select: none; user-select: none; }
    img { pointer-events: none; }
    .stApp { background-color: #0e1117; color: #00ff41; }
    .security-msg { color: #ffffff; font-weight: bold; border: 2px solid #ff4b4b; padding: 10px; border-radius: 5px; background: #ff4b4b; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. Database & User Setup
users = {"PANTHER": "SOURCER", "SCORPION": "MASTERMIND", "PRIVATE": "HIDDEN"}
if not os.path.exists("uploads"):
    os.makedirs("uploads")

CHAT_FILE = "chat_log.txt"
STATUS_FILE = "user_activity.txt"

# 3. Helper Functions
def save_message(user, content, msg_type="text"):
    timestamp = datetime.now().strftime("%H:%M")
    unix_time = t.time()
    with open(CHAT_FILE, "a") as f:
        f.write(f"{unix_time}|{timestamp}|{user}|{msg_type}|{content}\n")

def update_activity(user):
    with open(STATUS_FILE, "a") as f:
        f.write(f"{user}|{t.time()}\n")

def get_last_seen():
    seen_dict = {}
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            for line in f.readlines():
                try:
                    u, ts = line.strip().split("|")
                    seen_dict[u] = float(ts)
                except: continue
    return seen_dict

# 4. Screenshot Detection & Auto-Logout Logic
st.components.v1.html(f"""
    <script>
    document.addEventListener("visibilitychange", function() {{
        if (document.visibilityState === 'hidden') {{
            fetch("/?ss_event=true&user={st.session_state.get('current_user', 'UNKNOWN')}");
        }}
    }});
    </script>
""", height=0)

# Detect Screenshot
if st.query_params.get("ss_event") == "true":
    violator = st.query_params.get("user", "UNKNOWN")
    if violator != "PANTHER" and violator != "UNKNOWN":
        save_message("SYSTEM
