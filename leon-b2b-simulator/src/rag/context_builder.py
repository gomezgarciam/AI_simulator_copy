from typing import List, Dict, Tuple

from src.rag.retrieval import retrieve_relevant_chunks


def build_assistant_context(question: str, chunk_index: List[Dict], top_k: int = 4) -> Tuple[str, List[str]]:
    relevant_chunks = retrieve_relevant_chunks(question, chunk_index, top_k=top_k)

    if not relevant_chunks:
        return "", []

    context_blocks = []
    sources = []

    for chunk in relevant_chunks:
        sources.append(chunk["source"])
        context_blocks.append(
            f"[Source: {chunk['source']} | Chunk: {chunk['chunk_id']}]\n{chunk['text']}"
        )

    return "\n\n".join(context_blocks), sorted(list(set(sources)))