import streamlit as st
from typing import Any, Dict, List, Optional
from src.ui.texts import UI_TEXTS

class SessionManager:
    """
    Wrapper for Streamlit session_state to provide typed access and centralize key management.
    """

    # Key constants
    BMS_ID = "bms_id"
    LANGUAGE = "session_language"
    APP_MODE = "app_mode"
    TARGET_COMPANY = "target_company"
    ROLE = "role"
    MESSAGES = "messages"
    ASSISTANT_MESSAGES = "assistant_messages"
    CHAT_SESSION = "chat_session"
    LAST_AUDIO = "last_audio"
    USER_AUDIO_DEBUG = "user_audio_debug"
    INPUT_KEY = "input_key"
    PDF_SUMMARY = "pdf_summary"
    COMPANY_URL = "company_url"

    @staticmethod
    def initialize():
        """Initialize default values for session state."""
        if SessionManager.BMS_ID not in st.session_state:
            st.session_state[SessionManager.BMS_ID] = None
        if SessionManager.LANGUAGE not in st.session_state:
            st.session_state[SessionManager.LANGUAGE] = "English"
        if SessionManager.TARGET_COMPANY not in st.session_state:
            st.session_state[SessionManager.TARGET_COMPANY] = None
        if SessionManager.MESSAGES not in st.session_state:
            st.session_state[SessionManager.MESSAGES] = []
        if SessionManager.ASSISTANT_MESSAGES not in st.session_state:
            st.session_state[SessionManager.ASSISTANT_MESSAGES] = []
        if SessionManager.INPUT_KEY not in st.session_state:
            st.session_state[SessionManager.INPUT_KEY] = 0

    @classmethod
    def get_bms_id(cls) -> Optional[str]:
        return st.session_state.get(cls.BMS_ID)

    @classmethod
    def set_bms_id(cls, bms_id: str):
        st.session_state[cls.BMS_ID] = bms_id

    @classmethod
    def get_language(cls) -> str:
        return st.session_state.get(cls.LANGUAGE, "English")

    @classmethod
    def set_language(cls, language: str):
        st.session_state[cls.LANGUAGE] = language

    @classmethod
    def get_texts(cls) -> Dict[str, Any]:
        lang = cls.get_language()
        return UI_TEXTS.get(lang, UI_TEXTS["English"])

    @classmethod
    def clear(cls):
        """Reset all simulation related keys."""
        keys_to_reset = [
            cls.TARGET_COMPANY, cls.ROLE, cls.MESSAGES, 
            cls.ASSISTANT_MESSAGES, cls.CHAT_SESSION, 
            cls.LAST_AUDIO, cls.USER_AUDIO_DEBUG,
            cls.PDF_SUMMARY, cls.COMPANY_URL
        ]
        for key in keys_to_reset:
            if key in st.session_state:
                st.session_state[key] = None if "messages" not in key else []
        st.session_state[cls.INPUT_KEY] = 0
