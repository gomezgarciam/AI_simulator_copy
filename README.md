# B2B AI Sales Simulator | Enterprise Technical Specification & Architecture

## 1. Executive Summary

The **B2B AI Sales Simulator** is an enterprise-grade, cloud-native conversational platform designed to simulate high-stakes B2B sales discovery calls and negotiations. Leveraging advanced Large Language Models (LLMs) via Google Cloud Vertex AI, multi-modal audio processing, and real-time streaming architectures, the platform provides realistic roleplay training and automated, rubric-driven evaluations (such as MEDPICC, BANT, and customized sales frameworks) for modern sales professionals.

## 2. System Architecture

The application is architected as a microservices-based, cloud-native solution deployed on **Google Cloud Platform (GCP)**. It supports two distinct operational modes: **Assisted Mode** (text-based interactions via Streamlit integrated with HTTP microservices) and **Live Mode** (low-latency, bidirectional audio/text streaming via WebSockets and custom React components).

### High-Level Architectural Flow

```
+---------------------------------------------------------------------------------------------------+
|                                      GOOGLE CLOUD PLATFORM                                        |
|                                                                                                   |
|  +--------------------+      +---------------------------------+      +------------------------+  |
|  |   FRONTEND UI      |      |     WEBSOCKET & API LAYER       |      |    SIMULATION CORES    |  |
|  |  (Streamlit /      | ---> |      (FastAPI Server &          | ---> |  (Assistant Engine,    |  |
|  |   React Frontend)  |      |       Cloud Memorystore Redis)  |      |   Roleplay Engine, RAG)|  |
|  +--------------------+      +---------------------------------+      +------------------------+  |
|            |                                  |                                   |               |
|            +----------------------------------+-----------------------------------+               |
|                                               |                                                   |
|                                               v                                                   |
|                              +---------------------------------+                                  |
|                              |      AI & SPEECH SERVICES       |                                  |
|                              |  (Google Cloud Speech-to-Text,  |                                  |
|                              |   Vertex AI Gemini 2.5/Pro)     |                                  |
|                              +---------------------------------+                                  |
|                                               |                                                   |
|                                               v                                                   |
|                              +---------------------------------+                                  |
|                              |    ANALYTICS & PERSISTENCE      |                                  |
|                              |   (BigQuery & Looker Studio)    |                                  |
|                              +---------------------------------+                                  |
+---------------------------------------------------------------------------------------------------+
```

## 3. Core Services & Technical Stack

The system is modularized into dedicated microservices, each handling specific domain responsibilities:

### 3.1 Frontend & User Interface Layer
* **Streamlit Framework (`app.py`, `src/ui/`)**: Powers the core interactive web application, handling session state management, chat rendering, scorecards, and parameter configurations.
* **Custom React Audio Component (`components/mic_recorder/`)**: Built with TypeScript and the Web Audio API to capture raw microphone streams, handle audio chunking, and facilitate real-time bi-directional voice streaming.

### 3.2 API & Communication Services
* **FastAPI WebSocket Server (`src/api/live_mode_backend.py`)**: Manages real-time bidirectional communication channels for Live Mode, synchronizing audio chunks, transcriptions, and engine responses with sub-second latency.
* **Global External Load Balancer**: Directs traffic securely across Cloud Run instances, managing SSL termination and WebSocket protocol upgrades.

### 3.3 Intelligence & Simulation Engines (`src/engines/`)
* **Coordinator Engine (`coordinator.py`)**: Orchestrates message flow between user inputs, RAG context retrieval, prompt management, and evaluation triggers.
* **Assistant Engine (`assistant_engine.py`)**: Provides real-time guidance, sales plays suggestions, and dynamic feedback during active sessions.
* **Roleplay Engine (`roleplay_engine.py`)**: Emulates persona-driven buyer behaviors (e.g., CTO, Procurement Director, Skeptical Buyer) using customized agentic prompts (`src/prompts/roleplay.py`).

### 3.4 Speech & Audio Processing (`src/services/`)
* **Audio Service & FFmpeg Pipeline (`audio_service.py`)**: Handles server-side audio transcoding, chunk decoding, and noise reduction.
* **Speech Service (`speech_service.py`)**: Integrates directly with the **Google Cloud Speech-to-Text API** for real-time streaming audio transcription.

### 3.5 Evaluation & RAG Pipeline (`src/evaluation/`, `src/rag/`)
* **Scoring & Rubric Engine (`scoring_engine.py`, `rubric_engine.py`)**: Evaluates conversation transcripts against structured criteria (e.g., MEDPICC, BANT) utilizing JSON-structured LLM outputs.
* **RAG Context Builder (`context_builder.py`, `retrieval.py`)**: Chunks, embeds, and retrieves enterprise product documentation and sales playbooks to ground LLM responses in factual data.

### 3.6 Data Persistence & Analytics (`src/services/db_service.py`)
* **Cloud Memorystore (Redis)**: Manages active session caching, user states, and real-time transcript logs.
* **BigQuery Integration**: Archives historical session transcripts, evaluation scores, and metadata for long-term analytics and reporting.
* **Looker Studio Dashboards**: Consumes BigQuery datasets via `JSON_EXTRACT()` queries to render executive sales performance analytics and team scorecards.

## 4. Deployment & DevOps

* **Containerization**: Fully containerized using a multi-stage `Dockerfile` supporting Python runtime dependencies, FFmpeg binaries, and Node.js frontend builds.
* **Orchestration**: Deployed on Google Cloud Run with NGINX reverse-proxy configurations (`nginx.conf`, `nginx_master.conf`) managing routing between Streamlit and FastAPI backends.
* **Environment Configuration**: Configured via `.env` parameters (`.env.example`) controlling Vertex AI endpoints, GCP project IDs, and Redis connection strings.

## 5. Getting Started & Development

1. **Clone the repository and configure environment variables:**
   ```bash
   cp .env.example .env
   # Populate necessary GCP credentials and API keys
   ```

2. **Run tests to verify backend logic:**
   ```bash
   bash scripts/run_tests.sh
   ```

3. **Start the development server:**
   ```bash
   bash start_dev.sh
   ```
