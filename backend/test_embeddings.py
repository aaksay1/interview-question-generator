import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from utils.pdf_parser import extract_text_from_pdf_bytes
from utils.text import clean_text
from utils.chunker import chunk_text

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# ---------------------------
# Step 1: Load & process resume
# ---------------------------
with open("sample_resume.pdf", "rb") as f:
    pdf_bytes = f.read()

text = extract_text_from_pdf_bytes(pdf_bytes)
text = clean_text(text)
resume_chunks = chunk_text(text)

print(f"Total resume chunks: {len(resume_chunks)}")

# ---------------------------
# Step 2: Initialize embeddings
# ---------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ---------------------------
# Step 3: Build in-memory FAISS vector store
# ---------------------------
vectorstore = FAISS.from_texts(resume_chunks, embeddings)

# ---------------------------
# Step 4: Test retrieval with sample JD
# ---------------------------
sample_jd = """
Looking for a software engineer experienced with FastAPI,
Python backend development, and deploying scalable AI chat systems.
"""

# Retrieve top 3 relevant resume chunks
retrieved = vectorstore.similarity_search(sample_jd, k=3)

print("\nTop 3 retrieved resume chunks for sample JD:\n")
for i, chunk in enumerate(retrieved, 1):
    print(f"--- Chunk {i} ---")
    print(chunk)
    print()