import asyncio
import json
import os
import queue
import threading
import logging
import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import speech
import uvicorn

# Importamos la lógica existente del proyecto
from src.config.settings import GOOGLE_CLOUD_PROJECT, MODEL_ID
from src.services.speech_service import get_speech_clients, synthesize_speech
from src.services.genai_service import get_genai_client
from src.engines.roleplay_engine import get_or_create_roleplay_session, send_roleplay_message

# Configuración de Logging
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
        self.client = speech.SpeechClient(
            client_options={"quota_project_id": GOOGLE_CLOUD_PROJECT}
        )
        self.closed = False
        
        # Lógica de Alex
        self.genai_client = get_genai_client(GOOGLE_CLOUD_PROJECT, "us-central1")
        _, self.tts_client = get_speech_clients()
        self.chat_session = None
        self.metadata = metadata

    def fill_buffer(self):
        while not self.closed:
            try:
                chunk = self.audio_queue.get(timeout=1)
                if chunk is None: return
                yield chunk
            except queue.Empty:
                continue

    async def safe_send(self, data):
        """Envía datos por el websocket solo si está abierto."""
        if self.closed: return
        try:
            await self.websocket.send_json(data)
        except Exception as e:
            logger.error(f"Error enviando al websocket: {e}")
            self.closed = True

    async def get_alex_response(self, user_text):
        """Envía el texto a Gemini y genera el audio de respuesta."""
        try:
            logger.info(f"Procesando con Alex: {user_text}")
            
            self.chat_session = get_or_create_roleplay_session(
                existing_chat_session=self.chat_session,
                genai_client=self.genai_client,
                model_id=MODEL_ID,
                target_company=self.metadata.get("target_company", "Google"),
                role=self.metadata.get("role", "CTO"),
                language=self.language,
                stop_phrase="FINISH_CALL"
            )

            response_ai, _ = send_roleplay_message(
                chat_session=self.chat_session,
                user_text=user_text,
                language=self.language
            )
            
            if response_ai and response_ai.text and not self.closed:
                ai_text = response_ai.text
                logger.info(f"Alex respondió: {ai_text}")
                
                audio_content = synthesize_speech(
                    self.tts_client,
                    ai_text,
                    self.language
                )
                
                await self.safe_send({
                    "type": "alex_response",
                    "transcript": ai_text,
                    "audio": base64.b64encode(audio_content).decode('utf-8')
                })
        except Exception as e:
            logger.error(f"Error procesando respuesta de Alex: {e}")

    def run(self):
        logger.info(f"Configurando STT para: {self.language_code}")
        recognition_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code=self.language_code,
            enable_automatic_punctuation=True,
        )
        streaming_config = speech.StreamingRecognitionConfig(
            config=recognition_config,
            interim_results=True
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
                if self.closed: break
                if not response.results: continue
                result = response.results[0]
                if not result.alternatives: continue
                
                transcript = result.alternatives[0].transcript
                is_final = result.is_final
                
                if is_final:
                    logger.info(f"STT FINAL: {transcript}")
                
                # Enviar transcripción al frontend
                asyncio.run_coroutine_threadsafe(
                    self.safe_send({
                        "type": "user_transcript",
                        "transcript": transcript,
                        "is_final": is_final
                    }), 
                    self.loop
                )

                if is_final and len(transcript.strip()) > 1:
                    asyncio.run_coroutine_threadsafe(
                        self.get_alex_response(transcript),
                        self.loop
                    )
                
        except Exception as e:
            if not self.closed:
                logger.error(f"Error en STT: {e}")
        finally:
            self.closed = True
            logger.info("Hilo STT finalizado.")

@app.websocket("/ws/live-transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info(f"Conexión Live Mode establecida.")
    loop = asyncio.get_event_loop()
    
    streamer = None
    try:
        initial_msg = await websocket.receive_text()
        metadata = json.loads(initial_msg)
        language = metadata.get("language", "English")
        
        streamer = SpeechStreamer(language, metadata, websocket, loop)
        stt_thread = threading.Thread(target=streamer.run)
        stt_thread.start()

        while True:
            data = await websocket.receive_bytes()
            if streamer.closed: break
            streamer.audio_queue.put(data)
            
    except WebSocketDisconnect:
        logger.info("Live Mode desconectado.")
    except Exception as e:
        logger.error(f"Error en websocket principal: {e}")
    finally:
        if streamer:
            streamer.closed = True
            streamer.audio_queue.put(None)
        logger.info("Conexión cerrada y recursos liberados.")

@app.get("/")
async def root():
    return {"status": "Backend Active"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
