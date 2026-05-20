from pypdf import PdfReader


def summarize_text(text, client, model_id, lang="English"):
    if not text or not isinstance(text, str):
        return ""

    prompt_templates = {
        "English": (
            "Summarize the following company research document in no more than 800 words, "
            "focusing on key business insights, challenges, strategic priorities, and relevant company context. "
            "Output the summary directly without introductory phrases.\n\n{text}"
        ),
        "Spanish": (
            "Resume el siguiente documento de investigación de la empresa en no más de 800 palabras, "
            "centrándote en insights clave del negocio, desafíos, prioridades estratégicas y contexto relevante de la empresa. "
            "Entrega el resumen directamente, sin frases introductorias.\n\n{text}"
        ),
        "Portuguese": (
            "Resuma o seguinte documento de pesquisa da empresa em no máximo 800 palavras, "
            "focando nos principais insights de negócios, desafios, prioridades estratégicas e contexto relevante da empresa. "
            "Entregue o resumo diretamente, sem frases introdutórias.\n\n{text}"
        ),
    }

    prompt = prompt_templates.get(lang, prompt_templates["English"]).format(text=text)

    response = client.models.generate_content(model=model_id, contents=prompt)
    return response.text if hasattr(response, "text") and response.text else text


def extract_text_from_uploaded_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        pages_text = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text)

        return "\n".join(pages_text).strip()

    except Exception as e:
        raise RuntimeError(f"Error reading PDF: {e}")
