import base64
import base64
from pathlib import Path
from typing import Optional

import streamlit as st

def get_image_base64(path: str) -> Optional[str]:
    try:
        p = Path(path)
        if p.exists():
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        return None
    return None

def render_header(info_text: str = ""):
    # Look for the project image in assets
    img_base64 = get_image_base64("assets/project_hero.png")

    # Container for the Hero Field
    with st.container(border=True):
        st.markdown('<div id="hero-card-anchor"></div>', unsafe_allow_html=True)
        
        # 2-column layout: Main Content (Left) and Controls/Visuals (Right)
        col_main, col_side = st.columns([3, 1])
        
        with col_main:
            st.markdown('<div class="hero-eyebrow">Executive Demo Experience</div>', unsafe_allow_html=True)
            
            tooltip_html = f'<div class="custom-tooltip-icon inline-tooltip">?<div class="custom-tooltip-box">{info_text}</div></div>' if info_text else ""
            st.markdown(f'<div class="hero-title-container"><div class="hero-title">AI Sales Simulator</div>{tooltip_html}</div>', unsafe_allow_html=True)
            
            st.markdown(
                f"""
                <div class="hero-subtitle">
                    A premium roleplay environment for enterprise discovery, objection handling, and positioning — powered by AI buyer simulation and official FY26 sales knowledge.
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with col_side:
            # Language Selector on top
            st.selectbox("Select Language", ["English", "Spanish", "Portuguese"], label_visibility="collapsed", key="language_selector")
            
            # Image below selector with professional spacing
            if img_base64:
                st.markdown(
                    f'<div class="hero-img-box-side"><img src="data:image/png;base64,{img_base64}" class="hero-project-image-side"></div>',
                    unsafe_allow_html=True
                )

        # Badges below (full width of the field)
        st.markdown(
            """
            <div class="hero-badges">
                <div class="hero-badge">Multilingual</div>
                <div class="hero-badge">Voice Enabled</div>
                <div class="hero-badge">FY26 Plays</div>
                <div class="hero-badge">Battlecards</div>
                <div class="hero-badge">Live Coaching</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def section_title(title: str, subtitle: Optional[str] = None, info: Optional[str] = None):
    info_html = ""
    if info:
        info_html = f'<span class="custom-tooltip-icon inline-tooltip">?<span class="custom-tooltip-box">{info}</span></span>'
    subtitle_html = f'<div class="section-title-subtitle">{subtitle}</div>' if subtitle else ''
    html = (
        '<div class="section-title-card">'
        '<div class="section-title-row">'
        f'<div class="section-title-text">{title}</div>'
        f'{info_html}'
        '</div>'
        f'{subtitle_html}'
        '</div>'
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
