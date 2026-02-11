import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time as t

# 1. Page Config
st.set_page_config(page_title="Official Friend Portal", layout="centered")

# JavaScript for System Notifications (Chrome, Android, Tablets)
def trigger_mobile_notif(sender, message):
    js = f"""
    <script>
    if (Notification.permission === "granted") {{
        const notif = new Notification("New Intel: {sender}", {{
            body: "{message}",
            vibrate: [200, 100, 200],
            tag: 'chat-alert',
            renotify: true
        }});
    }}
    </script>
    """
    st.components.v1.html(js, height=0)

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00ff41; }
    .security-msg { color: #ffffff; font-weight: bold; border: 2px solid #ff4b4b; padding: 10px; border-radius: 5px; background: #ff4b4b; text-align: center; margin-bottom: 10px; }
    .notif-msg { color: #000000; font-weight: bold; border: 1px solid #00ff41; padding: 8px; border-radius: 5px; background: #00ff41; text-align: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Database Setup
