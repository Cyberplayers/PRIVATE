import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time as t

# 1. Page Config & Security Shield
st.set_page_config(page_title="Official Friend Portal", layout="centered")

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
                    p = line.strip().split("|")
                    seen_dict[p[0]] = float(p[1])
                except:
                    continue
    return seen_dict

# 4. Automated Security Notifications (Screenshot Detection)
st.components.v1.html(f"""
    <script>
    document.addEventListener("visibilitychange", function() {{
        if (document.visibilityState === 'hidden') {{
            fetch("/?ss_event=true&user={st.session_state.get('current_user', 'UNKNOWN')}");
        }}
    }});
    </script>
""", height=0)

if st.query_params.get("ss_event") == "true":
    violator = st.query_params.get("user", "UNKNOWN")
    if violator != "PANTHER" and violator != "UNKNOWN":
        save_message("SYSTEM", f"🚨 ALERT: {violator} detected leaving or capturing screen!", "security")
    st.query_params.clear()

# 5. Session & 90-Second Timeout
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
    # 7. Navigation Row
    st_autorefresh(interval=5000, key="chatupdate")
    update_activity(st.session_state.current_user)
    
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
    
    # 8. Chat Display
    chat_box = st.container(height=450)
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
                        else:
                            st.write(f"**[{clock}] {sender}:** {content}")
                            if mtype == "image": st.image(content, width=250)
                            if mtype == "audio": st.audio(content)
                    except:
                        continue

    st.divider()

    # 9. Communication Tabs
    t1, t2, t3, t4 = st.tabs(["💬 Text", "📸 Camera", "📁 Media", "🎤 Voice"])
    
    with t1:
        with st.form("txt", clear_on_submit=True):
            m = st.text_input("Message")
            if st.form_submit_button("Send"):
                save_message(st.session_state.current_user, m, "text")
                st.session_state.last_action_time = t.time()
                st.rerun()
    
    with t2:
        img_file = st.camera_input("Take Photo", key="cam_input")
        if img_file:
            if "last_img" not in st.session_state or st.session_state.last_img != img_file.name:
                p = os.path.join("uploads", img_file.name)
                with open(p, "wb") as f:
                    f.write(img_file.getbuffer())
                save_message(st.session_state.current_user, p, "image")
                st.session_state.last_img = img_file.name 
                st.session_state.last_action_time = t.time()
                st.rerun()

    with t3:
        media_file = st.file_uploader("Upload Intel", type=['png','jpg','jpeg'], key="media_input")
        if media_file and st.button("Submit Media"):
            mp = os.path.join("uploads", media_file.name)
            with open(mp, "wb") as f:
                f.write(media_file.getbuffer())
            save_message(st.session_state.current_user, mp, "image")
            st.session_state.last_action_time = t.time()
            st.rerun()

    with t4:
        voice = st.audio_input("Record", key="voice_input")
        if voice:
            vid = hash(voice.getvalue())
            if "last_v" not in st.session_state or st.session_state.last_v != vid:
                ap = os.path.join("uploads", f"v_{int(t.time())}.wav")
                with open(ap, "wb") as f:
                    f.write(voice.getbuffer())
                save_message(st.session_state.current_user, ap, "audio")
                st.session_state.last_v = vid 
                st.session_state.last_action_time = t.time()
                st.rerun()

    # 10. Self-Destruct
    if st.button("🧨 SELF-DESTRUCT"):
        if os.path.exists(CHAT_FILE):
            os.remove(CHAT_FILE)
        for fn in os.listdir("uploads"):
            os.remove(os.path.join("uploads", fn))
        st.rerun()
