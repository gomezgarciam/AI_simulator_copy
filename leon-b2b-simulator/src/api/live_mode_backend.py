import asyncio
import json
import queue
import threading
import base64
import traceback
from typing import Optional, Any, List, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import speech
import uvicorn

from src.config.settings import settings
from src.utils.logger import logger
from src.utils.exceptions import AIServiceError, DatabaseError
from src.services.speech_service import get_speech_clients, synthesize_speech
from src.services.genai_service import get_genai_client
from src.engines.roleplay_engine import get_or_create_roleplay_session, send_roleplay_message
from src.evaluation.rubric_engine import evaluate_transcript, format_transcript_from_messages
from src.services.db_service import save_simulation_to_bq

app = FastAPI(title="BDR Simulator Live API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LANGUAGE_MAPPING = {
    "English": "en-US",
    "Spanish": "es-ES",
    "Portuguese": "pt-BR"
}

class SpeechStreamer:
    """
    Handles real-time STT streaming and interaction with Gemini.
    """
    def __init__(self, language: str, metadata: Dict[str, Any], websocket: WebSocket, loop: asyncio.AbstractEventLoop):
        self.language = language
        self.language_code = LANGUAGE_MAPPING.get(language, "en-US")
        self.sample_rate = metadata.get("sample_rate", 16000)
        self.websocket = websocket
        self.loop = loop
        self.audio_queue = queue.Queue()
        self.closed = False
        self.stt_running = False
        self.chunk_count = 0

        logger.info(f"🎤 Initializing SpeechStreamer: Lang={self.language_code}, Rate={self.sample_rate}")
        
        self.client = speech.SpeechClient(
            client_options={"quota_project_id": settings.GOOGLE_CLOUD_PROJECT}
        )

        self.genai_client = get_genai_client(settings.GOOGLE_CLOUD_PROJECT, settings.GOOGLE_CLOUD_LOCATION)
        _, self.tts_client = get_speech_clients()
        self.chat_session = None
        self.metadata = metadata
        self.session_messages = []

        # --- SILENCE DETECTION ---
        self.silence_timer: Optional[threading.Timer] = None
        self.last_transcript = ""
        self.silence_threshold = 2.0
        self.is_processing = False
        self.response_triggered = False

    def fill_buffer(self):
        while not self.closed:
            try:
                chunk = self.audio_queue.get(timeout=1)
                if chunk is None:
                    return
                self.chunk_count += 1
                yield chunk
            except queue.Empty:
                continue

    async def safe_send(self, data: Dict[str, Any]):
        if self.closed:
            return
        try:
            await self.websocket.send_json(data)
        except Exception as e:
            logger.error(f"WebSocket Send Error: {e}")

    def _handle_silence(self):
        if self.closed or not self.last_transcript or self.response_triggered:
            return
        
        logger.info("🤫 Silence detected. Processing...")
        self.response_triggered = True
        
        asyncio.run_coroutine_threadsafe(
            self.process_and_respond(self.last_transcript),
            self.loop
        )

    def _reset_silence_timer(self):
        if self.silence_timer:
            self.silence_timer.cancel()
        
        self.silence_timer = threading.Timer(self.silence_threshold, self._handle_silence)
        self.silence_timer.start()
        
        asyncio.run_coroutine_threadsafe(
            self.safe_send({"type": "vad_timer_reset", "duration": self.silence_threshold}),
            self.loop
        )

    async def process_and_respond(self, user_text: str):
        if self.is_processing:
            return

        self.is_processing = True
        try:
            logger.info(f"🤖 Processing user input: '{user_text}'")
            self.session_messages.append({"role": "user", "content": user_text})

            stop_phrase = "FINISH_CALL"
            self.chat_session = get_or_create_roleplay_session(
                existing_chat_session=self.chat_session,
                genai_client=self.genai_client,
                model_id=settings.MODEL_ID,
                target_company=self.metadata.get("target_company", "Google"),
                role=self.metadata.get("role", "CTO"),
                language=self.language,
                stop_phrase=stop_phrase
            )
            
            response_ai, _ = send_roleplay_message(
                chat_session=self.chat_session,
                user_text=user_text,
                language=self.language
            )

            if response_ai and response_ai.text and not self.closed:
                ai_text = response_ai.text
                self.session_messages.append({"role": "assistant", "content": ai_text})

                if stop_phrase in ai_text:
                    clean_ai_text = ai_text.replace(stop_phrase, "").strip()
                    audio_content = synthesize_speech(self.tts_client, clean_ai_text, self.language)
                    await self.safe_send({
                        "type": "alex_response",
                        "transcript": clean_ai_text,
                        "audio": base64.b64encode(audio_content).decode("utf-8")
                    })
                    
                    report = evaluate_transcript(format_transcript_from_messages(self.session_messages), self.genai_client, settings.MODEL_ID)
                    payload = {
                        "bms_id": self.metadata.get("bms_id", "UNKNOWN"),
                        "sim_mode": "Live Mode",
                        "target_company": self.metadata.get("target_company", "UNKNOWN"),
                        "role": self.metadata.get("role", "UNKNOWN"),
                        "final_score": report.get("final_score", 0),
                        "status": report.get("status", ""),
                        "detailed_evaluation": report.get("evaluations", []),
                        "transcript": format_transcript_from_messages(self.session_messages)
                    }
                    await asyncio.to_thread(save_simulation_to_bq, payload)

                    await self.safe_send({"type": "session_report", "report": report})
                    return

                audio_content = synthesize_speech(self.tts_client, ai_text, self.language)
                await self.safe_send({
                    "type": "alex_response",
                    "transcript": ai_text,
                    "audio": base64.b64encode(audio_content).decode("utf-8")
                })
        except Exception as e:
            logger.error(f"Error in process_and_respond: {e}")
            await self.safe_send({"type": "error", "message": str(e)})
        finally:
            self.is_processing = False
            self.response_triggered = False
            self.last_transcript = ""

    def run(self):
        self.stt_running = True
        recognition_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code=self.language_code,
            enable_automatic_punctuation=True,
        )
        streaming_config = speech.StreamingRecognitionConfig(config=recognition_config, interim_results=True)

        def request_generator():
            for content in self.fill_buffer():
                yield speech.StreamingRecognizeRequest(audio_content=content)

        try:
            responses = self.client.streaming_recognize(config=streaming_config, requests=request_generator())
            for response in responses:
                if self.closed or self.response_triggered or self.is_processing or not response.results:
                    continue

                result = response.results[0]
                if not result.alternatives: continue

                transcript = result.alternatives[0].transcript
                is_final = result.is_final
                self.last_transcript = transcript

                asyncio.run_coroutine_threadsafe(
                    self.safe_send({"type": "user_transcript", "transcript": transcript, "is_final": is_final}),
                    self.loop
                )

                if not self.response_triggered: self._reset_silence_timer()
                if is_final and not self.response_triggered:
                    if self.silence_timer: self.silence_timer.cancel()
                    self._handle_silence()

        except Exception as e:
            logger.error(f"STT Pipeline Error: {e}")
            asyncio.run_coroutine_threadsafe(self.safe_send({"type": "error", "message": f"STT error: {str(e)}"}), self.loop)
        finally:
            self.stt_running = False

@app.websocket("/ws/live-transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    loop = asyncio.get_event_loop()
    streamer = None
    try:
        first_msg = await websocket.receive()
        if "text" not in first_msg or first_msg["text"] is None:
            await websocket.send_json({"type": "error", "message": "Invalid metadata."})
            return

        metadata = json.loads(first_msg["text"])
        language = metadata.get("language", "English")
        streamer = SpeechStreamer(language, metadata, websocket, loop)
        threading.Thread(target=streamer.run, daemon=True).start()

        while True:
            msg = await websocket.receive()
            if msg.get("type") == "websocket.disconnect": break
            if msg.get("bytes"): streamer.audio_queue.put(msg["bytes"])
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket: Disconnected.")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
    finally:
        if streamer:
            streamer.closed = True
            streamer.audio_queue.put(None)

@app.get("/")
async def root():
    return {"status": "Backend Active"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
