import streamlit as st

st.set_page_config(page_title="Official Friend Portal", layout="centered")

users = {
    "PANTHER": "SOURCER",
    "SCORPION": "MASTERMIND",
    "PRIVATE": "HIDDEN"
}


if "emergency" not in st.session_state:
    st.session_state.emergency = False
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


if not st.session_state.authenticated:
    st.title("🔒 Official Login Portal")
    name = st.text_input("Username")
    word = st.text_input("Password", type="password")

    if st.button("Enter Portal"):
        if name in users and users[name] == word:
            st.session_state.authenticated = True
            st.session_state.current_user = name
            st.rerun()
        else:
            st.error("Invalid Credentials")

else:
    if st.session_state.emergency:
        st.error("🚨 RISK DETECTED: URGENT TALK REQUESTED!")
        st.warning(f"⚠️ {st.session_state.emergency_sender} needs attention NOW!")
        if st.button("Clear Alarm"):
            st.session_state.emergency = False
            st.rerun()

    st.title(f"👋 Welcome, {st.session_state.current_user}")

    if st.button("🆘 TRIGGER EMERGENCY NOTIFICATION"):
        st.session_state.emergency = True
        st.session_state.emergency_sender = st.session_state.current_user
        st.rerun()

    chat_msg = st.text_input("Send a message:")
    if chat_msg:
        st.info(f"{st.session_state.current_user}: {chat_msg}")

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
