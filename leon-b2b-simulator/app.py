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
    render_evaluation_card,
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
from src.evaluation.rubric_engine import evaluate_transcript, format_transcript_from_messages
import streamlit as st
import io
import json
import pandas as pd
from typing import Optional
from src.rag.loader import load_internal_documents_from_gcs
from src.rag.chunking import build_chunk_index
from src.rag.context_builder import build_assistant_context
from src.services.db_service import save_simulation_to_bq

# =========================================================
# 1. APP CONFIG
# =========================================================
st.set_page_config(
    page_title=PAGE_TITLE,
    layout="wide",
    page_icon=PAGE_ICON,
)

initialize_session_state()

# --- LANGUAGE & MODE ---
lang_choice = st.session_state.get("language_selector", "English")
T = UI_TEXTS[lang_choice]
mode = st.session_state.get("app_mode", T["mode_classic_title"])

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
    # Solo intentamos cargar si el bucket está configurado y no es el default de cloudshell
    if not INTERNAL_DOCS_BUCKET or "your-bucket" in INTERNAL_DOCS_BUCKET:
        return [], []

    try:
        # Añadimos un mensaje de estado que no bloquee
        with st.spinner("Conectando con base de conocimientos FY26..."):
            docs = load_internal_documents_from_gcs(
                INTERNAL_DOCS_BUCKET,
                prefix=INTERNAL_DOCS_PREFIX,
            )
            if not docs:
                return [], []
            chunk_index = build_chunk_index(docs)
            return docs, chunk_index
    except Exception as e:
        print(f"DEBUG: GCS Load failed (normal in dev): {e}")
        return [], []

# Intentamos cargar, pero si falla o tarda, la app sigue
try:
    internal_docs, internal_chunk_index = load_document_knowledge()
except:
    internal_docs, internal_chunk_index = [], []


