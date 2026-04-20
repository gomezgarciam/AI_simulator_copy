from src.config.settings import (
    PAGE_TITLE,
    PAGE_ICON,
    MODEL_ID,
    GOOGLE_CLOUD_PROJECT,
    GOOGLE_CLOUD_LOCATION,
    INTERNAL_DOCS_BUCKET,
    INTERNAL_DOCS_PREFIX,
    ASSISTANT_TOP_K,
    ROLEPLAY_HISTORY_MAX_TURNS,
    PDF_SUMMARY_THRESHOLD,
)
from src.ui.texts import UI_TEXTS
from src.ui.styles import GLOBAL_STYLES
from src.ui.components import (
    render_header,
    section_title,
    render_metric_strip,
    render_glass_tip,
    live_mic_recorder,
)
from src.services.pdf_service import (
    summarize_text,
    extract_text_from_uploaded_pdf,
)
from src.services.audio_service import load_audiosegment_from_streamlit_audio
from src.services.genai_service import (
    get_genai_client,
    create_chat_session,
    generate_content,
)
from src.services.speech_service import (
    get_speech_clients,
    transcribe_audio,
    synthesize_speech,
)
from src.services.session_service import (
    initialize_session_state,
    start_simulation_session,
    clear_session_state,
)
from src.engines.roleplay_engine import (
    get_or_create_roleplay_session,
    send_roleplay_message,
)
from src.prompts.assistant import create_sales_assistant_prompt
from src.prompts.assistant import create_document_assistant_prompt
from src.engines.assistant_engine import generate_sales_assistant_response
import streamlit as st
import io
import json
import pandas as pd
from typing import Optional
from src.rag.loader import load_internal_documents_from_gcs
from src.rag.chunking import build_chunk_index
from src.rag.context_builder import build_assistant_context

# =========================================================
# 1. APP CONFIG
# =========================================================
st.set_page_config(
    page_title=PAGE_TITLE,
    layout="wide",
    page_icon=PAGE_ICON,
)

initialize_session_state()

# --- NEW: SPRINT 1 MODE SELECTOR ---
mode = st.sidebar.radio("Select Mode", ("Classic MVP", "Live Mode (Sprint 1 Test)"))

# =========================================================
# 2. CLIENTS / RESOURCES
# =========================================================
@st.cache_resource
def get_clients():
    genai_client_local = get_genai_client(
        GOOGLE_CLOUD_PROJECT,
        GOOGLE_CLOUD_LOCATION,
    )
    speech_client_local, tts_client_local = get_speech_clients()
    return genai_client_local, speech_client_local, tts_client_local


@st.cache_resource
def load_document_knowledge():
    try:
        docs = load_internal_documents_from_gcs(
            INTERNAL_DOCS_BUCKET,
            prefix=INTERNAL_DOCS_PREFIX,
        )
        chunk_index = build_chunk_index(docs)
        return docs, chunk_index
    except Exception as e:
        st.error(f"Error loading internal documents from GCS: {e}")
        return [], []


try:
    genai_client, speech_client, tts_client = get_clients()
except Exception as e:
    st.error(f"Credential/API error: {e}")
    st.stop()

internal_docs, internal_chunk_index = load_document_knowledge()


