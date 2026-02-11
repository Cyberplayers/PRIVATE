import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time as t

# 1. Page Config & CSS
st.set_page_config(page_title="Official Friend Portal", layout="centered")

st.markdown("""
    <style>
    * { -webkit-user-select: none; user-select: none; }
    .stApp { background-color: #0e1117; color: #00ff41; }
    .security-msg { color: #ffffff; font-weight: bold; border: 2px solid #ff4b4b; padding: 10px; border-radius: 5px; background: #ff4b4b; text-align: center; margin-bottom: 10px; }
    .notif-msg { color: #000000; font-weight: bold; border: 1px solid #00ff41; padding: 8px; border-radius: 5px; background: #00ff41; text-align: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Setup
users = {"PANTHER": "SOURCER", "SCORPION": "MASTERMIND", "PRIVATE": "HIDDEN"}
if not os.path.exists("uploads"): os.makedirs("uploads")
CHAT_FILE = "chat_log.txt"
STATUS_FILE = "user_activity.txt"

# 3. Helper Functions
def save_message(user, content, msg_type="text"):
    timestamp = datetime.now().strftime("%H:%M")
    unix_time = t.time()
    with open(CHAT_FILE, "a") as f:
        f.write(f"{unix_time}|{timestamp}|{user}|{msg_type}|{content}\n")

def get_last_seen():
    seen_dict = {}
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            for line in f.readlines():
                try:
                    p = line.strip().split("|")
                    seen_dict[p[0]] = float(p[1])
                except: continue
    return seen_dict

# 4. Auth
if "authenticated" not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Official Login Portal")
    name = st.text_input("Username").upper()
    word = st.text_input("Password", type="password")
    if st.button("Enter Portal"):
        if name in users and users[name] == word:
            st.session_state.authenticated, st.session_state.current_user = True, name
            st.rerun()
else:
    # 5. The Notification Engine
    st_autorefresh(interval=3000, key="notif_check") # Check every 3 seconds
    
    # Logic to detect NEW messages for the Pop-up
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip().split("|")
                last_msg_id = last_line[0] # Use unix time as ID
                
                if "seen_msg_id" not in st.session_state:
                    st.session_state.seen_msg_id = last_msg_id
                
                # If a new message appeared that isn't ours, POP UP!
                if last_msg_id != st.session_state.seen_msg_id:
                    sender = last_line[2]
                    if sender != st.session_state.current_user:
                        st.toast(f"💬 New message from {sender}!", icon="🔔")
                    st.session_state.seen_msg_id = last_msg_id

    # 6. Navigation Row
    col1, col2 = st.columns([3,1])
    with col1:
        last_seen = get_last_seen()
        online = [f"🟢 {u}" for u, ts in last_seen.items() if t.time() - ts < 60]
        st.write(f"Active: {', '.join(online)}")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

    st.title(f"Welcome, Agent {st.session_state.current_user}")
    
    # 7. Chat Display
    chat_box = st.container(height=400)
    with chat_box:
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, "r") as f:
                for line in f.readlines():
                    try:
                        p = line.strip().split("|")
                        unix, clock, sender, mtype, content = p[0], p[1], p[2], p[3], p[4]
                        if mtype == "security":
                            if st.session_state.current_user == "PANTHER":
                                st.markdown(f"<div class='security-msg'>[{clock}] {content}</div>", unsafe_allow_html=True)
                        elif mtype == "notif":
                            st.markdown(f"<div class='notif-msg'>[{clock}] {content}</div>", unsafe_allow_html=True)
                        else:
                            st.write(f"**[{clock}] {sender}:** {content}")
                            if mtype == "image": st.image(content, width=250)
                            if mtype == "audio": st.audio(content)
                    except: continue

    # 8. Input Tabs
    t1, t2, t3, t4 = st.tabs(["💬 Text", "📸 Camera", "📁 Media", "🎤 Voice"])
    with t1:
        with st.form("txt", clear_on_submit=True):
            m = st.text_input("Message")
            if st.form_submit_button("Send"):
                save_message(st.session_state.current_user, m, "text")
                st.rerun()
    with t2:
        img = st.camera_input("Take Photo")
        if img:
            p = os.path.join("uploads", img.name)
            with open(p, "wb") as f: f.write(img.getbuffer())
            save_message(st.session_state.current_user, p, "image")
            save_message("SYSTEM", f"📸 Camera capture by {st.session_state.current_user}", "notif")
            st.rerun()
    with t3:
        media = st.file_uploader("Upload", type=['png','jpg','jpeg'])
        if media and st.button("Submit"):
            mp = os.path.join("uploads", media.name)
            with open(mp, "wb") as f: f.write(media.getbuffer())
            save_message(st.session_state.current_user, mp, "image")
            save_message("SYSTEM", f"📁 Intel uploaded by {st.session_state.current_user}", "notif")
            st.rerun()
    with t4:
        v = st.audio_input("Record")
        if v:
            ap = os.path.join("uploads", f"v_{int(t.time())}.wav")
            with open(ap, "wb") as f: f.write(v.getbuffer())
            save_message(st.session_state.current_user, ap, "audio")
            save_message("SYSTEM", f"🎤 Audio recorded by {st.session_state.current_user}", "notif")
            st.rerun()

    if st.button("🧨 SELF-DESTRUCT"):
        if os.path.exists(CHAT_FILE): os.remove(CHAT_FILE)
        st.rerun()
