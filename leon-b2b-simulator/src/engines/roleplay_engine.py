import time
from typing import Optional, Tuple

from src.prompts.roleplay import create_system_prompt
from src.services.genai_service import create_chat_session


def build_roleplay_extra_context(
    pdf_summary: Optional[str] = None,
    company_url: Optional[str] = None,
) -> Optional[str]:
    extra_context_parts = []

    if pdf_summary:
        extra_context_parts.append(
            f"Uploaded company research summary:\n{pdf_summary}"
        )

    if company_url:
        extra_context_parts.append(
            f"Company website URL provided by user: {company_url}"
        )

    return "\n\n".join(extra_context_parts) if extra_context_parts else None


def get_or_create_roleplay_session(
    existing_chat_session,
    genai_client,
    model_id: str,
    target_company: str,
    role: str,
    language: str,
    stop_phrase: str,
    pdf_summary: Optional[str] = None,
    company_url: Optional[str] = None,
    temperature: float = 0.7,
):
    if existing_chat_session is not None:
        return existing_chat_session

    extra_context = build_roleplay_extra_context(
        pdf_summary=pdf_summary,
        company_url=company_url,
    )

    system_instruction = create_system_prompt(
        target_company=target_company,
        role=role,
        language=language,
        stop_phrase=stop_phrase,
        extra_context=extra_context,
    )

    return create_chat_session(
        genai_client,
        model_id,
        system_instruction,
        temperature=temperature,
    )


def send_roleplay_message(
    chat_session,
    user_text: str,
    language: str,
    max_retries: int = 3,
) -> Tuple[object, Optional[str]]:
    quota_messages = {
        "English": "⚠️ Daily usage quota exceeded. Retrying in a few seconds...",
        "Spanish": "⚠️ Se ha excedido la cuota de uso diario. Reintentando en unos segundos...",
        "Portuguese": "⚠️ A cota de uso diário foi excedida. Tentando novamente em alguns segundos...",
    }

    attempt = 0
    response_ai = None

    while attempt < max_retries:
        try:
            response_ai = chat_session.send_message(user_text)
            return response_ai, None
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e).upper():
                attempt += 1
                if attempt < max_retries:
                    time.sleep(attempt * 2)
                else:
                    return None, quota_messages.get(language, quota_messages["English"])
            else:
                raise e

    return None, quota_messages.get(language, quota_messages["English"])