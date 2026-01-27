# backend/main.py

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from chains.question_chain import generate_questions_for_jd, SYSTEM_PROMPT, QUESTION_PROMPT_TEMPLATE
from utils.parsing import extract_questions
from PyPDF2 import PdfReader
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Interview Question Generator")

# Initialize embeddings once
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def pdf_to_text(file) -> str:
    """Extract text from uploaded PDF file"""
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


@app.post("/generate-questions")
async def generate_questions(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    # Step 1: Extract resume text
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await resume.read())
        tmp_path = tmp.name

    resume_text = pdf_to_text(tmp_path)
    os.remove(tmp_path)

    # Step 2: Chunk resume text
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = splitter.split_text(resume_text)

    # Step 3: Build FAISS vectorstore in-memory
    vectorstore = FAISS.from_texts(chunks, embeddings)

    # Step 4: Retrieve top 3 relevant resume chunks for the job description
    retrieved_docs = vectorstore.similarity_search(job_description, k=3)

    # Step 5: Generate questions using Groq LLM
    llm_response = generate_questions_for_jd(job_description, retrieved_docs)
    
    # Log the raw response for debugging (first 500 chars)
    logger.info(f"LLM Response (first 500 chars): {llm_response[:500] if llm_response else 'None'}")

    # Step 6: Extract JSON list from LLM output
    questions = extract_questions(llm_response)
    
    # Log if we got empty questions
    if not questions:
        logger.warning(f"Failed to extract questions. Raw response: {llm_response[:1000] if llm_response else 'None'}")

    return JSONResponse(content={"questions": questions})
