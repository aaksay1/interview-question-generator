import io
import pdfplumber

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extracts text from a PDF file provided as bytes.
    Returns a single cleaned string.
    """
    text = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)
