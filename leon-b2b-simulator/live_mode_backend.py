import asyncio
import json
import queue
import threading
import logging
import base64
import traceback

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import speech
import uvicorn

from src.config.settings import GOOGLE_CLOUD_PROJECT, MODEL_ID
from src.services.speech_service import get_speech_clients, synthesize_speech
from src.services.genai_service import get_genai_client
from src.engines.roleplay_engine import get_or_create_roleplay_session, send_roleplay_message

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("live_backend")

app = FastAPI()

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
    def __init__(self, language, metadata, websocket, loop):
        self.language = language
        self.language_code = LANGUAGE_MAPPING.get(language, "en-US")
        self.sample_rate = metadata.get("sample_rate", 16000)
        self.websocket = websocket
        self.loop = loop
        self.audio_queue = queue.Queue()
        self.closed = False
        self.stt_running = False
        self.chunk_count = 0

        logger.info(f"🎤 Configurando SpeechStreamer: Idioma={self.language_code}, SampleRate={self.sample_rate}")
        
        self.client = speech.SpeechClient(
            client_options={"quota_project_id": GOOGLE_CLOUD_PROJECT}
        )

        self.genai_client = get_genai_client(GOOGLE_CLOUD_PROJECT, "us-central1")
        _, self.tts_client = get_speech_clients()
        self.chat_session = None
        self.metadata = metadata

        # --- SILENCE DETECTION ---
        self.silence_timer: Optional[threading.Timer] = None
        self.last_transcript = ""
        self.silence_threshold = 2.0  # seconds
        self.is_processing = False
        self.response_triggered = False

    def fill_buffer(self):
        while not self.closed:
            try:
                chunk = self.audio_queue.get(timeout=1)
                if chunk is None:
                    return
                self.chunk_count += 1
                if self.chunk_count % 50 == 0:
                    logger.info(f"📥 Backend: Recibidos {self.chunk_count} fragmentos de audio.")
                yield chunk
            except queue.Empty:
                continue

    async def safe_send(self, data):
        if self.closed:
            return
        try:
            await self.websocket.send_json(data)
        except Exception as e:
            logger.error(f"WebSocket Send Error: {e}")

    def _handle_silence(self):
        if self.closed or not self.last_transcript or self.response_triggered:
            return
        
        logger.info("🤫 Silencio detectado. Procesando el último fragmento.")
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

    async def process_and_respond(self, user_text):
        if self.is_processing:
            logger.warning("⚠️ Intento de procesar mientras ya hay una respuesta en curso. Ignorando.")
            return

        self.is_processing = True
        try:
            logger.info(f"🤖 [ALEX ENGINE] Iniciando procesamiento para: '{user_text}'")
            logger.info(f"📊 [METADATA] Company: {self.metadata.get('target_company')}, Role: {self.metadata.get('role')}, Lang: {self.language}")

            self.chat_session = get_or_create_roleplay_session(
                existing_chat_session=self.chat_session,
                genai_client=self.genai_client,
                model_id=MODEL_ID,
                target_company=self.metadata.get("target_company", "Google"),
                role=self.metadata.get("role", "CTO"),
                language=self.language,
                stop_phrase="FINISH_CALL"
            )
            
            logger.info(f"⏳ [ALEX ENGINE] Enviando mensaje a Gemini...")

            response_ai, _ = send_roleplay_message(
                chat_session=self.chat_session,
                user_text=user_text,
                language=self.language
            )

            if response_ai and response_ai.text and not self.closed:
                ai_text = response_ai.text
                logger.info(f"🎙️ [ALEX ENGINE] Alex respondió: '{ai_text}'")

                audio_content = synthesize_speech(
                    self.tts_client,
                    ai_text,
                    self.language
                )
                
                logger.info(f"🔊 [ALEX ENGINE] Audio sintetizado ({len(audio_content)} bytes). Enviando al WebSocket...")

                await self.safe_send({
                    "type": "alex_response",
                    "transcript": ai_text,
                    "audio": base64.b64encode(audio_content).decode("utf-8")
                })
            else:
                logger.warning("⚠️ [ALEX ENGINE] Gemini no devolvió texto o el socket está cerrado.")

        except Exception as e:
            logger.error(f"Error en process_and_respond: {e}")
            traceback.print_exc()
            await self.safe_send({
                "type": "error",
                "message": f"Error generando respuesta: {str(e)}"
            })
        finally:
            self.is_processing = False
            self.response_triggered = False
            self.last_transcript = ""


    def run(self):
        logger.info(f"🎙️ Iniciando STT Stream para: {self.language_code} @ {self.sample_rate}Hz")
        self.stt_running = True

        recognition_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code=self.language_code,
            enable_automatic_punctuation=True,
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=recognition_config,
            interim_results=True,
            single_utterance=False
        )

        def request_generator():
            for content in self.fill_buffer():
                yield speech.StreamingRecognizeRequest(audio_content=content)

        try:
            responses = self.client.streaming_recognize(
                config=streaming_config,
                requests=request_generator()
            )

            for response in responses:
                if self.closed or self.response_triggered:
                    break

                if not response.results:
                    continue

                result = response.results[0]
                if not result.alternatives:
                    continue

                transcript = result.alternatives[0].transcript
                is_final = result.is_final

                logger.info(f"📝 STT {'FINAL' if is_final else 'INTERIM'}: {transcript}")

                self.last_transcript = transcript

                asyncio.run_coroutine_threadsafe(
                    self.safe_send({
                        "type": "user_transcript",
                        "transcript": transcript,
                        "is_final": is_final
                    }),
                    self.loop
                )

                if not self.response_triggered:
                    self._reset_silence_timer()

                if is_final and not self.response_triggered:
                    logger.info("🚀 [ALEX ENGINE] Disparando respuesta por 'is_final'")
                    if self.silence_timer:
                        self.silence_timer.cancel()
                    self._handle_silence()

        except Exception as e:
            logger.error(f"STT Pipeline Error: {e}")
            traceback.print_exc()
            asyncio.run_coroutine_threadsafe(
                self.safe_send({
                    "type": "error",
                    "message": f"STT error: {str(e)}"
                }),
                self.loop
            )
        finally:
            self.stt_running = False
            logger.info("🧵 Hilo STT finalizado.")

