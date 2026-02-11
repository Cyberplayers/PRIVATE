import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time as t

# 1. Page Config & Security Shield
st.set_page_config(page_title="Official Friend Portal", layout="centered")

# CSS to block right-clicks and text selection
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

# 4. Screenshot Detection Logic
st.components.v1.html(f"""
    <script>
    document.addEventListener("visibilitychange", function() {{
        if (document.visibilityState === 'hidden') {{
            fetch("/?ss_event=true&user={st.session_state.get('current_user', 'UNKNOWN')}");
        }}
    }});
    </script>
""", height=0)

# Detect Screenshot Trigger
if st.query_params.get("ss_event") == "true":
    violator = st.query_params.get("user", "UNKNOWN")
    if violator != "PANTHER" and violator != "UNKNOWN":
        save_message("SYSTEM", f"🚨 ALERT: {violator} took a screenshot or recorded the chat!", "security")
    st.query_params.clear()

# 5. Session & 90-Second Timeout Management
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
    # Top Row: Status, Logout, and Panic
    st_autorefresh(interval=5000, key="chatupdate")
    update_activity(st.session_state.current_user)
    
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        last_seen = get_last_seen()
        online_agents = [f"🟢 {u}" for u, ts in last_seen.items() if t.time() - ts < 60]
        st.write(f"Active: {', '.join(online_agents)}")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()
    with col3:
        if st.button("🚨 PANIC"):
            st.session_state.authenticated = False
            st.rerun()

    st.title(f"Welcome, Agent {st.session_state.current_user}")
    
    # 7. CHAT DISPLAY
    chat_box = st.container(height=450)
    with chat_box:
        if
