import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time as t

# 1. Page Config
st.set_page_config(page_title="Official Friend Portal", layout="centered")

# JS for Scroll + Vibrate
def trigger_js(sender, message):
    js = f"""
    <script>
    if (Notification.permission === "granted") {{
        new Notification("New Intel: {sender}", {{ body: "{message}", vibrate: [200, 100, 200] }});
    }}
    var chatWindow = window.parent.document.querySelector('div[data-testid="stVerticalBlockBorderWrapper"]');
    if (chatWindow) {{ chatWindow.scrollTop = chatWindow.scrollHeight; }}
    </script>
    """
    st.components.v1.html(js, height=0)

st.markdown("<style>.stApp { background-color: #0e1117; color: #00ff41; } [data-testid='stVerticalBlockBorderWrapper'] { overflow-y: auto !important; }</style>", unsafe_allow_html=True)

# 2. Setup
users = {"PANTHER": "SOURCER", "SCORPION": "MASTERMIND", "PRIVATE": "HIDDEN"}
if not os.path.exists("uploads"): os.makedirs("uploads")
CHAT_FILE = "chat_log.txt"

def save_message(user, content, msg_type="text"):
    ts = datetime.now().strftime("%H:%M")
    uid = str(t.time())
    with open(CHAT_FILE, "a") as f:
        f.write(f"{uid}|{ts}|{user}|{msg_type}|{content}\n")

# 3. Session Initialization (Fixes Black Screen)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "last_seen_id" not in st.session_state:
    st.session_state.last_seen_id = None

# 4. Login
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
    # 5. Refresh & Auto-Scroll
    st_autorefresh(interval=3000, key="refresh") 
    
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            lines = f.readlines()
            if lines:
                last_data = lines[-1].strip().split("|")
                if last_data[0] != st.session_state.last_seen_id:
                    if last_data[2] != st.session_state.current_user:
                        trigger_js(last_data[2], last_data[4])
                    st.session_state.last_seen_id = last_data[0]
                # Keep scroll at bottom
                st.components.v1.html("<script>window.parent.document.querySelector('div[data-testid=\"stVerticalBlockBorderWrapper\"]').scrollTop = 1000000;</script>", height=0)

    st.title(f"Portal: {st.session_state.current_user}")
    chat_box = st.container(height=450, border=True)
    with chat_box:
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, "r") as f:
                for line in f.readlines():
                    try:
                        _, ts, user, mtype, msg = line.strip().split("|")
                        st.write(f"**[{ts}] {user}:** {msg}")
                    except: continue

    # 6. Tools
    with st.form("msg", clear_on_submit=True):
        txt = st.text_input("Message")
        if st.form_submit_button("Send"):
            save_message(st.session_state.current_user, txt, "text")
            st.rerun()

    # 7. Self Destruct (Fixed Indentation)
    if st.button("🧨 SELF-DESTRUCT"):
        if os.path.exists(CHAT_FILE):
            os.remove(CHAT_FILE)
        st.rerun()
