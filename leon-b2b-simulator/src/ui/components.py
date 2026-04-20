import base64
from pathlib import Path
from typing import Optional

import streamlit as st

def render_header(info_text: str = ""):
    # We use a container to wrap the entire hero card
    with st.container(border=True):
        # We place a hidden anchor that tells our CSS to style this container as the Hero Card
        st.markdown('<div id="hero-card-anchor"></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="hero-eyebrow">Executive Demo Experience</div>', unsafe_allow_html=True)
        
        # Title Row: Title, Tooltip, and Language Selector
        title_col, select_col = st.columns([4, 1])
        
        with title_col:
            tooltip_html = ""
            if info_text:
                tooltip_html = f'<div class="custom-tooltip-icon inline-tooltip">?<div class="custom-tooltip-box">{info_text}</div></div>'
            
            st.markdown(
                f"""
                <div class="hero-title-container">
                    <div class="hero-title">AI Sales Simulator</div>
                    {tooltip_html}
                </div>
                """, 
                unsafe_allow_html=True
            )
            
        with select_col:
            st.selectbox(
                "Select Language",
                ["English", "Spanish", "Portuguese"],
                label_visibility="collapsed",
                key="language_selector",
            )
        
        # Subtitle and Badges with professional spacing
        st.markdown(
            f"""
            <div class="hero-subtitle">
                A premium roleplay environment for enterprise discovery, objection handling, and positioning — powered by AI buyer simulation and official FY26 sales knowledge.
            </div>
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
