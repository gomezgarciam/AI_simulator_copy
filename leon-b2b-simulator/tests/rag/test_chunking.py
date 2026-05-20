from src.rag.chunking import build_chunk_index, chunk_text


def test_chunk_text_simple():
    text = "This is a test text that will be chunked. It is a bit long to make sure that chunking happens."
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    assert len(chunks) > 1
    assert chunks[0] == "This is a test text"
    assert chunks[1] == "text that will be ch"
    assert "nking happens." in chunks[-1]


def test_chunk_text_empty():
    text = ""
    chunks = chunk_text(text)
    assert chunks == []


def test_chunk_text_small():
    text = "This is a short text."
    chunks = chunk_text(text, chunk_size=50, overlap=10)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_build_chunk_index_simple():
    documents = [
        {"source": "doc1", "text": "This is the first document."},
        {
            "source": "doc2",
            "text": "This is the second document, which is a bit longer.",
        },
    ]
    indexed_chunks = build_chunk_index(documents)
    assert len(indexed_chunks) > 0
    assert indexed_chunks[0]["source"] == "doc1"
    assert indexed_chunks[0]["chunk_id"] == 0
    assert indexed_chunks[0]["text"] == "This is the first document."

    # Check if second document was chunked if it was long enough
    doc2_chunks = [chunk for chunk in indexed_chunks if chunk["source"] == "doc2"]
    assert len(doc2_chunks) > 0
    assert (
        doc2_chunks[0]["text"] == "This is the second document, which is a bit longer."
    )


def test_build_chunk_index_empty():
    documents = []
    indexed_chunks = build_chunk_index(documents)
    assert indexed_chunks == []


def test_chunk_text_with_overlap():
    text = "abcdefghijklmnopqrstuvwxyz"
    chunks = chunk_text(text, chunk_size=10, overlap=3)
    assert chunks[0] == "abcdefghij"
    assert chunks[1] == "hijklmnopq"
    assert chunks[2] == "opqrstuvwx"
    assert chunks[3] == "vwxyz"


def test_chunk_text_exact_size():
    text = "12345678901234567890"
    chunks = chunk_text(text, chunk_size=10, overlap=2)
    assert chunks[0] == "1234567890"
    assert chunks[1] == "9012345678"
