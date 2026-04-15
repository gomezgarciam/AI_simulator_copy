GLOBAL_STYLES = """

    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.08), transparent 28%),
                radial-gradient(circle at top right, rgba(99, 102, 241, 0.08), transparent 30%),
                linear-gradient(180deg, #f6f8fc 0%, #eef3fb 100%);
        }

        .main .block-container {
            max-width: 1480px;
            padding-top: 1.1rem;
            padding-bottom: 1.25rem;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stToolbar"] {
            right: 1rem;
        }

        .hero-card {
            position: relative;
            overflow: hidden;
            background: linear-gradient(135deg, #081224 0%, #0d1b3d 42%, #1c2f6b 100%);
            border: 1px solid rgba(255,255,255,0.09);
            border-radius: 30px;
            padding: 2rem 2rem;
            color: white;
            margin-bottom: 1.15rem;
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.18);
        }

        .hero-card::before {
            content: "";
            position: absolute;
            inset: auto -10% -50% auto;
            width: 420px;
            height: 420px;
            border-radius: 999px;
            background: radial-gradient(circle, rgba(96, 165, 250, 0.22), transparent 65%);
        }

        .hero-grid {
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 1.5rem;
            align-items: center;
        }

        .hero-copy { position: relative; z-index: 2; }
        .hero-eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.42rem 0.8rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.09);
            border: 1px solid rgba(255,255,255,0.12);
            color: rgba(255,255,255,0.86);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.8rem;
        }

        .hero-title {
            font-size: clamp(3rem, 4.6vw, 4.55rem);
            font-weight: 900;
            line-height: 0.96;
            margin-bottom: 0.7rem;
            letter-spacing: -0.05em;
        }

        .hero-subtitle {
            font-size: 1.08rem;
            line-height: 1.65;
            color: rgba(255,255,255,0.84);
            max-width: 860px;
            margin-bottom: 1.15rem;
        }

        .hero-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.65rem;
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.55rem 0.95rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.15);
            font-size: 0.88rem;
            font-weight: 700;
            color: white;
            backdrop-filter: blur(8px);
        }

        .hero-visual {
            position: relative;
            z-index: 2;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .hero-logo-shell {
            position: relative;
            overflow: visible !important;
            width: 132px;
            min-width: 132px;
            height: 132px;
            border-radius: 28px;
            background: rgba(255,255,255,0.96);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.6), 0 20px 40px rgba(0,0,0,0.18);
            overflow: visible !important;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .hero-logo-shell .custom-tooltip-icon {
            position: absolute;
            top: 10px;
            left: 10px;
        }

        .hero-logo-shell .custom-tooltip-box {
            left: 0;
            right: auto;
        }

        .assistant-card .custom-tooltip-box {
            right: 0;
            left: auto;
        }

        .hero-inline-logo {
            width: 88px;
            height: auto;
            object-fit: contain;
        }

        .hero-inline-logo-fallback {
            font-size: 1.2rem;
            font-weight: 800;
            color: #0B1220;
            letter-spacing: 0.08em;
        }

        .custom-tooltip-icon {
            position: relative;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            border-radius: 999px;
            background: rgba(226,232,240,0.92);
            color: #0f172a;
            border: 1px solid #cbd5e1;
            font-size: 0.9rem;
            font-weight: 800;
            cursor: help;
            z-index: 5;
        }

        .custom-tooltip-icon.inline-tooltip {
            position: relative;
        }

        .custom-tooltip-box {
            position: absolute;
            top: calc(100% + 10px);
            right: 0;
            max-width: min(420px, calc(100vw - 40px));
            white-space: normal;
            overflow-wrap: anywhere;
            z-index: 99999;
            width: 420px;
            background: #0f172a;
            color: white;
            border-radius: 14px;
            padding: 0.85rem 0.95rem;
            font-size: 0.82rem;
            line-height: 1.55;
            box-shadow: 0 18px 34px rgba(15,23,42,0.22);
            opacity: 0;
            visibility: hidden;
            transform: translateY(4px);
            transition: all 0.16s ease;
            text-align: left;
        }

        .custom-tooltip-icon:hover .custom-tooltip-box {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        .info-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 24px;
            height: 24px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 800;
            cursor: help;
        }


        .language-bar {
            background: rgba(255,255,255,0.78);
            border: 1px solid rgba(148,163,184,0.18);
            box-shadow: 0 10px 30px rgba(15,23,42,0.05);
            border-radius: 24px;
            padding: 1rem 1.2rem 0.65rem 1.2rem;
            margin-bottom: 1rem;
            backdrop-filter: blur(14px);
        }

        .language-bar-title {
            font-size: 0.78rem;
            font-weight: 800;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.4rem;
        }

        .section-title-card,
        .glass-panel,
        [data-testid="stForm"],
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255,255,255,0.78) !important;
            border: 1px solid rgba(148,163,184,0.16) !important;
            border-radius: 24px !important;
            box-shadow: 0 12px 34px rgba(15, 23, 42, 0.06) !important;
            backdrop-filter: blur(14px);
        }

        .section-title-card {
            padding: 1rem 1.1rem;
            margin-bottom: 0.85rem;
        }

        .section-title-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem;
        }

        .section-title-text {
            font-size: 1.08rem;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: -0.02em;
        }

        .section-title-subtitle {
            font-size: 0.92rem;
            color: #64748b;
            margin-top: 0.35rem;
            line-height: 1.5;
        }

        .info-icon {
            background: #e2e8f0;
            color: #1e293b;
            border: 1px solid #cbd5e1;
            flex-shrink: 0;
        }

        .section-kicker {
            font-size: 0.75rem;
            font-weight: 800;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.11em;
            margin-top: 0.5rem;
            margin-bottom: 0.55rem;
        }

        .scenario-box,
        .assistant-badge,
        .metric-strip,
        .glass-tip {
            border-radius: 20px;
        }

        .scenario-box {
            background: linear-gradient(180deg, rgba(248,250,252,0.96), rgba(241,245,249,0.96));
            border: 1px solid rgba(148,163,184,0.18);
            padding: 1.15rem;
            line-height: 1.8;
            color: #334155;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
        }

        .assistant-badge {
            background: linear-gradient(135deg, #0b1220, #172554 60%, #1e3a8a 100%);
            padding: 1rem 1rem;
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 0.8rem;
            box-shadow: 0 14px 28px rgba(15,23,42,0.12);
        }

        .assistant-badge-title {
            font-weight: 800;
            font-size: 0.95rem;
            color: white;
        }

        .assistant-badge-desc {
            font-size: 0.84rem;
            color: #dbeafe;
            margin-top: 0.35rem;
            line-height: 1.52;
        }

        .small-muted {
            font-size: 0.95rem;
            color: #64748b;
            line-height: 1.7;
        }

        .session-caption {
            font-size: 0.92rem;
            color: #64748b;
            margin-top: -0.1rem;
            margin-bottom: 0.8rem;
        }

        .metric-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin-bottom: 0.95rem;
        }

        .metric-pill {
            min-width: 160px;
            flex: 1 1 0;
            background: rgba(255,255,255,0.78);
            border: 1px solid rgba(148,163,184,0.18);
            padding: 0.9rem 1rem;
            box-shadow: 0 10px 26px rgba(15,23,42,0.05);
            border-radius: 18px;
        }

        .metric-pill span {
            display: block;
            font-size: 0.72rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #64748b;
            font-weight: 800;
            margin-bottom: 0.18rem;
        }

        .metric-pill strong {
            font-size: 1rem;
            color: #0f172a;
            font-weight: 800;
        }

        .glass-tip {
            background: rgba(255,255,255,0.74);
            border: 1px solid rgba(148,163,184,0.18);
            padding: 0.8rem 0.95rem;
            color: #475569;
            line-height: 1.6;
            margin-bottom: 0.8rem;
            box-shadow: 0 8px 24px rgba(15,23,42,0.04);
        }

        .assistant-panel {
            position: sticky;
            top: 1rem;
        }

        .stButton button,
        .stForm button {
            background: linear-gradient(135deg, #0b1220 0%, #182a63 100%) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255,255,255,0.06) !important;
            border-radius: 16px !important;
            font-weight: 800 !important;
            min-height: 50px !important;
            box-shadow: 0 14px 24px rgba(15, 23, 42, 0.16) !important;
            transition: all 0.18s ease-in-out !important;
        }

        .stButton button:hover,
        .stForm button:hover {
            transform: translateY(-1px);
            filter: brightness(1.06);
        }

        .stButton button p,
        .stForm button p {
            color: #ffffff !important;
            font-weight: 800 !important;
        }

        .stTextInput input,
        .stTextArea textarea,
        div[data-baseweb="select"] > div,
        .stFileUploader section,
        .stAudioInput > div {
            background: rgba(255,255,255,0.92) !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 18px !important;
            box-shadow: inset 0 1px 2px rgba(15,23,42,0.02) !important;
        }

        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder {
            color: #94a3b8 !important;
            opacity: 1 !important;
        }

        div[data-baseweb="select"] * {
            color: #0f172a !important;
        }

        div[role="listbox"] {
            background: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 16px !important;
            box-shadow: 0 20px 40px rgba(15,23,42,0.12) !important;
        }

        div[role="option"] {
            color: #0f172a !important;
        }

        div[role="option"][aria-selected="true"] {
            background: #eef2ff !important;
        }

        .stFileUploader small,
        .stFileUploader span,
        .stFileUploader button {
            color: #0f172a !important;
        }

        [data-testid="stChatMessage"] {
            background: rgba(255,255,255,0.62);
            border: 1px solid rgba(148,163,184,0.14);
            border-radius: 18px;
            padding: 0.35rem 0.4rem;
            margin-bottom: 0.65rem;
        }

        [data-testid="stAlert"] {
            border-radius: 18px !important;
            border: 1px solid rgba(148,163,184,0.15) !important;
        }

        [data-testid="stCaptionContainer"] p, .stCaption {
            color: #64748b !important;
        }


        div[data-testid="stWidgetLabel"] p,
        div[data-testid="stWidgetLabel"] label,
        .stSelectbox label,
        .stTextInput label,
        .stTextArea label,
        .stFileUploader label,
        .stAudioInput label {
            color: #0f172a !important;
            font-weight: 600 !important;
        }

        .stAudioInput [data-testid="stWidgetLabel"] p,
        .stFileUploader [data-testid="stWidgetLabel"] p {
            color: #0f172a !important;
        }

        @media (max-width: 1100px) {
            .hero-grid { grid-template-columns: 1fr; }
            .hero-visual { justify-content: flex-start; }
        }
    
        .tooltip-bubble {
            position: absolute;
            z-index: 9999 !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            overflow: visible !important;
        }

        .assistant-card,
        .hero-card,
        .section-shell {
            overflow: visible !important;
        }

        .stButton button {
            color: #ffffff !important;
        }

        .stFileUploader button,
        .stFileUploader button * {
            color: #111827 !important;
        }

        .stFileUploader button {
            background: #e5e7eb !important;
            border: 1px solid #d1d5db !important;
        }

    
        /* Fix assistant/roleplay chat text visibility */
        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] div,
        [data-testid="stChatMessageContent"] p,
        [data-testid="stChatMessageContent"] div,
        .stChatMessage p,
        .stChatMessage div {
            color: #0f172a !important;
        }

        /* Tooltip bubble: avoid clipping and allow wrapping */
        .tooltip-bubble {
            position: absolute;
            z-index: 99999 !important;
            max-width: 520px !important;
            min-width: 320px !important;
            width: max-content !important;
            white-space: normal !important;
            line-height: 1.45 !important;
            word-break: break-word !important;
            overflow-wrap: anywhere !important;
            box-sizing: border-box !important;
            padding: 18px 22px !important;
        }

        .tooltip-bubble p,
        .tooltip-bubble div,
        .tooltip-bubble span {
            white-space: normal !important;
            word-break: break-word !important;
            overflow-wrap: anywhere !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stChatMessage"],
        [data-testid="stChatMessageContent"],
        .assistant-card,
        .hero-card,
        .section-shell {
            overflow: visible !important;
        }

    
        .hero-card,
        .hero-visual,
        .assistant-card,
        .section-shell,
        .section-title-card,
        div[data-testid="stVerticalBlockBorderWrapper"] {
            overflow: visible !important;
        }

    
        .hero-card,
        .hero-grid,
        .hero-visual,
        .hero-logo-shell,
        
        
        
        
        div[data-testid="stVerticalBlockBorderWrapper"] {
            overflow: visible !important;
        }

        .hero-logo-shell .custom-tooltip-box {
            left: auto !important;
            right: 0 !important;
            top: calc(100% + 12px) !important;
            width: 420px !important;
            max-width: min(420px, calc(100vw - 40px)) !important;
            z-index: 99999 !important;
        }

        .custom-tooltip-box {
            position: absolute !important;
            padding: 16px 18px !important;
            border-radius: 16px !important;
            background: linear-gradient(135deg, #0f172a, #1e3a8a) !important;
            color: #ffffff !important;
            font-size: 14px !important;
            line-height: 1.5 !important;
            white-space: normal !important;
            overflow-wrap: break-word !important;
            box-shadow: 0 20px 40px rgba(0,0,0,0.30) !important;
            opacity: 0;
            visibility: hidden;
            transform: translateY(4px);
            transition: all 0.16s ease;
        }

        .custom-tooltip-icon:hover .custom-tooltip-box {
            opacity: 1 !important;
            visibility: visible !important;
            transform: translateY(0) !important;
        }

    
        html, body, [data-testid="stAppViewContainer"], .stApp {
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }

    </style>
"""