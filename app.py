import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time as t

# 1. Page Config
st.set_page_config(page_title="Official Friend Portal", layout="centered")

# 2. Setup Database & Users
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

# 4. Auth Logic
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
    # AUTO-REFRESH (Every 5 seconds)
    st_autorefresh(interval=5000, key="chatupdate")
    update_activity(st.session_state.current_user)
    last_seen = get_last_seen()

    st.title(f"Welcome, Agent {st.session_state.current_user}")
    
    # CHAT BOX WITH AUTO-SCROLL
    chat_box = st.container(height=450)
    with chat_box:
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, "r") as f:
                for line in f.readlines():
                    try:
                        unix, clock, sender, mtype, content = line.strip().split("|")
                        # SEEN LOGIC (✓✓)
                        status = "✓"
                        for u, ts in last_seen.items():
                            if u != sender and ts > float(unix): status = "✓✓"
                        
                        if mtype == "text": st.write(f"**[{clock}] {sender}:** {content} `{status}`")
                        elif mtype == "image": 
                            st.write(f"**[{clock}] {sender} sent intel:**")
                            st.image(content)
                        elif mtype == "audio":
                            st.write(f"**[{clock}] {sender} sent voice:**")
                            st.audio(content)
                    except: continue

    st.divider()

    # THE FOUR OPTIONS TABS
    t1, t2, t3, t4 = st.tabs(["💬 Text", "📸 Camera", "📁 Media", "🎤 Voice"])
    
    with t1:
        with st.form("txt", clear_on_submit=True):
            m = st.text_input("Message")
            if st.form_submit_button("Send"):
                save_message(st.session_state.current_user, m, "text")
                st.rerun()
    
    with t2:
        # CAMERA: Opens phone camera immediately
        img_file = st.camera_input("Take Photo")
        if img_file:
            p = os.path.join("uploads", img_file.name)
            with open(p, "wb") as f: f.write(img_file.getbuffer())
            save_message(st.session_state.current_user, p, "image")
            st.success("Photo Dispatched!")
            st.rerun()

    with t3:
        # MEDIA: Choose existing files from phone gallery
        media_file = st.file_uploader("Select from Gallery", type=['png','jpg','jpeg','mp4','mov'])
        if media_file and st.button("Upload Selected"):
            mp = os.path.join("uploads", media_file.name)
            with open(mp, "wb") as f: f.write(media_file.getbuffer())
            save_message(st.session_state.current_user, mp, "image")
            st.rerun()

    with t4:
        # VOICE: Record directly from browser microphone
        st.write("Record Voice Note")
        audio_file = st.audio_input("Tap to record voice")
        if audio_file:
            ap = os.path.join("uploads", f"v_{int(t.time())}.wav")
            with open(ap, "wb") as f: f.write(audio_file.getbuffer())
            save_message(st.session_state.current_user, ap, "audio")
            st.success("Voice Sent!")
            st.rerun()

    if st.button("🧨 SELF-DESTRUCT"):
        if os.path.exists(CHAT_FILE): os.remove(CHAT_FILE)
        st.rerun()
