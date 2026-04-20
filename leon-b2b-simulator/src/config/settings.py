import os
from dotenv import load_dotenv

# Load local .env file if it exists
load_dotenv(override=True)

APP_NAME = "AI Sales Simulator"
PAGE_TITLE = "Google BDR Simulator - Alex"
PAGE_ICON = "🎙️"

# Configuration variables are strictly sourced from the environment.
# Use a .env file locally to set these without modifying the codebase.
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

MODEL_ID = os.getenv("MODEL_ID", "gemini-2.5-flash")

INTERNAL_DOCS_BUCKET = os.getenv("INTERNAL_DOCS_BUCKET")
INTERNAL_DOCS_PREFIX = os.getenv("INTERNAL_DOCS_PREFIX", "Plays/")

ASSISTANT_TOP_K = int(os.getenv("ASSISTANT_TOP_K", "4"))
ROLEPLAY_HISTORY_MAX_TURNS = int(os.getenv("ROLEPLAY_HISTORY_MAX_TURNS", "12"))
PDF_SUMMARY_THRESHOLD = int(os.getenv("PDF_SUMMARY_THRESHOLD", "15000"))

# Validation to ensure required configuration is present
if not GOOGLE_CLOUD_PROJECT:
    print("WARNING: GOOGLE_CLOUD_PROJECT environment variable is not set.")
if not INTERNAL_DOCS_BUCKET:
    print("WARNING: INTERNAL_DOCS_BUCKET environment variable is not set.")