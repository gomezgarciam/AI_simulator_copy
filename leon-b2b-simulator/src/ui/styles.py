GLOBAL_STYLES = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Google+Sans:wght@400;500;700&display=swap');

        :root {
            /* Light Theme - Google Professional */
            --google-blue: #1a73e8;
            --google-blue-hover: #1765cc;
            --bg-color: #f8f9fa;
            --surface-color: #ffffff;
            --surface-variant: rgba(255, 255, 255, 0.7);
            --text-primary: #202124;
            --text-secondary: #5f6368;
            --border-color: #dadce0;
            --card-shadow: 0 1px 3px rgba(60,64,67,0.1);
            --faded-gradient: radial-gradient(circle at top left, rgba(26, 115, 232, 0.08), transparent 40%),
                              radial-gradient(circle at top right, rgba(138, 180, 248, 0.08), transparent 40%),
                              linear-gradient(180deg, #f8f9fa 0%, #eef3fb 100%);
            --faded-blue: rgba(26, 115, 232, 0.07);
            --assistant-accent: #1e3a8a;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                /* Dark Theme - Google Material */
                --google-blue: #8ab4f8;
                --google-blue-hover: #aecbfa;
                --bg-color: #202124;
                --surface-color: #2d2e31;
                --surface-variant: rgba(60, 64, 67, 0.7);
                --text-primary: #e8eaed;
                --text-secondary: #9aa0a6;
                --border-color: #444746;
                --card-shadow: 0 4px 6px rgba(0,0,0,0.3);
                --faded-gradient: radial-gradient(circle at top left, rgba(26, 115, 232, 0.12), transparent 40%),
                                  radial-gradient(circle at top right, rgba(138, 180, 248, 0.12), transparent 40%),
                                  linear-gradient(180deg, #202124 0%, #17181a 100%);
                --faded-blue: rgba(138, 180, 248, 0.15);
                --assistant-accent: #3c4043;
            }
        }

        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Roboto', 'Google Sans', sans-serif;
            background-color: var(--bg-color) !important;
            color: var(--text-primary);
        }

        /* App-wide Faded Background */
        .stApp {
            background: var(--faded-gradient) !important;
        }

        .main .block-container {
            max-width: 1400px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        /* The Hero "Field" Container - Professional Faded Blue Background */
        [data-testid="stVerticalBlock"]:has(#hero-card-anchor),
        [data-testid="stVerticalBlockBorderWrapper"]:has(#hero-card-anchor) {
            background-color: var(--faded-blue) !important;
            background-image: linear-gradient(145deg, var(--faded-blue) 0%, transparent 80%) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 28px !important;
            padding: 2.5rem 3.5rem !important;
            margin-bottom: 2.5rem !important;
            box-shadow: none !important;
            overflow: visible !important;
        }
        
        /* Internal Padding for the Hero Field */
        [data-testid="stVerticalBlockBorderWrapper"]:has(#hero-card-anchor) > div {
            padding: 0 !important;
        }

        /* Hero Title and Tooltip Alignment */
        .hero-title-container {
            display: flex;
            align-items: center;
            gap: 1.2rem;
            margin: 0.8rem 0 !important;
        }

        .hero-title {
            font-family: 'Google Sans', 'Roboto', sans-serif;
            font-size: clamp(2.2rem, 5vw, 3.8rem);
            font-weight: 700;
            color: var(--text-primary) !important;
            margin: 0 !important;
            line-height: 1.1;
            letter-spacing: -0.02em;
        }

        .hero-eyebrow {
            color: var(--google-blue) !important;
            font-weight: 600;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-bottom: 0.5rem;
        }

        .hero-subtitle {
            font-size: 1.1rem;
            color: var(--text-secondary) !important;
            max-width: 900px;
            margin: 1.8rem 0 !important;
            line-height: 1.7;
        }

        .hero-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-top: 1.5rem;
            overflow: visible !important;
        }

        .hero-badge {
            background-color: var(--surface-color) !important;
            border: 1px solid var(--border-color) !important;
            padding: 0.6rem 1.2rem !important;
            border-radius: 12px !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
            color: var(--text-primary) !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            white-space: nowrap;
        }

        /* Fixed Tooltip Styles */
        .custom-tooltip-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 26px;
            height: 26px;
            border-radius: 50%;
            background-color: var(--surface-variant);
            color: var(--text-primary);
            font-size: 0.9rem;
            font-weight: 700;
            cursor: help;
            position: relative;
            border: 1px solid var(--border-color);
            transition: all 0.2s ease;
        }

        .custom-tooltip-box {
            position: absolute;
            top: calc(100% + 12px);
            right: 0;
            background-color: #202124 !important;
            color: #ffffff !important;
            padding: 14px 18px;
            border-radius: 12px;
            font-size: 0.88rem;
            width: 320px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.25);
            opacity: 0;
            visibility: hidden;
            transition: all 0.2s ease;
            z-index: 1000;
            white-space: normal;
            line-height: 1.5;
        }

        .custom-tooltip-icon:hover {
            background-color: var(--google-blue);
            color: white;
            border-color: var(--google-blue);
        }

        .custom-tooltip-icon:hover .custom-tooltip-box {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        /* Generic Container Fixes */
        [data-testid="stVerticalBlockBorderWrapper"], .glass-panel, .section-title-card {
            background-color: var(--surface-color) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            box-shadow: var(--card-shadow) !important;
            padding: 1.5rem !important;
            color: var(--text-primary) !important;
        }

        /* Interaction Elements */
        .stButton button, .stForm button {
            background-color: var(--google-blue) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            padding: 0.5rem 1.5rem !important;
            transition: background-color 0.2s;
        }

        .stButton button:hover {
            background-color: var(--google-blue-hover) !important;
            box-shadow: 0 1px 3px 0 rgba(60,64,67,.3), 0 4px 8px 3px rgba(60,64,67,.15) !important;
        }

        /* Inputs */
        .stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {
            background-color: var(--surface-color) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }

        /* Chat Messages */
        [data-testid="stChatMessage"] {
            background-color: var(--surface-variant) !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 1rem !important;
        }

        [data-testid="stChatMessage"] p {
            color: var(--text-primary) !important;
        }

        /* Metric Pllls */
        .metric-pill {
            background-color: var(--surface-variant);
            padding: 0.75rem 1rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }

        .metric-pill span {
            color: var(--text-secondary);
            font-size: 0.75rem;
            font-weight: 500;
        }

        .metric-pill strong {
            color: var(--text-primary);
        }

        /* Assistant Panel */
        .assistant-badge {
            background-color: var(--assistant-accent);
            color: white;
            border-radius: 8px;
            padding: 1rem;
        }

        /* Tooltip Overrides */
        .custom-tooltip-icon {
            background-color: var(--surface-variant);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }

        /* Specific fix for file uploader */
        .stFileUploader section {
            background-color: var(--surface-variant) !important;
            border: 1px dashed var(--border-color) !important;
            border-radius: 8px !important;
        }

        /* Hide Streamlit elements for cleaner look */
        #MainMenu, footer, header { visibility: hidden; }

        /* Scrollbar Styling */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg-color); }
        ::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--text-secondary); }

    </style>
"""
