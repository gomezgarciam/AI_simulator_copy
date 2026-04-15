import re
from typing import List, Dict


def tokenize(text: str) -> set:
    text = text.lower()
    words = re.findall(r"\b[a-zA-Z0-9áéíóúñãõçüÁÉÍÓÚÑÃÕÇÜ]+\b", text)
    return set(words)


def score_chunk(question: str, chunk: str) -> int:
    q_tokens = tokenize(question)
    c_tokens = tokenize(chunk)
    return len(q_tokens.intersection(c_tokens))


def retrieve_relevant_chunks(question: str, chunk_index: List[Dict], top_k: int = 4) -> List[Dict]:
    scored = []

    for chunk in chunk_index:
        score = score_chunk(question, chunk["text"])
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:top_k]]