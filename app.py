import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time as t

# 1. Page Config & Imports
st.set_page_config(page_title="Official Friend Portal", layout="centered")
from st_audio_recorder import st_audio_recorder

# 2. Database of Users
users = {"PANTHER": "SOURCER", "SCORPION": "MASTERMIND", "PRIVATE": "HIDDEN"}

# 3. Setup Folders & Files
if not os.path.exists("uploads"):
    os.makedirs("uploads")

CHAT_FILE = "chat_log.txt"
STATUS_FILE = "user_activity.txt"

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

def save_message(user, content, msg_type="text"):
    timestamp = datetime.now().strftime("%H:%M")
    unix_time = t.time()
    with open(CHAT_FILE, "a") as f:
        f.write(f"{unix_time}|{timestamp}|{user}|{msg_type}|{content}\n")

def get_messages():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            return f.readlines()
    return []

# 4. Authentication Logic
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
    # AUTO-SYNC: Updates every 5 seconds and marks user as active
    st_autorefresh(interval=5000, key="chatupdate")
    update_activity(st.session_state.current_user)
    last_seen = get_last_seen()

    st.title(f"Welcome, Agent {st.session_state.current_user}")
    
    # CHAT FEED with AUTO-SCROLL
    st.subheader("💬 Global Mission Chat")
    chat_data = get_messages()
    
    # Use a fixed-height container for auto-scrolling
    chat_box = st.container(height=450)
    with chat_box:
        for line in chat_data:
            try:
                unix, clock, sender, mtype, content = line.strip().split("|")
                
                # Check for "Seen" status (✓✓)
                status = "✓" 
                for u_name, u_time in last_seen.items():
                    if u_name != sender and u_time > float(unix):
                        status = "✓✓"
                
                if mtype == "text":
                    st.markdown(f"**[{clock}] {sender}:** {content} `{status}`")
                elif mtype == "image":
                    st.markdown(f"**[{clock}] {sender} sent intel:**")
                    st.image(content)
                    st.caption(f"Status: {status}")
                elif mtype == "audio":
                    st.markdown(f"**[{clock}] {sender} sent voice note:**")
                    st.audio(content)
                    st.caption(f"Status: {status}")
            except: continue

    st.divider()

    # MULTIMEDIA TABS
    t1, t2, t3 = st.tabs(["💬 Text", "🖼️ Image", "🎤 Voice"])
    
    with t1:
        with st.form("txt_form", clear_on_submit=True):
            m = st.text_input("Message...")
            if st.form_submit_button("Send") and m:
                save_message(st.session_state.current_user, m, "text")
                st.rerun()

    with t2:
        img = st.file_uploader("Upload Intel", type=['png','jpg','jpeg'])
        if img and st.button("Deploy Image"):
            p = os.path.join("uploads", img.name)
            with open(p, "wb") as f: f.write(img.getbuffer())
            save_message(st.session_state.current_user, p, "image")
            st.rerun()

    with t3:
        st.write("Record Voice Note")
        aud = st_audio_recorder()
        if aud and st.button("Send Recording"):
            ap = os.path.join("uploads", f"v_{int(t.time())}.wav")
            with open(ap, "wb") as f: f.write(aud)
            save_message(st.session_state.current_user, ap, "audio")
            st.rerun()
            
