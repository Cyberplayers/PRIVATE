import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time as t

# 1. Page Config & JavaScript for Notifications + AUTO-SCROLL
st.set_page_config(page_title="Official Friend Portal", layout="centered")

def trigger_features(sender, message):
    # This script triggers the vibration AND forces the window to the bottom
    js_code = f"""
    <script>
    // 1. Notification & Vibration
    if (Notification.permission === "granted") {{
        new Notification("New Intel: {sender}", {{
            body: "{message}",
            vibrate: [200, 100, 200]
        }});
    }}
    
    // 2. Auto-Scroll Logic: Finds the chat container and snaps to bottom
    var chatWindow = window.parent.document.querySelector('div[data-testid="stVerticalBlockBorderWrapper"]');
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
    /* Ensure the chat container allows scrolling */
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
            st.session_state.current_user = u_in
            st.components.v1.html("<script>Notification.requestPermission();</script>", height=0)
            st.rerun()
else:
    # 4. Refresh & Smart Notification/Scroll Engine
    st_autorefresh(interval=3000, key="refresh") 

    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            lines = f.readlines()
            if lines:
                last_data = lines[-1].strip().split("|")
                last_id = last_data[0]
                
                if "last_seen_id" not in st.session_state:
                    st.session_state.last_seen_id = last_id
                
                # TRIGGER: If a new message exists, notify and scroll
                if last_id != st.session_state.last_seen_id:
                    sender = last_data[2]
                    msg_content = last_data[4]
                    if sender != st.session_state.current_user:
                        trigger_features(sender, msg_content)
                    else:
                        # Even if it's your message, trigger the scroll
                        st.components.v1.html("<script>window.parent.document.querySelector('div[data-testid=\"stVerticalBlockBorderWrapper\"]').scrollTop = 1000000;</script>", height=0)
                    st.session_state.last_seen_id = last_id

    # 5. Dashboard
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    st.title(f"Portal: {st.session_state.current_user}")
    
    # 6. Chat Container (Target for Auto-Scroll)
    chat_box = st.container(height=400)
    with chat_box:
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, "r") as f:
                for line in f.readlines():
                    try:
                        uid, ts, user, mtype, msg = line.strip().split("|")
                        if mtype == "security":
                            if st.session_state.current_user == "PANTHER":
                                st.markdown(f"<div class='security-msg'>[{ts}] {msg}</div>", unsafe_allow_html=True)
                        elif mtype == "notif":
                            st.markdown(f"<div class='notif-msg'>[{ts}] {msg}</div>", unsafe_allow_html=True)
                        else:
                            st.write(f"**[{ts}] {user}:** {msg}")
                            if mtype == "image": st.image(msg, width=250)
                            if mtype == "audio": st.audio(msg)
                    except: continue

    # 7. Tools
    t1, t2, t3 = st.tabs(["💬 Chat", "📸 Media", "🎤 Voice"])
    with t1:
        with st.form("msg", clear_on_submit=True):
            txt = st.text_input("Message")
            if st.form_submit_button("Send"):
                save_message(st.session_state.current_user, txt, "text")
                st.rerun()
    with t2:
        cam = st.camera_input("Camera")
        if cam:
            path = os.path.join("uploads", cam.name)
            with open(path, "wb") as f: f.write(cam.getbuffer())
            save_message(st.session_state.current_user, path, "image")
            st.rerun()
    with t3:
        aud = st.audio_input("Record")
        if aud:
            path = os.path.join("uploads", f"v_{int(t.time())}.wav")
            with open(path, "wb") as f: f.write(aud.getbuffer())
            save_message(st.session_state.current_user, path, "audio")
            st.rerun()

    if st.button("🧨 SELF-DESTRUCT"):
        if os.path.exists(CHAT_FILE): os.remove(CHAT_FILE)
        st.rerun()
