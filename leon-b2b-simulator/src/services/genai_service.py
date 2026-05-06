from typing import Any, Optional
from google import genai
from google.genai import types
from src.utils.logger import logger
from src.utils.exceptions import ai_service_retry, AIServiceError

def get_genai_client(project: str, location: str) -> genai.Client:
    """
    Initializes and returns a Vertex AI GenAI Client.
    """
    try:
        return genai.Client(
            vertexai=True,
            project=project,
            location=location
        )
    except Exception as e:
        logger.error(f"Failed to initialize GenAI Client: {e}")
        raise AIServiceError(f"GenAI Initialization failed: {e}")

def create_chat_session(
    client: genai.Client, 
    model_id: str, 
    system_instruction: str, 
    temperature: float = 0.7
) -> Any:
    """
    Creates a new interactive chat session.
    """
    try:
        return client.chats.create(
            model=model_id,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature
            )
        )
    except Exception as e:
        logger.error(f"Failed to create chat session: {e}")
        raise AIServiceError(f"Chat session creation failed: {e}")

@ai_service_retry
def generate_content(client: genai.Client, model_id: str, prompt: str) -> str:
    """
    Generates a single completion with retry logic.
    """
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        return response.text if hasattr(response, "text") and response.text else ""
    except Exception as e:
        logger.error(f"Error during generate_content: {e}")
        raise AIServiceError(f"Content generation failed: {e}")
