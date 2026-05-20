from typing import Dict, List


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> List[str]:
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == text_length:
            break

        start = end - overlap

    return chunks


def build_chunk_index(documents: List[Dict]) -> List[Dict]:
    indexed_chunks = []

    for doc in documents:
        source = doc["source"]
        text = doc["text"]
        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            indexed_chunks.append({"source": source, "chunk_id": i, "text": chunk})

    return indexed_chunks