# =========================================================
# 3. GLOBAL STYLES
# =========================================================
st.markdown(GLOBAL_STYLES, unsafe_allow_html=True)
# =========================================================
# 3.5. BDR AUTHENTICATION (BMS LOGIN)
# =========================================================
if not st.session_state.get("bms_id"):
    # 1. Leemos el idioma específico del selector de esta pantalla
    login_lang = st.session_state.get("login_language_selector", "English")
    T_login = UI_TEXTS.get(login_lang, UI_TEXTS["English"])

    render_header(info_text=T_login.get("login_welcome", ""), key_prefix="login_")

    st.write("<br><br>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 1.5, 1])

    with center_col:
        st.markdown(f"<h3 style='text-align: center; color: #1a73e8;'>{T_login.get('login_title', '🔑 BDR Authentication')}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #5f6368;'>{T_login.get('login_desc', '')}</p>", unsafe_allow_html=True)

        with st.container(border=True):
            bms_input = st.text_input(T_login.get("login_input", ""), placeholder=T_login.get("login_placeholder", ""), key="login_bms_input")

            if st.button(T_login.get("login_btn", "Access Simulator"), use_container_width=True, type="primary"):
                if len(bms_input.strip()) < 3:
                    st.error(T_login.get("login_err", ""))
                else:
                    st.session_state.bms_id = bms_input.strip()
                    # 2. Sincronizamos el idioma maestro para el resto de la app
                    st.session_state.language_selector = login_lang
                    st.rerun()

    st.stop()
# =========================================================
# 5. SETUP SCREEN
# =========================================================
if st.session_state.target_company is None:
    render_header(info_text=T.get("simulator_info", ""), key_prefix="setup_")

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

        # --- MODE EXPLANATIONS ---
        st.markdown(
            f"""
            <div style="background: rgba(26, 115, 232, 0.05); padding: 1rem; border-radius: 12px; border: 1px solid rgba(26, 115, 232, 0.2); margin-bottom: 1.5rem;">
                <div style="font-weight: 600; color: var(--google-blue); margin-bottom: 0.5rem; font-size: 0.9rem;">{T['mode_classic_title']}</div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.4;">{T['mode_classic_desc']}</div>
                <div style="margin-top: 1rem; font-weight: 600; color: #15803d; margin-bottom: 0.5rem; font-size: 0.9rem;">{T['mode_live_title']}</div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.4;">{T['mode_live_desc']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        preview_company = company if company else "-"
        preview_role = role if role else "-"

        render_metric_strip(
            preview_company,
            preview_role,
            lang_choice,
            T,
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
if mode == T["mode_live_title"]:
    render_header(info_text=T.get("simulator_info", ""), key_prefix="live_")

    st.title(f"Live Mode: {st.session_state.target_company}")

    # Preparamos metadatos reales de la sesión activa
    metadata = {
        "target_company": st.session_state.target_company,
        "role": st.session_state.role,
        "language": st.session_state.language,
        "bms_id": st.session_state.get("bms_id", "UNKNOWN")
    }

    render_metric_strip(
        metadata["target_company"],
        metadata["role"],
        metadata["language"],
        T=T
    )

    # Render our custom component with metadata
    live_mic_recorder(metadata=metadata)

    st.stop()
# =========================================================
# 6. ACTIVE SESSION (Assisted Mode)
# =========================================================
# T is already defined
# assistant siempre abierto
st.session_state.show_assistant = True

# =========================================================
# 6. TOP HEADER
# =========================================================
render_header(info_text=T["simulator_info"], key_prefix="assisted_")

render_metric_strip(
    st.session_state.target_company,
    st.session_state.role,
    st.session_state.language,
    T=T
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

                    if "FINISH_CALL" in ai_text:
                        clean_ai_text = ai_text.replace("FINISH_CALL", "").strip()
                        st.session_state.messages.append({"role": "assistant", "content": clean_ai_text})
                        st.session_state.last_audio = synthesize_speech(tts_client, clean_ai_text, st.session_state.language)
                        
                        with st.spinner(T.get("evaluating_spinner", "Generating professional evaluation...")):
                            report = evaluate_transcript(format_transcript_from_messages(st.session_state.messages), genai_client, MODEL_ID)
                        
                        # --- NUEVO: GUARDAR EN BIGQUERY ---
                        payload_bq = {
                            "bms_id": st.session_state.get("bms_id", "UNKNOWN"),
                            "sim_mode": "Assisted Mode",
                            "target_company": st.session_state.target_company,
                            "role": st.session_state.role,
                            "final_score": report.get("final_score", 0),
                            "status": report.get("status", ""),
                            "detailed_evaluation": report.get("evaluations", []),
                            "transcript": format_transcript_from_messages(st.session_state.messages)
                        }
                        # Usamos el Project ID que ya tienes en settings.py
                        save_simulation_to_bq(GOOGLE_CLOUD_PROJECT, payload_bq)
                        # ----------------------------------
                        
                        st.divider()
                        st.subheader(f"📊 {T.get('evaluation_results', 'Evaluation Results')}")
                        c1, c2, c3 = st.columns(3)
                        c1.metric(T.get("final_score_label", "Final Score"), f"{report['final_score']}%")
                        c2.metric(T.get("status_label", "Status"), report["status"])
                        c3.metric(T.get("points_label", "Points"), f"{report['actual_points']} / {report['max_points']}")

                        st.info(report.get("final_comment", ""))
                        
                        # Crear el dataframe
                        df_evals = pd.DataFrame(report["evaluations"])
                        
                        # --- NUEVO: Desglose por Categoría ---
                        st.markdown("### 📈 Desglose por Categoría")
                        cat_scores = df_evals.groupby("category")["points"].sum().reset_index()
                        cat_cols = st.columns(len(cat_scores))
                        for idx, row in cat_scores.iterrows():
                            cat_cols[idx].metric(row["category"], f"{row['points']} pts")

                        # --- NUEVO: Tabla Detallada Limpia ---
                        st.markdown("### 📝 Detalle de Evaluación MEDPICC")
                        st.dataframe(
                            df_evals[["category", "parameter", "rating", "points", "evidence", "improvement_tip"]],
                            hide_index=True,
                            use_container_width=True
                        )
                        
                        st.info(f"**Comentario Ejecutivo:** {report.get('final_comment', '')}")
                        st.balloons()
                        st.stop()

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
