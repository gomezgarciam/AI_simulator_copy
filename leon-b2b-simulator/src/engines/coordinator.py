import io
from typing import Dict, Any, List, Optional, Tuple
from src.services.genai_service import generate_content
from src.services.speech_service import transcribe_audio, synthesize_speech
from src.services.audio_service import load_audiosegment_from_streamlit_audio
from src.engines.roleplay_engine import get_or_create_roleplay_session, send_roleplay_message
from src.evaluation.rubric_engine import evaluate_transcript, format_transcript_from_messages
from src.services.db_service import save_simulation_to_bq
from src.config.settings import settings

class SimulationCoordinator:
    """
    Orchestrates the simulation flow: Audio -> Transcription -> LLM -> TTS -> Evaluation -> DB.
    Decouples UI from business logic.
    """

    def __init__(self, genai_client, speech_client, tts_client):
        self.genai_client = genai_client
        self.speech_client = speech_client
        self.tts_client = tts_client

    def process_user_audio(
        self, 
        audio_val: Any, 
        language: str
    ) -> Optional[str]:
        """Loads and transcribes user audio."""
        seg = load_audiosegment_from_streamlit_audio(audio_val)
        if seg is None:
            return None

        buf = io.BytesIO()
        seg.export(buf, format="wav")
        return transcribe_audio(self.speech_client, buf.getvalue(), language)

    def get_alex_response(
        self,
        chat_session: Any,
        user_text: str,
        language: str,
        target_company: str,
        role: str,
        pdf_summary: Optional[str] = None,
        company_url: Optional[str] = None,
        stop_phrase: str = "FINISH_CALL"
    ) -> Tuple[str, Optional[bytes], bool]:
        """
        Communicates with Alex (Gemini) and synthesizes audio response.
        Returns: (text_response, audio_bytes, is_finished)
        """
        # Ensure session exists (though usually handled by state)
        if chat_session is None:
            chat_session = get_or_create_roleplay_session(
                existing_chat_session=None,
                genai_client=self.genai_client,
                model_id=settings.MODEL_ID,
                target_company=target_company,
                role=role,
                language=language,
                stop_phrase=stop_phrase,
                pdf_summary=pdf_summary,
                company_url=company_url
            )

        response_ai, _ = send_roleplay_message(
            chat_session=chat_session,
            user_text=user_text,
            language=language
        )

        if not response_ai or not response_ai.text:
            return "", None, False

        ai_text = response_ai.text
        is_finished = stop_phrase in ai_text
        clean_text = ai_text.replace(stop_phrase, "").strip()
        
        audio_response = synthesize_speech(self.tts_client, clean_text, language)
        
        return clean_text, audio_response, is_finished

    def run_evaluation_and_save(
        self, 
        messages: List[Dict[str, str]], 
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Runs the final MEDPICC evaluation and saves results to BigQuery.
        """
        transcript = format_transcript_from_messages(messages)
        # Añadimos "bdr_qa_rubric_v1" al final
        report = evaluate_transcript(
            transcript, 
            self.genai_client, 
            settings.MODEL_ID,
            "bdr_qa_rubric_v1"
        )
        
        # Prepare payload for BQ
        payload = {
            "bms_id": session_data.get("bms_id", "UNKNOWN"),
            "sim_mode": session_data.get("sim_mode", "Assisted Mode"),
            "target_company": session_data.get("target_company", ""),
            "role": session_data.get("role", ""),
            "final_score": report.get("final_score", 0),
            "status": report.get("status", ""),
            "detailed_evaluation": report.get("evaluations", []),
            "transcript": transcript
        }
        
        save_simulation_to_bq(payload)
        return report
