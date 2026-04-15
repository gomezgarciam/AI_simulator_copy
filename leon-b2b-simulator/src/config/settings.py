import os

APP_NAME = "AI Sales Simulator"
PAGE_TITLE = "Google BDR Simulator - Alex"
PAGE_ICON = "🎙️"

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "b2b-agent-485013")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

MODEL_ID = os.getenv("MODEL_ID", "gemini-2.5-flash")

INTERNAL_DOCS_BUCKET = os.getenv("INTERNAL_DOCS_BUCKET", "bdr-simulator-internal-docs")
INTERNAL_DOCS_PREFIX = os.getenv("INTERNAL_DOCS_PREFIX", "Plays/")

ASSISTANT_TOP_K = int(os.getenv("ASSISTANT_TOP_K", "4"))
ROLEPLAY_HISTORY_MAX_TURNS = int(os.getenv("ROLEPLAY_HISTORY_MAX_TURNS", "12"))
PDF_SUMMARY_THRESHOLD = int(os.getenv("PDF_SUMMARY_THRESHOLD", "15000"))