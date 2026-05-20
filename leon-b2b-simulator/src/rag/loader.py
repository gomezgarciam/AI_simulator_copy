import io

from google.cloud import storage
from pypdf import PdfReader


def load_internal_documents_from_gcs(bucket_name: str, prefix: str = ""):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    documents = []

    for blob in bucket.list_blobs(prefix=prefix):
        if not blob.name.lower().endswith(".pdf"):
            continue

        try:
            pdf_bytes = blob.download_as_bytes()
            reader = PdfReader(io.BytesIO(pdf_bytes))

            pages_text = []
            for page in reader.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    pages_text.append(page_text)

            full_text = "\n".join(pages_text).strip()

            if full_text:
                documents.append({"source": blob.name, "text": full_text})

        except Exception as e:
            print(f"Error loading {blob.name}: {e}")

    return documents
