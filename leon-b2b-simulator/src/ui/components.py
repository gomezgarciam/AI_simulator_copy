import base64
import os
from pathlib import Path
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

from src.services.session_manager import SessionManager
from src.ui.texts import UI_TEXTS


def live_mic_recorder(metadata: dict = None):
    """
    Bridge for the custom Live Mode microphone component.
    """
    component_path = "leon-b2b-simulator/components/mic_recorder/frontend/public"
    if not os.path.exists(component_path):
        component_path = "components/mic_recorder/frontend/public"

    _component_func = components.declare_component(
        "live_mic_recorder", path=component_path
    )

    return _component_func(metadata=metadata)


def get_image_base64(path: str) -> Optional[str]:
    try:
        p = Path(path)
        if p.exists():
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        return None
    return None


def render_header(info_text: str = "", key_prefix: str = ""):
    # Look for the project image in assets
    img_base64 = get_image_base64("assets/project_hero.png")

    # 1. READ GLOBAL LANGUAGE STATE
    lang_choice = st.session_state.get(SessionManager.LANGUAGE, "English")
    T = UI_TEXTS.get(lang_choice, UI_TEXTS["English"])

    # Container for the Hero Field
    with st.container(border=True):
        st.markdown('<div id="hero-card-anchor"></div>', unsafe_allow_html=True)

        # 2-column layout: Main Content (Left) and Controls/Visuals (Right)
        col_main, col_side = st.columns([3, 1])

        with col_main:
            st.markdown(
                '<div class="hero-eyebrow">Executive Demo Experience</div>',
                unsafe_allow_html=True,
            )

            tooltip_html = (
                f'<div class="custom-tooltip-icon inline-tooltip">?<div class="custom-tooltip-box">{info_text}</div></div>'
                if info_text
                else ""
            )
            st.markdown(
                f'<div class="hero-title-container"><div class="hero-title">AI Sales Simulator</div>{tooltip_html}</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="hero-subtitle">
                    {T["hero_subtitle"]}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_side:
            # 2. SYNC LANGUAGE UPON CHANGE
            def sync_language():
                st.session_state[SessionManager.LANGUAGE] = st.session_state[
                    f"{key_prefix}language_selector"
                ]

            # Language Selector on top
            lang_options = ["English", "Spanish", "Portuguese"]
            idx = lang_options.index(lang_choice) if lang_choice in lang_options else 0

            st.selectbox(
                "Select Language",
                lang_options,
                index=idx,
                label_visibility="collapsed",
                key=f"{key_prefix}language_selector",
                on_change=sync_language,
            )

            # --- PERSISTENT MODE SELECTOR ---
            with st.popover(f"{T.get('mode_btn', 'Mode')} ⚙️", use_container_width=True):
                st.markdown(f"**{T.get('mode_btn', 'Mode')} Select**")

                modes = (T["mode_classic_title"], T["mode_live_title"])
                current_mode = st.session_state.get("app_mode", modes[0])

                # 3. FIX MODE RESET ACROSS LANGUAGES
                all_live_strings = [
                    UI_TEXTS["English"]["mode_live_title"],
                    UI_TEXTS["Spanish"]["mode_live_title"],
                    UI_TEXTS["Portuguese"]["mode_live_title"],
                    "Live Mode (Sprint 1 Test)",
                ]

                current_index = 1 if current_mode in all_live_strings else 0

                new_mode = st.radio(
                    "Simulation Mode",
                    modes,
                    index=current_index,
                    label_visibility="collapsed",
                    key=f"{key_prefix}app_mode_radio_internal",
                )

                # Only update and rerun if the actual selection changed
                if new_mode != current_mode:
                    st.session_state.app_mode = new_mode
                    st.rerun()

            # Image below selector with professional spacing
            if img_base64:
                st.markdown(
                    f'<div class="hero-img-box-side"><img src="data:image/png;base64,{img_base64}" class="hero-project-image-side"></div>',
                    unsafe_allow_html=True,
                )

        # Badges below (full width of the field)
        badges_html = "".join(
            [f'<div class="hero-badge">{badge}</div>' for badge in T["hero_badges"]]
        )
        st.markdown(
            f"""
            <div class="hero-badges">
                {badges_html}
            </div>
            """,
            unsafe_allow_html=True,
        )


def section_title(
    title: str, subtitle: Optional[str] = None, info: Optional[str] = None
):
    info_html = ""
    if info:
        info_html = f'<span class="custom-tooltip-icon inline-tooltip">?<span class="custom-tooltip-box">{info}</span></span>'
    subtitle_html = (
        f'<div class="section-title-subtitle">{subtitle}</div>' if subtitle else ""
    )
    html = (
        '<div class="section-title-card">'
        '<div class="section-title-row">'
        f'<div class="section-title-text">{title}</div>'
        f"{info_html}"
        "</div>"
        f"{subtitle_html}"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_metric_strip(company: str, role: str, language: str, T=None):
    company_label = (T["company"] if T and "company" in T else "Company") + ": "
    role_label = (T["role"] if T and "role" in T else "Role") + ": "
    language_label = (T["language"] if T and "language" in T else "Language") + ": "
    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="metric-pill"><span>{company_label}</span><strong>{company}</strong></div>
            <div class="metric-pill"><span>{role_label}</span><strong>{role}</strong></div>
            <div class="metric-pill"><span>{language_label}</span><strong>{language}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_glass_tip(text_value: str):
    st.markdown(f'<div class="glass-tip">{text_value}</div>', unsafe_allow_html=True)


def render_evaluation_card(evaluation: dict, T: dict):
    """
    Renders a single evaluation item as a card with a score-based color scheme.
    """
    rating = evaluation.get("rating", "N/A")

    # Define color scheme based on rating
    if rating == "Meets Expectations":
        border_color = "#1E8E3E"  # Green
        background_color = "rgba(30, 142, 62, 0.05)"
        emoji = "✅"
    elif rating == "Partially Meets Expectations":
        border_color = "#F29900"  # Amber
        background_color = "rgba(242, 153, 0, 0.05)"
        emoji = "⚠️"
    elif rating == "Needs Improvement":
        border_color = "#D93025"  # Red
        background_color = "rgba(217, 48, 37, 0.05)"
        emoji = "❌"
    elif rating == "Auto-Fail":
        border_color = "#D93025"  # Red
        background_color = "rgba(217, 48, 37, 0.1)"
        emoji = "🚫"
    else:  # N/A or other
        border_color = "#DADCE0"  # Grey
        background_color = "rgba(218, 220, 224, 0.1)"
        emoji = "➡️"

    with st.container(border=True):
        st.markdown(
            f"""
            <div style="border-left: 5px solid {border_color}; background-color: {background_color}; padding: 1rem; border-radius: 8px;">
                <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;">{emoji} {evaluation["parameter"]}</div>
                <div style="font-style: italic; color: {border_color}; margin-bottom: 1rem;">{T.get("rating_label", "Rating")}: {rating}</div>
                
                <div style="margin-bottom: 0.75rem;">
                    <strong style="font-size: 0.9rem;">{T.get("evidence_label", "Evidence")}:</strong>
                    <div style="font-size: 0.9rem; color: var(--text-secondary);">{evaluation.get("evidence", "No evidence provided.")}</div>
                </div>
                
                <div>
                    <strong style="font-size: 0.9rem;">{T.get("improvement_label", "Improvement Tip")}:</strong>
                    <div style="font-size: 0.9rem; color: var(--text-secondary);">{evaluation.get("improvement_tip", "No tip provided.")}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
