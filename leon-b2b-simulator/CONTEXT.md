# CONTEXT.md

## 1. System Overview

This application is a sophisticated B2B sales roleplaying simulator designed to train Business Development Representatives (BDRs). It leverages Google Cloud AI services to create an interactive, voice-driven learning experience with a dual-agent architecture.

### Core Experience
1.  **Alex (The Prospect):** An AI persona (CTO, CFO, CEO, etc.) that the user interacts with via voice. Alex is designed to be a realistic, skeptical enterprise stakeholder.
2.  **Sales Assistant (The Coach):** A separate RAG-powered agent available during the simulation to provide real-time coaching, objection handling, or internal product knowledge.

### Workflow
1.  **Voice Input:** User records their sales pitch via Streamlit's audio input.
2.  **Transcription:** Handled by Google Cloud Speech-to-Text.
3.  **Roleplay Engine:** Transcribed text is processed by `gemini-2.5-flash`. Alex responds based on detailed role-specific guidance.
4.  **RAG Knowledge:** The Sales Assistant retrieves context from internal documents (FY26 Plays, battlecards) stored in Google Cloud Storage.
5.  **Text-to-Speech:** Alex's responses are converted back to audio using Google Cloud Text-to-Speech.
6.  **Feedback:** At the end of the session, a structured JSON-based feedback table is generated.

The application is fully multilingual, with deep support for English, Spanish, and Portuguese.

## 2. Architecture & Tech Stack

-   **Language:** Python 3.9+
-   **Frontend:** Streamlit (with custom Glassmorphism CSS styles).
-   **AI Services (Google GenAI SDK & Cloud APIs):**
    -   `google-genai`: Powers the Gemini LLM for roleplay and assistant logic.
    -   `google-cloud-speech`: High-accuracy audio transcription.
    -   `google-cloud-texttospeech`: Natural voice synthesis.
    -   `google-cloud-storage`: Used for RAG knowledge base retrieval.
-   **Data & Document Processing:**
    -   `rag`: Custom implementation for document loading (`pypdf`), chunking, and index-based retrieval.
    -   `pydub`: Audio format conversion (requires `ffmpeg`).
    -   `pandas`: Structuring feedback reports.

## 3. Infrastructure & Deployment

-   **Platform:** Google Cloud Platform (Project: `b2b-agent-485013`, Region: `us-central1`).
-   **Deployment:** Google Cloud Run (Service: `simulator-b2b`).
-   **Containerization:** Docker (`python:3.9-slim` base, includes `ffmpeg` installation).
-   **Storage:** GCS Bucket `bdr-simulator-internal-docs` for internal coaching material.

## 4. Project Structure (Modular src/)

```
/
├── app.py                  # Main entry point, UI orchestration, and state management.
├── requirements.txt        # Project dependencies (streamlit, google-genai, etc.).
├── Dockerfile              # Container configuration for Cloud Run.
├── .gcloudignore           # Exclusions for GCP deployment.
└── src/
    ├── config/
    │   └── settings.py     # Global constants, bucket names, and model IDs.
    ├── engines/
    │   ├── roleplay_engine.py  # Logic for Alex's conversation session.
    │   └── assistant_engine.py # Logic for the RAG-based coaching assistant.
    ├── prompts/
    │   ├── roleplay.py     # System prompts for Alex (CTO/CFO/CEO logic).
    │   └── assistant.py    # System prompts for the Sales Assistant.
    ├── rag/
    │   ├── loader.py       # GCS document loading.
    │   ├── chunking.py     # Text splitting and indexing.
    │   └── context_builder.py # Context assembly for LLM prompts.
    ├── services/
    │   ├── audio_service.py # Pydub utilities.
    │   ├── genai_service.py # Gemini client initialization.
    │   ├── speech_service.py # STT and TTS wrappers.
    │   └── pdf_service.py   # PDF text extraction and summarization.
    ├── ui/
    │   ├── components.py   # Reusable Streamlit UI elements.
    │   ├── styles.py       # Glassmorphism and layout CSS.
    │   └── texts.py        # Multilingual UI strings (EN/ES/PT).
```

## 5. Key Configuration (src/config/settings.py)

The application uses an environment-driven configuration model to ensure project isolation and security.

-   **Environment Management:** Handled via `python-dotenv`.
-   **Required Variables:**
    -   `GOOGLE_CLOUD_PROJECT`: The target GCP Project ID.
    -   `INTERNAL_DOCS_BUCKET`: The GCS bucket containing training materials.
-   **Sensible Defaults:**
    -   `GOOGLE_CLOUD_LOCATION`: `us-central1`.
    -   `MODEL_ID`: `gemini-2.5-flash`.
    -   `INTERNAL_DOCS_PREFIX`: `Plays/`.
    -   `ASSISTANT_TOP_K`: 4.
    -   `ROLEPLAY_HISTORY_MAX_TURNS`: 12.

**Local Setup:** Copy `.env.example` to `.env` and fill in your personal project details.
**Cloud Run / GKE:** Set the corresponding environment variables in the service configuration.