@app.websocket("/ws/live-transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("⚡ WebSocket: Conexión establecida.")
    loop = asyncio.get_event_loop()

    streamer = None

    try:
        first_msg = await websocket.receive()

        if "text" not in first_msg or first_msg["text"] is None:
            await websocket.send_json({
                "type": "error",
                "message": "Primer mensaje inválido. Se esperaba metadata JSON."
            })
            return

        metadata = json.loads(first_msg["text"])
        language = metadata.get("language", "English")
        logger.info(f"📝 Metadata recibida: {metadata}")

        streamer = SpeechStreamer(language, metadata, websocket, loop)
        stt_thread = threading.Thread(target=streamer.run, daemon=True)
        stt_thread.start()

        while True:
            msg = await websocket.receive()

            if msg.get("type") == "websocket.disconnect":
                logger.info("🔌 Cliente desconectado.")
                break

            if msg.get("bytes") is not None:
                streamer.audio_queue.put(msg["bytes"])
            elif msg.get("text") is not None:
                logger.info(f"📨 Mensaje texto adicional recibido: {msg['text']}")

    except WebSocketDisconnect:
        logger.info("🔌 WebSocket: Desconectado.")
    except Exception as e:
        logger.error(f"❌ Error en loop de WebSocket: {e}")
        traceback.print_exc()
    finally:
        if streamer:
            streamer.closed = True
            streamer.audio_queue.put(None)
        logger.info("♻️ Recursos liberados en Backend.")

@app.get("/")
async def root():
    return {"status": "Backend Active"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
