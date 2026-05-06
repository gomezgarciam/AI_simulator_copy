import streamlit as st
import pandas as pd
from typing import Optional

# --- Internal Imports ---
from src.config.settings import settings
from src.services.session_manager import SessionManager
from src.engines.coordinator import SimulationCoordinator
from src.utils.logger import logger

from src.ui.texts import UI_TEXTS
from src.ui.styles import GLOBAL_STYLES
from src.ui.components import (
    render_header,
    section_title,
    render_metric_strip,
    render_glass_tip,
)

from src.services.pdf_service import summarize_text, extract_text_from_uploaded_pdf
from src.services.speech_service import get_speech_clients
from src.services.genai_service import get_genai_client
from src.services.session_service import start_simulation_session
from src.engines.assistant_engine import generate_sales_assistant_response
from src.rag.loader import load_internal_documents_from_gcs
from src.rag.chunking import build_chunk_index

# =========================================================
# 1. INITIALIZATION & RESOURCES
# =========================================================
st.set_page_config(
    page_title=settings.PAGE_TITLE,
    layout="wide",
    page_icon=settings.PAGE_ICON,
)

SessionManager.initialize()
st.markdown(GLOBAL_STYLES, unsafe_allow_html=True)

@st.cache_resource
def get_simulation_resources():
    try:
        genai_client = get_genai_client(settings.GOOGLE_CLOUD_PROJECT, settings.GOOGLE_CLOUD_LOCATION)
        speech_client, tts_client = get_speech_clients()
        coordinator = SimulationCoordinator(genai_client, speech_client, tts_client)
        return genai_client, coordinator
    except Exception as e:
        st.error("Failed to initialize simulation services. Please check your credentials.")
        logger.critical(f"Initialization failure: {e}")
        st.stop()

genai_client, coordinator = get_simulation_resources()

@st.cache_resource
def load_knowledge_base():
    if not settings.INTERNAL_DOCS_BUCKET or "your-bucket" in settings.INTERNAL_DOCS_BUCKET:
        return [], []
    try:
        docs = load_internal_documents_from_gcs(settings.INTERNAL_DOCS_BUCKET, prefix=settings.INTERNAL_DOCS_PREFIX)
        return (docs, build_chunk_index(docs)) if docs else ([], [])
    except Exception as e:
        logger.warning(f"GCS knowledge base load failed: {e}")
        return [], []

internal_docs, internal_chunk_index = load_knowledge_base()

# =========================================================
# 2. LOGIN SCREEN (BMS ID)
# =========================================================
if not SessionManager.get_bms_id():
    login_lang = st.session_state.get("login_language_selector", "English")
    T_login = UI_TEXTS.get(login_lang, UI_TEXTS["English"])
    
    render_header(info_text=T_login.get("login_welcome", ""), key_prefix="login_")
    _, center_col, _ = st.columns([1, 1.5, 1])
    
    with center_col:
        st.markdown(f"<h3 style='text-align: center; color: #1a73e8;'>{T_login.get('login_title', '🔑 BDR Authentication')}</h3>", unsafe_allow_html=True)
        with st.container(border=True):
            bms_input = st.text_input(T_login.get("login_input", ""), key="login_bms_input")
            if st.button(T_login.get("login_btn", "Access"), use_container_width=True, type="primary"):
                if len(bms_input.strip()) >= 3:
                    SessionManager.set_bms_id(bms_input.strip())
                    SessionManager.set_language(login_lang)
                    logger.info(f"User logged in: {bms_input.strip()}")
                    st.rerun()
    st.stop()

# --- Global UI Context ---
T = SessionManager.get_texts()

# =========================================================
# 3. SETUP SCREEN
# =========================================================
if st.session_state.get(SessionManager.TARGET_COMPANY) is None:
    render_header(info_text=T.get("simulator_info", ""), key_prefix="setup_")
    
    left_col, center_col, right_col = st.columns([1.05, 1.15, 1.0], gap="large")
    
    with left_col:
        section_title(T["setup_title"], T["setup_subtitle"])
        company = st.text_input(T["company_q"], key="setup_company").strip()
        
        role_choice = st.selectbox(T["role_q"], ["CTO", "CEO", "CFO", T["other_role_option"]], key="setup_role_sel")
        role = st.text_input(T["custom_role_q"], key="setup_custom_role").strip() if role_choice == T["other_role_option"] else role_choice
        
        uploaded_file = st.file_uploader(T["pdf_uploader_label"], type=["pdf"], key="setup_pdf")
        company_url = st.text_input(T["url_input_label"], key="setup_url")
        
        if st.button(T["start_btn"], use_container_width=True, type="primary"):
            if company and role:
                start_simulation_session(company=company, role=role, language=SessionManager.get_language(), greeting=T["greeting"], company_url=company_url)
                if uploaded_file:
                    pdf_text = extract_text_from_uploaded_pdf(uploaded_file)
                    st.session_state[SessionManager.PDF_SUMMARY] = summarize_text(pdf_text, genai_client, settings.MODEL_ID, SessionManager.get_language()) if len(pdf_text) > settings.PDF_SUMMARY_THRESHOLD else pdf_text
                logger.info(f"Simulation started for {company} - Role: {role}")
                st.rerun()
    
    with center_col:
        section_title(T["scenario_preview"], T["scenario_subtitle"])
        render_metric_strip(company if company else "-", role if role else "-", SessionManager.get_language(), T)

    with right_col:
        section_title(T["assistant_title"], T["assistant_subtitle"])
        if not internal_docs: st.warning(T["no_docs_loaded"])
        render_glass_tip(T["assistant_tip"])
    st.stop()

