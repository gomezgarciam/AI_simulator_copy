# CONTEXT.md

## 1. System Overview

This application is a sophisticated B2B sales roleplaying simulator designed to train Business Development Representatives (BDRs). It leverages a suite of Google Cloud AI services to create an interactive, voice-driven learning experience.

The core functionality allows a user to simulate a sales call with "Alex," an AI persona whose role (e.g., CTO, CFO) and company are configurable. The user interacts with Alex using their voice. The application's workflow is as follows:

1.  **Voice Input:** The user records their sales pitch.
2.  **Speech-to-Text:** The audio is transcribed into text using the Google Cloud Speech-to-Text API.
3.  **AI Roleplay:** The transcribed text is sent as a prompt to a Google Gemini model. The model is guided by a detailed system prompt that defines Alex's personality as an impatient but professional executive who is skeptical of generic pitches.
4.  **Business Logic Evaluation:** The AI's primary goal is to evaluate the BDR's ability to articulate the specific business value of Google Cloud Platform (GCP) services. The "winning condition" is for the user to explain the implementation and benefits of at least three distinct GCP services.
5.  **Text-to-Speech:** The AI's generated response is converted back into audio using the Google Cloud Text-to-Speech API.
6.  **Feedback Loop:** When the simulation ends, the AI generates a structured feedback table, rating the user's performance across several categories and providing a final summary.

The application is multilingual, supporting English, Spanish, and Portuguese for both the UI and the AI interaction.

## 2. Architecture & Tech Stack

The application is built entirely on a Python stack, designed for rapid development and deployment.

-   **Language:** Python 3.9
-   **Web Framework:** Streamlit, used to create the interactive web-based user interface.
-   **Core AI & Cloud Services:**
    -   **`google-genai`:** Client library for the Gemini Large Language Model (`gemini-1.5-flash`), which powers the AI's conversational logic.
    -   **`google-cloud-speech`:** Used for high-accuracy voice transcription.
    -   **`google-cloud-texttospeech`:** Used to synthesize natural-sounding voice responses for the AI persona.
-   **Audio Processing:**
    -   **`pydub`:** A utility for handling audio format conversions, essential for preparing the user's recorded audio for the Speech-to-Text API. `ffmpeg` is a required system dependency for this library.
-   **Data Handling:**
    -   **`pandas`:** Used to structure and display the final feedback report in a clean, readable table format.

## 3. Infrastructure & Deployment

The architecture is designed for a serverless, container-based deployment on Google Cloud Platform.

-   **Deployment Target:** Google Cloud Run, which provides a scalable, managed environment for running containers.
-   **Containerization:** The application is packaged as a Docker image. The `Dockerfile` is configured to:
    -   Use a lightweight `python:3.9-slim` base image.
    -   Install necessary system dependencies, notably `ffmpeg`.
    -   Install all Python packages from `requirements.txt`.
    -   Run the Streamlit application, correctly configured to listen on the port provided by Cloud Run (`$PORT`).
-   **GCP Environment:** The application is hardcoded to align with the specified deployment environment:
    -   **Project ID:** `b2b-agent-485013`
    -   **Region:** `us-central1`
    -   **Cloud Run Service:** The setup is consistent with a service named `simulator-b2b`.

## 4. Project Structure

The codebase is organized into a few key files, reflecting a typical Streamlit application structure.

```
/
├── app.py                  # Main application entry point: UI, state management, and API orchestration.
├── prompts.py              # Core business logic: Defines the AI's persona and evaluation criteria.
├── requirements.txt        # Lists all Python package dependencies.
├── Dockerfile              # Instructions for building the production Docker container for Cloud Run.
├── check_models.py         # A utility script for checking available Gemini models.
└── .gcloudignore           # Defines files to be excluded from GCP deployments.
```

-   **`app.py`:** The heart of the application, managing the user interface, session state, and the sequence of calls to Google's AI APIs.
-   **`prompts.py`:** A critical module that encapsulates the simulation's business logic by generating the system prompt for the Gemini model.

## 5. Git Context

This context document reflects the state of the codebase as of the `example-branch` in the `leon-b2b-simulator` repository.
