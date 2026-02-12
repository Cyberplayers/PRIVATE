import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time as t

# 1. Page Configuration & CSS
st.set_page_config(page_title="Official Friend Portal", layout="centered")

# JavaScript for: Notifications + Vibration + AUTO-SCROLL
def trigger_js_features(sender, message):
    js_code = f"""
    <script>
    if (Notification.permission === "granted") {{
        new Notification("New Intel: {sender}", {{
            body: "{message}",
            vibrate: [200, 100, 200]
        }});
    }}
    // Auto-Scroll Logic: Targets the Streamlit vertical block
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
    [data-testid="stVerticalBlockBorderWrapper"] { overflow-y: auto !important; scroll-behavior: smooth; }
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

# 3. Auth Initialization (Prevents "Blackout" AttributeError)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "last_seen_id" not in st.session_state:
    st.session_state.last_seen_id = None

# 4. Login Screen
if not st.session_state.authenticated:
    st.title("🔐 Login")
    u_in = st.text_input("User").upper()
    p_in = st.text_input("Pass", type="password")
    if st.button("Enter"):
        if u_in in users and users[u_in] == p_in:
            st.session_state.authenticated = True
            st.session_state.current_user = u_in
            st.rerun()
else:
    # 5. Refresh & Automation Engine (Pings every 3s to keep Cron-job alive