# =========================================================
# 4. SIMULATION SCREEN (Assisted Mode)
# =========================================================
render_header(info_text=T["simulator_info"], key_prefix="active_")
render_metric_strip(st.session_state[SessionManager.TARGET_COMPANY], st.session_state[SessionManager.ROLE], SessionManager.get_language(), T)

if st.button(T["reset_btn"], type="secondary"):
    SessionManager.clear()
    st.rerun()

left_panel, right_panel = st.columns([2.15, 1.0], gap="large")

with left_panel:
    section_title(T["roleplay_header"], "")
    with st.container(border=True):
        for msg in st.session_state[SessionManager.MESSAGES]:
            with st.chat_message(msg["role"]): st.write(msg["content"])
        
        if st.session_state.get(SessionManager.LAST_AUDIO):
            st.audio(st.session_state[SessionManager.LAST_AUDIO], format="audio/mp3", autoplay=True)

    audio_val = st.audio_input(T["input_label"], key=f"input_{st.session_state[SessionManager.INPUT_KEY]}")
    
    if audio_val:
        with st.spinner(T["listening"]):
            user_text = coordinator.process_user_audio(audio_val, SessionManager.get_language())
            if user_text:
                st.session_state[SessionManager.MESSAGES].append({"role": "user", "content": user_text})
                
                ai_text, ai_audio, is_finished = coordinator.get_alex_response(
                    chat_session=st.session_state.get(SessionManager.CHAT_SESSION),
                    user_text=user_text,
                    language=SessionManager.get_language(),
                    target_company=st.session_state[SessionManager.TARGET_COMPANY],
                    role=st.session_state[SessionManager.ROLE],
                    pdf_summary=st.session_state.get(SessionManager.PDF_SUMMARY),
                    company_url=st.session_state.get(SessionManager.COMPANY_URL)
                )
                
                if ai_text:
                    st.session_state[SessionManager.MESSAGES].append({"role": "assistant", "content": ai_text})
                    st.session_state[SessionManager.LAST_AUDIO] = ai_audio
                    
                    if is_finished:
                        with st.spinner(T["evaluating_spinner"]):
                            report = coordinator.run_evaluation_and_save(
                                st.session_state[SessionManager.MESSAGES],
                                {"bms_id": SessionManager.get_bms_id(), "target_company": st.session_state[SessionManager.TARGET_COMPANY], "role": st.session_state[SessionManager.ROLE]}
                            )
                        
                        st.subheader(f"📊 {T.get('evaluation_results', 'Evaluation Results')}")
                        c1, c2, c3 = st.columns(3)
                        c1.metric(T.get("final_score_label", "Final Score"), f"{report['final_score']}%")
                        c2.metric(T.get("status_label", "Status"), report["status"])
                        c3.metric(T.get("points_label", "Points"), f"{report['actual_points']} / {report['max_points']}")

                        df_evals = pd.DataFrame(report["evaluations"])
                        st.markdown("### 📝 Detalle de Evaluación MEDPICC")
                        st.dataframe(
                            df_evals[["category", "parameter", "rating", "points", "evidence", "improvement_tip"]],
                            hide_index=True,
                            use_container_width=True
                        )
                        st.info(f"**Comentario Ejecutivo:** {report.get('final_comment', '')}")
                        st.balloons()
                        st.stop()
                        
                    st.session_state[SessionManager.INPUT_KEY] += 1
                    st.rerun()

with right_panel:
    section_title(T["assistant_title"], T["assistant_subtitle"])
    with st.container(border=True, height=400):
        for msg in st.session_state.get(SessionManager.ASSISTANT_MESSAGES, []):
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if msg.get("sources"): st.caption(f"Sources: {', '.join(msg['sources'])}")

    with st.form("asst_form", clear_on_submit=True):
        asst_q = st.text_input(T["assistant_input"])
        if st.form_submit_button(T["assistant_button"], use_container_width=True) and asst_q:
            st.session_state[SessionManager.ASSISTANT_MESSAGES].append({"role": "user", "content": asst_q})
            try:
                answer, sources = generate_sales_assistant_response(
                    user_question=asst_q,
                    conversation_history=st.session_state[SessionManager.MESSAGES],
                    company=st.session_state[SessionManager.TARGET_COMPANY],
                    role=st.session_state[SessionManager.ROLE],
                    chunk_index=internal_chunk_index,
                    uploaded_company_context=st.session_state.get(SessionManager.PDF_SUMMARY),
                    language=SessionManager.get_language(),
                    genai_client=genai_client,
                    model_id=settings.MODEL_ID
                )
                st.session_state[SessionManager.ASSISTANT_MESSAGES].append({"role": "assistant", "content": answer, "sources": sources})
                st.rerun()
            except Exception as e:
                logger.error(f"Assistant error: {e}")
                st.error("Assistant is currently unavailable.")
