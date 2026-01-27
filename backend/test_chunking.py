from utils.pdf_parser import extract_text_from_pdf_bytes
from utils.text import clean_text
from utils.chunker import chunk_text

with open("sample_resume.pdf", "rb") as f:
    pdf_bytes = f.read()

text = extract_text_from_pdf_bytes(pdf_bytes)
text = clean_text(text)

chunks = chunk_text(text)

print(f"Total chunks: {len(chunks)}")
print("First chunk preview:")
print(chunks[0])