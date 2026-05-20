
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings managed via Pydantic.
    Environment variables will override these defaults.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # App Metadata
    APP_NAME: str = "AI Sales Simulator"
    PAGE_TITLE: str = "Google BDR Simulator - Alex"
    PAGE_ICON: str = "🎙️"

    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT: str = "b2b-agent-485013"
    GOOGLE_CLOUD_LOCATION: str = "us-central1"

    # AI Models
    MODEL_ID: str = "gemini-2.5-flash"

    # Storage & RAG
    INTERNAL_DOCS_BUCKET: str = "bdr-simulator-internal-docs"
    INTERNAL_DOCS_PREFIX: str = "Plays/"

    # Engine Hyperparameters
    ASSISTANT_TOP_K: int = 4
    ROLEPLAY_HISTORY_MAX_TURNS: int = 12
    PDF_SUMMARY_THRESHOLD: int = 15000

    # BigQuery
    BIGQUERY_DATASET: str = "simulator_data"
    BIGQUERY_TABLE: str = "evaluations"


# Create a singleton instance
settings = Settings()

# For backward compatibility during migration, we also export individual variables
# but the preferred way should be `from src.config.settings import settings`
APP_NAME = settings.APP_NAME
PAGE_TITLE = settings.PAGE_TITLE
PAGE_ICON = settings.PAGE_ICON
GOOGLE_CLOUD_PROJECT = settings.GOOGLE_CLOUD_PROJECT
GOOGLE_CLOUD_LOCATION = settings.GOOGLE_CLOUD_LOCATION
MODEL_ID = settings.MODEL_ID
INTERNAL_DOCS_BUCKET = settings.INTERNAL_DOCS_BUCKET
INTERNAL_DOCS_PREFIX = settings.INTERNAL_DOCS_PREFIX
ASSISTANT_TOP_K = settings.ASSISTANT_TOP_K
ROLEPLAY_HISTORY_MAX_TURNS = settings.ROLEPLAY_HISTORY_MAX_TURNS
PDF_SUMMARY_THRESHOLD = settings.PDF_SUMMARY_THRESHOLD
