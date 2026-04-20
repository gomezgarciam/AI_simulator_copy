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
        self.language = language # English, Spanish, etc.
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
        self.metadata = metadata # Contiene company, role, etc.

    def fill_buffer(self):
        while not self.closed:
            chunk = self.audio_queue.get()
            if chunk is None: return
            yield chunk

    async def get_alex_response(self, user_text):
        """Envía el texto a Gemini y genera el audio de respuesta."""
        try:
            logger.info(f"Enviando a Alex: {user_text}")
            
            # 1. Obtener o crear sesión de chat
            self.chat_session = get_or_create_roleplay_session(
                existing_chat_session=self.chat_session,
                genai_client=self.genai_client,
                model_id=MODEL_ID,
                target_company=self.metadata.get("target_company", "Google"),
                role=self.metadata.get("role", "CTO"),
                language=self.language,
                stop_phrase="FINISH_CALL"
            )

            # 2. Enviar mensaje a Gemini
            response_ai, _ = send_roleplay_message(
                chat_session=self.chat_session,
                user_text=user_text,
                language=self.language
            )
            
            if response_ai and response_ai.text:
                ai_text = response_ai.text
                logger.info(f"Alex respondió: {ai_text}")
                
                # 3. Generar Audio (TTS)
                audio_content = synthesize_speech(
                    self.tts_client,
                    ai_text,
                    self.language
                )
                
                # 4. Enviar texto y audio al frontend
                await self.websocket.send_json({
                    "type": "alex_response",
                    "transcript": ai_text,
                    "audio": base64.b64encode(audio_content).decode('utf-8')
                })
        except Exception as e:
            logger.error(f"Error procesando respuesta de Alex: {e}")

    def run(self):
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
                if not response.results: continue
                result = response.results[0]
                if not result.alternatives: continue
                
                transcript = result.alternatives[0].transcript
                is_final = result.is_final
                
                # Enviar transcripción al frontend
                asyncio.run_coroutine_threadsafe(
                    self.websocket.send_json({
                        "type": "user_transcript",
                        "transcript": transcript,
                        "is_final": is_final
                    }), 
                    self.loop
                )

                # Si la frase es final, ¡Alex debe responder!
                if is_final and len(transcript.strip()) > 2:
                    asyncio.run_coroutine_threadsafe(
                        self.get_alex_response(transcript),
                        self.loop
                    )
                
        except Exception as e:
            logger.error(f"Error en STT: {e}")
        finally:
            self.closed = True

@app.websocket("/ws/live-transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info(f"Conexión Live Mode establecida.")
    loop = asyncio.get_event_loop()
    
    try:
        # 1. Esperar metadatos (ahora esperamos más info)
        initial_msg = await websocket.receive_text()
        metadata = json.loads(initial_msg)
        language = metadata.get("language", "English")
        
        # 2. Iniciar lógica de Alex y STT
        streamer = SpeechStreamer(language, metadata, websocket, loop)
        stt_thread = threading.Thread(target=streamer.run)
        stt_thread.start()

        # 3. Recibir Audio
        while True:
            data = await websocket.receive_bytes()
            streamer.audio_queue.put(data)
            
    except WebSocketDisconnect:
        logger.info("Live Mode desconectado.")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if 'streamer' in locals():
            streamer.audio_queue.put(None)
            streamer.closed = True

@app.get("/")
async def root():
    return {"status": "Sprint 2 Backend Active"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
