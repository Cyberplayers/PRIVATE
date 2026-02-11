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
    .notif-msg { color: #000000; font-weight: bold; border: 1px solid #00ff41; padding: 8px; border-radius: 5px; background: #00ff41; text-align: center; margin-bottom: 10px; }
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
                    p = line.strip().split("|")
                    seen_dict[p[0]] = float(p[1])
                except:
                    continue
    return seen_dict

# 4. Automated Security Notifications (SS Detection)
st.components.v1.html(f"""
    <script>
    document.addEventListener("visibilitychange", function() {{
        if (document.visibilityState === 'hidden') {{
            fetch("/?ss_event=true&user={st.session_state.get('current_user', 'UNKNOWN')}");
        }}
    }});
    </script>
""", height=0)

if st.query_params.get("ss_event") == "true":
    violator = st.query_params.get("user", "UNKNOWN")
    if violator != "PANTHER" and violator != "UNKNOWN":
        save_message("SYSTEM", f"🚨 ALERT: {violator} captured the screen/media!", "security")
    st.query_params.clear()

# 5. Session & 90-Second Timeout
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if st.session_state.authenticated:
    current_time = t.time()
    if "last_action_time" in st.session_state:
        elapsed = current_time - st.session_state.last_action_time
        if elapsed > 90:
            st.session_state.authenticated = False
            st.rerun()
    st.session_state.last_action_time = current_time

# 6. Auth Logic
if not st.session_state.authenticated:
    st.title("🔐 Official Login Portal")
    name = st.text_input("Username").upper()
    word = st.text_input("Password", type="password")
    if st.button("Enter Portal"):
        if name in users and users[name] == word:
            st.session_state.authenticated, st.session_state.current_user = True, name
            st.session_state.last_action_time = t.time()
            st.rerun()
        else:
            st.error("Invalid Credentials")
else:
    # 7. Navigation Row
    st_autorefresh(interval=5000, key="chatupdate")
    update_activity(st.session_state.current_user)
