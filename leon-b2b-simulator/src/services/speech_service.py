from google.cloud import speech
from google.cloud import texttospeech
from src.config.settings import GOOGLE_CLOUD_PROJECT


LANGUAGE_CODES = {
    "English": "en-US",
    "Spanish": "es-ES",
    "Portuguese": "pt-BR",
}

VOICE_NAMES = {
    "English": "en-US-Wavenet-D",
    "Spanish": "es-ES-Wavenet-B",
    "Portuguese": "pt-BR-Wavenet-B",
}


def get_speech_clients():
    client_options = {"quota_project_id": GOOGLE_CLOUD_PROJECT}
    return (
        speech.SpeechClient(client_options=client_options),
        texttospeech.TextToSpeechClient(client_options=client_options),
    )


def get_language_code(language: str) -> str:
    return LANGUAGE_CODES.get(language, "en-US")


def get_voice_name(language: str) -> str:
    return VOICE_NAMES.get(language, "en-US-Wavenet-D")


def transcribe_audio(speech_client, audio_bytes: bytes, language: str) -> str:
    language_code = get_language_code(language)

    response = speech_client.recognize(
        config=speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=44100,
            language_code=language_code,
            enable_automatic_punctuation=True,
            use_enhanced=True,
            model="latest_long" if language == "English" else "default",
        ),
        audio=speech.RecognitionAudio(content=audio_bytes),
    )

    if not response or not response.results:
        return ""

    full_transcript = [
        result.alternatives[0].transcript
        for result in response.results
        if result.alternatives
    ]

    return " ".join(full_transcript).strip()


def synthesize_speech(tts_client, text: str, language: str) -> bytes:
    language_code = get_language_code(language)
    voice_name = get_voice_name(language)

    clean_text = text.replace("*", "").replace("#", "").replace("- ", "")

    response = tts_client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=clean_text),
        voice=texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
        ),
        audio_config=texttospeech.AudioConfig(
            audio_encoding="MP3"
        ),
    )

    return response.audio_content