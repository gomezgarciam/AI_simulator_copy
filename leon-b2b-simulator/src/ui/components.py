import base64
from pathlib import Path
from typing import Optional

import streamlit as st

def find_logo_path() -> Optional[str]:
    candidates = [
        "1.png",
        "logo.png",
        "assets/1.png",
        "assets/logo.png",
        "./1.png",
        "./logo.png",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None



def render_header(show_logo: bool = True, info_text: str = ""):
    logo_html = ""

    if show_logo:
        logo_path = find_logo_path()
        tooltip = info_text or "This simulator recreates enterprise sales roleplays with Alex and pairs them with a live assistant grounded in FY26 plays, battle cards, and any PDF you upload."
        tooltip_html = f'<span class="custom-tooltip-icon">?<span class="custom-tooltip-box">{tooltip}</span></span>'
        if logo_path:
            try:
                with open(logo_path, "rb") as logo_file:
                    encoded_logo = base64.b64encode(logo_file.read()).decode("utf-8")
                logo_html = f'<div class="hero-logo-shell">{tooltip_html}<img class="hero-inline-logo" src="data:image/png;base64,{encoded_logo}" alt="Logo" /></div>'
            except Exception:
                logo_html = f'<div class="hero-logo-shell">{tooltip_html}<div class="hero-inline-logo-fallback">GCP</div></div>'
        else:
            logo_html = f'<div class="hero-logo-shell">{tooltip_html}<div class="hero-inline-logo-fallback">GCP</div></div>'

    st.markdown(
        f"""
<div class="hero-card">
  <div class="hero-grid">
    <div class="hero-copy">
      <div class="hero-eyebrow">Executive Demo Experience</div>
      <div class="hero-title">AI Sales Simulator</div>
      <div class="hero-subtitle">
        A premium roleplay environment for enterprise discovery, objection handling, and positioning — powered by AI buyer simulation and official FY26 sales knowledge.
      </div>
      <div class="hero-badges">
        <span class="hero-badge">Multilingual</span>
        <span class="hero-badge">Voice Enabled</span>
        <span class="hero-badge">FY26 Plays</span>
        <span class="hero-badge">Battlecards</span>
        <span class="hero-badge">Live Coaching</span>
      </div>
    </div>
    <div class="hero-visual">{logo_html}</div>
  </div>
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
    company_label = T["company"] if T and "company" in T else "Company"
    role_label = T["role"] if T and "role" in T else "Role"
    language_label = T["language"] if T and "language" in T else "Language"
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
