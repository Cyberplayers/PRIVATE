import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time as t

# 1. Page Config & Security Shield
st.set_page_config(page_title="Official Friend Portal", layout="centered")

# CSS to block right-clicks and text selection for security
st.markdown("""
    <style>
    * {
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }
    img {
        pointer-events: none;
        -webkit-touch-callout: none;
    }
    .stApp {
        background-color: #0e1117;
        color: #00ff41;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Database Setup
users = {"PANTHER": "SOURCER", "SCORPION": "MASTERMIND", "PRIVATE": "HIDDEN"}
if not os.path.exists("uploads"):
    os.makedirs("uploads")

CHAT_FILE = "chat_log.txt"
STATUS_FILE = "user_activity.txt"

# 3. Functions
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

# 4. Login Logic
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
    # 5. ONLINE STATUS & REFRESH
    st_autorefresh(interval=5000, key="chatupdate")
    update_activity(st.session_state.current_user)
    last_seen = get_last_seen()

    online_agents = [f"🟢 {u}" for u, ts in last_seen.items() if t.time() - ts < 60]
    st.markdown(f"**Agents Active:** {', '.join(online_agents)}")
    st.title(f"Welcome, Agent {st.session_state.current_user}")
    
    # 6. CHAT DISPLAY
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
                        
                        if mtype == "text": 
                            st.write(f"**[{clock}] {sender}:** {content} `{status}`")
                        elif mtype == "image": 
                            st.write(f"**[{clock}] {sender} sent intel:**")
                            st.image(content, width=250) 
                        elif mtype == "audio":
                            st.write(f"**[{clock}] {sender} sent voice:**")
                            st.audio(content)
                    except: continue

    st.divider()

    # 7. INPUT TABS
    t1, t2, t3, t4 = st.tabs(["💬 Text", "📸 Camera", "📁 Media", "🎤 Voice"])
    
    with t1:
        with st.form("txt", clear_on_submit=True):
            m = st.text_input("Message")
            if st.form_submit_button("Send"):
                save_message(st.session_state.current_user, m, "text")
                st.rerun()
    
    with t2:
        img_file = st.camera_input("Take Photo", key="cam_input")
        if img_file:
            if "last_img" not in st.session_state or st.session_state.last_img != img_file.name:
                p = os.path.join("uploads", img_file.name)
                with open(p, "wb") as f: f.write(img_file.getbuffer())
                save_message(st.session_state.current_user, p, "image")
                st.session_state.last_img = img_file.name 
                st.rerun()

    with t3:
        media_file = st.file_uploader("Select from Gallery", type=['png','jpg','jpeg'], key="media_input")
        if media_file and st.button("Upload Selected"):
            mp = os.path.join("uploads", media_file.name)
            with open(mp, "wb") as f: f.write(media_file.getbuffer())
            save_message(st.session_state.current_user, mp, "image")
            st.rerun()

    with t4:
        audio_data = st.audio_input("Tap to record", key="voice_input")
        if audio_data:
            audio_id = hash(audio_data.getvalue())
            if "last_voice_id" not in st.session_state or st.session_state.last_voice_id != audio_id:
                ap = os.path.join("uploads", f"v_{int(t.time())}.wav")
                with open(ap, "wb") as f: f.write(audio_data.getbuffer())
                save_message(st.session_state.current_user, ap, "audio")
                st.session_state.last_voice_id = audio_id 
                st.rerun()

    if st.button("🧨 SELF-DESTRUCT"):
        if os.path.exists(CHAT_FILE): os.remove(CHAT_FILE)
        for f in os.listdir("uploads"): os.remove(os.path.join("uploads", f))
        st.rerun()
