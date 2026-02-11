import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time as t

# 1. Page Config & CSS
st.set_page_config(page_title="Official Friend Portal", layout="centered")

# JavaScript for: Notifications + Vibration + AUTO-SCROLL
def trigger_js_features(sender, message):
    js_code = f"""
    <script>
    // 1. Notification Logic
    if (Notification.permission === "granted") {{
        new Notification("New Intel: {sender}", {{
            body: "{message}",
            vibrate: [200, 100, 200]
        }});
    }}
    
    // 2. Auto-Scroll Logic
    var chatWindow = window.parent.document.querySelector('.stElementContainer div[data-testid="stVerticalBlockBorderWrapper"]');
    if (chatWindow) {{
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }}
    </script>
    """
    st.components.v1.html(js_code, height=0)

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    .security-msg { color: #ffffff; font-weight: bold; border: 2px solid #ff4b4b; padding: 10px; border-radius: 5px; background: #ff4b4b; text-align: center; margin-bottom: 10px; }
    .notif-msg { color: #000000; font-weight: bold; border: 1px solid #00ff41; padding: 8px; border-radius: 5px; background: #00ff41; text-align: center; margin-bottom: 10px; }
    /* Style to make chat container look cleaner */
    [data-testid="stVerticalBlockBorderWrapper"] { overflow-y: auto !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Database Setup
users = {"PANTHER": "SOURCER", "SCORPION": "MASTERMIND", "PRIVATE": "HIDDEN"}
if not os.path.exists("uploads"): os.makedirs("uploads")
CHAT_FILE = "chat_log.txt"

def save_message(user, content, msg_type="text"):
    ts = datetime.now().strftime("%H:%M")
    uid = str(t.time())
    with open(CHAT_FILE, "a") as f:
        f.write(f"{uid}|{ts}|{user}|{msg_type}|{content}\n")

# 3. Auth Initialization (Prevents AttributeError)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login")
    u_in = st.text_input("User").upper()
    p_in = st.text_input("Pass", type="password")
    if st.button("Enter"):
        if u_in in users and users[u_in] == p_in:
            st.session_state.authenticated = True
            st.session_state.current_user = u_in
            st.components.v1.html("<script>Notification.requestPermission();</script>", height=0)
            st.rerun()
else:
    # 4. Refresh & Notification/Scroll Engine
    st_autorefresh(interval=3000, key="refresh") 

    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            lines = f.readlines()
            if lines:
                last_data = lines[-1].strip().split("|")
                last_id = last_data[0]
                
                if "last_seen_id" not in st.session_state:
                    st.session_state.last_seen_id = last_id
                
                # Trigger JS if new data arrives
                if last_id != st.session_state.last_seen_id:
                    sender, msg_content = last_data[2], last_data[4]
                    if sender != st.session_state.current_user:
                        trigger_js_features(sender, msg_content)
                    st.session_state.last_seen_id = last_id
                else:
                    # Keep scrolling to bottom even if no new message
                    st.components.v1.html("<script>window.parent.document.querySelectorAll('div[data-testid=\"stVerticalBlockBorderWrapper\"]')[0].scrollTo(0, 1000000);</script>", height=0)

    # 5. UI Layout
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    st.title(f"Portal: {st.session_state.current_user}")
    
    # 6. Chat Container
    chat_box = st.container(height=400, border=True)
    with chat_box:
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, "r") as f:
                for line in f.readlines():
                    try:
                        uid, ts, user, mtype, msg = line.strip().split("|")
                        if mtype == "security":
                            if st.session_state.current_user == "PANTHER":
