from utils.pdf_parser import extract_text_from_pdf_bytes
from utils.text import clean_text

with open("sample_resume.pdf", "rb") as f:
    pdf_bytes = f.read()

text = extract_text_from_pdf_bytes(pdf_bytes)
text = clean_text(text)

print(text[:500])  # print first 500 chars
