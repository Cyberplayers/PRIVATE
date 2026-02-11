import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time as t

# 1. Page Config
st.set_page_config(page_title="Official Friend Portal", layout="centered")
from st_custom_components import st_audiorecorder # Updated for stability

# 2. Database & Setup
users = {"PANTHER": "SOURCER", "SCORPION": "MASTERMIND", "PRIVATE": "HIDDEN"}
if not os.path.exists("uploads"):
    os.makedirs("uploads")

CHAT_FILE = "chat_log.txt"
STATUS_FILE = "user_activity.txt"

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

# 3. Auth Logic
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Official Login Portal")
    name = st.text_input("Username").upper()
    word = st.text_input("Password", type="password")
    if st.button("Enter Portal"):
        if name in users and users[name] == word:
            st.session_state.authenticated, st.session_state.current_user = True, name
            st.rerun()
        else:
            st.error("Invalid Credentials")
else:
    # AUTO-SYNC
    st_autorefresh(interval=5000, key="chatupdate")
    update_activity(st.session_state.current_user)
    last_seen = get_last_seen()

    st.title(f"Welcome, Agent {st.session_state.current_user}")
    
    # CHAT FEED
    chat_box = st.container(height=450)
    with chat_box:
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, "r") as f:
                for line in f.readlines():
                    try:
                        unix, clock, sender, mtype, content = line.strip().split("|")
                        status = "✓"
                        for u, ts in last_seen.items():
                            if u != sender and ts > float(unix): status = "✓✓"
                        
                        if mtype == "text": st.write(f"**[{clock}] {sender}:** {content} `{status}`")
                        elif mtype == "image": 
                            st.write(f"**[{clock}] {sender} sent intel:**")
                            st.image(content)
                            st.caption(f"Status: {status}")
                        elif mtype == "audio":
                            st.write(f"**[{clock}] {sender} sent voice:**")
                            st.audio(content)
                            st.caption(f"Status: {status}")
                    except: continue

    st.divider()

    # INPUT TABS
    t1, t2, t3 = st.tabs(["💬 Text", "🖼️ Image", "🎤 Voice"])
    with t1:
        with st.form("txt", clear_on_submit=True):
            m = st.text_input("Message")
            if st.form_submit_button("Send"):
                save_message(st.session_state.current_user, m, "text")
                st.rerun()
    with t2:
        img = st.file_uploader("Upload", type=['png','jpg','jpeg'])
        if img and st.button("Upload Intel"):
            p = os.path.join("uploads", img.name)
            with open(p, "wb") as f: f.write(img.getbuffer())
            save_message(st.session_state.current_user, p, "image")
            st.rerun()
    with t3:
        st.write("Record Voice Note")
        audio = st_audiorecorder()
        if audio and st.button("Send Voice"):
            ap = os.path.join("uploads", f"v_{int(t.time())}.wav")
            with open(ap, "wb") as f: f.write(audio)
            save_message(st.session_state.current_user, ap, "audio")
            st.rerun()

    if st.button("🧨 SELF-DESTRUCT"):
        if os.path.exists(CHAT_FILE): os.remove(CHAT_FILE)
        for f in os.listdir("uploads"): os.remove(os.path.join("uploads", f))
        st.rerun()
