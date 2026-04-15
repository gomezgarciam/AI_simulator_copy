from google import genai
from google.genai import types


def get_genai_client(project: str, location: str):
    return genai.Client(
        vertexai=True,
        project=project,
        location=location
    )


def create_chat_session(client, model_id: str, system_instruction: str, temperature: float = 0.7):
    return client.chats.create(
        model=model_id,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature
        )
    )


def generate_content(client, model_id: str, prompt: str) -> str:
    response = client.models.generate_content(
        model=model_id,
        contents=prompt
    )
    return response.text if hasattr(response, "text") and response.text else ""