# =========================================================
# 3. GLOBAL STYLES
# =========================================================
st.markdown(GLOBAL_STYLES, unsafe_allow_html=True)
# =========================================================
# 4. SETUP SCREEN
# =========================================================
if "target_company" not in st.session_state:
    # We use the language selector from the header directly
    render_header(
        info_text=UI_TEXTS["English"].get(
            "simulator_info",
            "This simulator recreates enterprise sales conversations and provides real-time guidance."
        )
    )
    
    lang_choice = st.session_state.get("language_selector", "English")
    T = UI_TEXTS[lang_choice]

    lang_choice = st.session_state.get("language_selector", "English")
    T = UI_TEXTS[lang_choice]

    st.markdown(
        f"""
        <div class="language-bar">
            <div class="language-bar-title">{T['presentation_language']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ROLES = ["CTO", "CEO", "CFO", T["other_role_option"]]

    left_col, center_col, right_col = st.columns([1.05, 1.15, 1.0], gap="large")

    with left_col:
        section_title(T["setup_title"], T["setup_subtitle"])

        st.markdown(
            f"<div class='section-kicker'>{T['profile_kicker']}</div>",
            unsafe_allow_html=True,
        )

        company = st.text_input(
            T["company_q"],
            placeholder=T.get("company_placeholder", "e.g. Uber"),
            key=f"company_input_{lang_choice}",
        ).strip()

        st.markdown(
            f"<div class='section-kicker'>{T['scenario_kicker']}</div>",
            unsafe_allow_html=True,
        )

        role_choice = st.selectbox(
            T["role_q"],
            ROLES,
            key=f"role_selector_{lang_choice}",
        )

        if role_choice == T["other_role_option"]:
            role = st.text_input(
                T["custom_role_q"],
                key=f"custom_role_{lang_choice}",
            ).strip()
            st.info(T["role_info_message"])
        else:
            role = role_choice

        st.markdown(
            f"<div class='section-kicker'>{T['additional_context']}</div>",
            unsafe_allow_html=True,
        )

        st.info(T["pdf_info"])

        uploaded_file = st.file_uploader(
            T["pdf_uploader_label"],
            type=["pdf"],
            key=f"uploader_{lang_choice}",
        )

        company_url = st.text_input(
            T["url_input_label"],
            key=f"url_{lang_choice}",
        )

        if st.button(T["start_btn"], use_container_width=True, key=f"start_btn_{lang_choice}"):
            if not company:
                st.warning(T.get("company_required", "Please enter a company name."))
                st.stop()

            if not role:
                st.warning(T.get("role_required", "Please enter a valid role."))
                st.stop()

            start_simulation_session(
                company=company,
                role=role,
                language=lang_choice,
                greeting=T["greeting"],
                company_url=company_url,
            )

            if uploaded_file:
                with st.spinner(T["pdf_processing"]):
                    try:
                        pdf_text = extract_text_from_uploaded_pdf(uploaded_file)
                        if pdf_text:
                            if len(pdf_text) > PDF_SUMMARY_THRESHOLD:
                                st.session_state.pdf_summary = summarize_text(
                                    pdf_text,
                                    genai_client,
                                    MODEL_ID,
                                    lang_choice,
                                )
                            else:
                                st.session_state.pdf_summary = pdf_text
                        else:
                            st.warning(T["pdf_empty"])
                    except Exception as e:
                        st.error(f"Error reading or processing uploaded PDF: {e}")

            st.rerun()

    with center_col:
        section_title(T["scenario_preview"], T["scenario_subtitle"])

        preview_company = company if company else "-"
        preview_role = role if role else "-"

        render_metric_strip(
            preview_company,
            preview_role,
            lang_choice,
            T,
        )

        st.markdown(
            f"""
            <div class="scenario-box">
                <strong>{T['company']}:</strong> {preview_company}<br>
                <strong>{T['role']}:</strong> {preview_role}<br>
                <strong>{T['language']}:</strong> {lang_choice}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        section_title(T["assistant_title"], T["assistant_subtitle"], T["assistant_info"])

        st.markdown(
            f"""
            <div class="assistant-badge">
                <div class="assistant-badge-title">{T['knowledge_badge_title']}</div>
                <div class="assistant-badge-desc">{T['knowledge_badge_desc']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not internal_docs:
            st.warning(T["no_docs_loaded"])
        else:
            st.caption(T["assistant_connected"])

        render_glass_tip(T["assistant_tip"])

        with st.container(border=True, height=360):
            st.markdown(
                f"<div class='small-muted'>{T['assistant_empty_state']}</div>",
                unsafe_allow_html=True,
            )

    st.stop()


# =========================================================
# 5. LIVE MODE OVERRIDE (Sprint 2)
# =========================================================
if mode == "Live Mode (Sprint 1 Test)":
    T = UI_TEXTS[st.session_state.language]
    render_header(info_text=T.get("simulator_info", ""))
    
    st.title(f"Live Mode: {st.session_state.target_company}")
    
    # Preparamos metadatos reales de la sesión activa
    metadata = {
        "target_company": st.session_state.target_company,
        "role": st.session_state.role,
        "language": st.session_state.language
    }
    
    st.info(f"Interacting with Alex as **{metadata['role']}** in **{metadata['language']}**.")
    
    # Render our custom component with metadata
    live_mic_recorder(metadata=metadata)
    
    st.stop()

# =========================================================
# 6. ACTIVE SESSION TEXTS (Classic MVP)
# =========================================================
T = UI_TEXTS[st.session_state.language]

# assistant siempre abierto
st.session_state.show_assistant = True

# =========================================================
# 6. TOP HEADER
# =========================================================
render_header(info_text=T["simulator_info"])

render_metric_strip(
    st.session_state.target_company,
    st.session_state.role,
    st.session_state.language,
    T=T
)

st.markdown(
    f"<div class='session-caption'>{T.get('session_caption', 'Live simulation with Alex')} | {st.session_state.role} at {st.session_state.target_company}</div>",
    unsafe_allow_html=True
)

top_actions_left, top_actions_right = st.columns([6, 1.2])

with top_actions_right:
    if st.button(T["reset_btn"], use_container_width=True):
        clear_session_state()
        st.rerun()

# =========================================================
# 7. MAIN LAYOUT
# =========================================================
left_col, right_col = st.columns([2.15, 1.0], gap="large")
# =========================================================
# 8. LEFT PANEL - ROLEPLAY
# =========================================================
with left_col:
    section_title(T["roleplay_header"], "")
    render_glass_tip(T["roleplay_tip"])
    st.info(f"**{T['instructions_label']}:**\n\n" + "\n".join(T["instructions"]))

    with st.container(border=True):
        for i, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

                if i == len(st.session_state.messages) - 1:
                    if msg["role"] == "assistant" and st.session_state.get("last_audio"):
                        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)

    if st.session_state.get("user_audio_debug"):
        with st.expander(T["debug_label"]):
            st.audio(st.session_state.user_audio_debug)

    audio_val = st.audio_input(T["input_label"], key=f"a_{st.session_state.input_key}")

    if audio_val is not None:
        st.session_state.user_audio_debug = audio_val

        with st.spinner(T["listening"]):
            try:
                seg = load_audiosegment_from_streamlit_audio(audio_val)

                if seg is None:
                    st.info(T["no_audio_heard"])
                    st.stop()

                buf = io.BytesIO()
                seg.export(buf, format="wav")

                user_text = transcribe_audio(
                    speech_client,
                    buf.getvalue(),
                    st.session_state.language,
                )

                if not user_text:
                    st.info(T["no_audio_heard"])
                    st.stop()

                st.session_state.messages.append({
                    "role": "user",
                    "content": user_text,
                })

                try:
                    st.session_state.chat_session = get_or_create_roleplay_session(
                        existing_chat_session=st.session_state.get("chat_session"),
                        genai_client=genai_client,
                        model_id=MODEL_ID,
                        target_company=st.session_state.target_company,
                        role=st.session_state.role,
                        language=st.session_state.language,
                        stop_phrase=T["stop_phrase"],
                        pdf_summary=st.session_state.get("pdf_summary"),
                        company_url=st.session_state.get("company_url"),
                        temperature=0.7,
                    )

                    response_ai, quota_warning = send_roleplay_message(
                        chat_session=st.session_state.chat_session,
                        user_text=user_text,
                        language=st.session_state.language,
                        max_retries=3,
                    )

                    if quota_warning:
                        st.error(quota_warning)
                        st.stop()

                    if not response_ai or not response_ai.text:
                        st.warning(T["no_ai_response"])
                        st.stop()

                    ai_text = response_ai.text

                    if "feedback_table" in ai_text:
                        try:
                            start = ai_text.find("{")
                            end = ai_text.rfind("}") + 1
                            data = json.loads(ai_text[start:end])

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": T["feedback_intro"],
                            })

                            df = pd.DataFrame(data["feedback_table"])
                            st.dataframe(df, hide_index=True, use_container_width=True)
                            st.info(data.get("final_comment", ""))
                            st.stop()
                        except Exception:
                            pass

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": ai_text,
                    })

                    st.session_state.last_audio = synthesize_speech(
                        tts_client,
                        ai_text,
                        st.session_state.language,
                    )

                    st.session_state.input_key += 1
                    st.rerun()

                except Exception as e:
                    st.error(f"Error en la comunicación con Alex: {e}")
                    if "closed" in str(e).lower():
                        st.session_state.chat_session = None

            except Exception as e:
                st.warning(T["instructions"][0])
                st.error(f"{T['audio_invalid']} Detail: {e}")

# =========================================================
# 9. RIGHT PANEL - SALES ASSISTANT
# =========================================================
with right_col:
    st.markdown("<div class='assistant-panel'>", unsafe_allow_html=True)
    section_title(T["assistant_title"], T["assistant_subtitle"], T["assistant_info"])

    st.markdown(
        f"""
        <div class="assistant-badge">
            <div class="assistant-badge-title">
                {T['knowledge_badge_title']}
            </div>
            <div class="assistant-badge-desc">
                {T['knowledge_badge_desc']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not internal_docs:
        st.warning(T["no_docs_loaded"])
    else:
        st.caption(T["assistant_connected"])

    with st.container(border=True, height=340):
        if not st.session_state.get("assistant_messages"):
            st.markdown(
                f"<div class='small-muted'>{T['assistant_empty_state']}</div>",
                unsafe_allow_html=True,
            )

        for msg in st.session_state.get("assistant_messages", []):
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if msg.get("sources"):
                    st.caption(f"{T['assistant_sources']} " + ", ".join(msg["sources"]))

    with st.form("assistant_form", clear_on_submit=True):
        assistant_question = st.text_input(
            T["assistant_input"],
            placeholder=T["assistant_placeholder"],
        )
        assistant_submitted = st.form_submit_button(
            T["assistant_button"],
            use_container_width=True,
        )

    if assistant_submitted and assistant_question.strip():
        st.session_state.assistant_messages.append({
            "role": "user",
            "content": assistant_question.strip(),
        })

        with st.spinner(T["assistant_loading"]):
            try:
                answer, sources = generate_sales_assistant_response(
                        user_question=assistant_question.strip(),
                        conversation_history=st.session_state.messages,
                        company=st.session_state.target_company,
                        role=st.session_state.role,
                        chunk_index=internal_chunk_index,
                        uploaded_company_context=st.session_state.get("pdf_summary"),
                        language=st.session_state.language,
                        genai_client=genai_client,
                        model_id=MODEL_ID,
                        assistant_top_k=ASSISTANT_TOP_K,
                        roleplay_history_max_turns=ROLEPLAY_HISTORY_MAX_TURNS,
                )

                st.session_state.assistant_messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })

            except Exception as e:
                st.session_state.assistant_messages.append({
                    "role": "assistant",
                    "content": f"{T['assistant_error']} {e}",
                    "sources": [],
                })

        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)