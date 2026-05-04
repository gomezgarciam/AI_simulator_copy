import streamlit as st


DEFAULT_SESSION_VALUES = {
    "bms_id": None,
    "assistant_messages": [],
    "messages": [],
    "input_key": 0,
    "last_audio": None,
    "user_audio_debug": None,
    "pdf_summary": None,
    "chat_session": None,
    "show_assistant": True,
    "company_url": "",
    "show_mode_selector": False,
    "app_mode": "Classic MVP",
    "language": "English",
    "target_company": None,
    "role": None,
}


def initialize_session_state():
    for key, value in DEFAULT_SESSION_VALUES.items():
        if key not in st.session_state:
            st.session_state[key] = value


def start_simulation_session(company: str, role: str, language: str, greeting: str, company_url: str = ""):
    st.session_state.target_company = company
    st.session_state.role = role
    st.session_state.language = language
    st.session_state.company_url = company_url.strip() if company_url else ""

    st.session_state.messages = [
        {"role": "assistant", "content": greeting}
    ]
    st.session_state.assistant_messages = []
    st.session_state.input_key = 0
    st.session_state.last_audio = None
    st.session_state.user_audio_debug = None
    st.session_state.pdf_summary = None
    st.session_state.chat_session = None
    st.session_state.show_assistant = True


def clear_session_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]