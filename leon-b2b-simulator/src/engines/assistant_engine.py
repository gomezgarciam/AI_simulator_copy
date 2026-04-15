from typing import Optional, Tuple, List

from src.rag.context_builder import build_assistant_context
from src.prompts.assistant import create_sales_assistant_prompt
from src.services.genai_service import generate_content


def format_roleplay_history(messages, max_turns=12):
    if not messages:
        return ""

    recent = messages[-max_turns:]
    lines = []

    for msg in recent:
        role = "BDR" if msg["role"] == "user" else "Alex"
        lines.append(f"{role}: {msg['content']}")

    return "\n".join(lines)


def detect_assistant_question_mode(question: str) -> str:
    q = question.lower().strip()

    roleplay_signals = [
        "what should i say",
        "how should i respond",
        "how do i respond",
        "how should i open",
        "opening",
        "objection",
        "what do i ask next",
        "what should i ask next",
        "how do i position",
        "how should i position",
        "what do i say next",
        "how was my opening",
        "help me with this conversation",
        "qué digo",
        "como digo",
        "cómo digo",
        "cómo respondo",
        "como respondo",
        "cómo debería responder",
        "como debería responder",
        "cómo abro",
        "como abro",
        "apertura",
        "objeción",
        "objecion",
        "qué pregunto",
        "que pregunto",
        "qué digo después",
        "que digo despues",
        "how should i handle",
        "handle this objection",
        "what should i do next",
        "o que eu digo",
        "como eu respondo",
        "como eu deveria responder",
        "como abro",
        "abertura",
        "objeção",
        "objecao",
        "o que eu pergunto",
        "o que eu digo depois",
    ]

    knowledge_signals = [
        "what does the play say",
        "what does the battle card say",
        "what do the pdfs say",
        "summarize",
        "summary",
        "document",
        "documents",
        "pdf",
        "pdfs",
        "play",
        "plays",
        "battle card",
        "battle cards",
        "fy26",
        "internal docs",
        "internal documents",
        "what is in",
        "explain based on the documents",
        "what does it say about",
        "resúmeme",
        "resumeme",
        "resume",
        "resumen",
        "documento",
        "documentos",
        "playbook",
        "documentos internos",
        "qué dice",
        "que dice",
        "qué hay en",
        "que hay en",
        "explícame",
        "explicame",
        "según los documentos",
        "segun los documentos",
        "o que diz",
        "resuma",
        "resumo",
        "com base nos documentos",
    ]

    if any(signal in q for signal in roleplay_signals):
        return "roleplay_coach"

    if any(signal in q for signal in knowledge_signals):
        return "knowledge_chat"

    return "auto"


def generate_sales_assistant_response(
    user_question: str,
    conversation_history: list,
    company: str,
    role: str,
    chunk_index: list,
    uploaded_company_context: Optional[str],
    language: str,
    genai_client,
    model_id: str,
    assistant_top_k: int = 4,
    roleplay_history_max_turns: int = 12,
) -> Tuple[str, List[str]]:
    retrieved_context, sources = build_assistant_context(
        user_question,
        chunk_index,
        top_k=assistant_top_k,
    )

    roleplay_history = format_roleplay_history(
        conversation_history,
        max_turns=roleplay_history_max_turns,
    )
    question_mode = detect_assistant_question_mode(user_question)

    assistant_prompt = create_sales_assistant_prompt(
        question=user_question,
        roleplay_history=roleplay_history,
        company=company,
        role=role,
        retrieved_context=retrieved_context,
        uploaded_company_context=uploaded_company_context,
        language=language,
        question_mode=question_mode,
    )

    answer = generate_content(
        genai_client,
        model_id,
        assistant_prompt,
    ) or "No response generated."

    return answer, sources