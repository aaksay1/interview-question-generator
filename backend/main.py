"""
FastAPI backend for generating interview questions from resumes and job descriptions.

Main Flow:
1. Resume PDF → Extract text → Chunk text
2. Chunks → FAISS vectorstore (semantic search)
3. Job description + Relevant chunks → LLM (Groq)
4. LLM response → Parse JSON → Return questions

Run locally: uvicorn backend.main:app --reload
"""
import os
import tempfile
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

from chains.question_chain import generate_questions_for_jd
from utils.parsing import extract_questions
from utils.pdf_parser import pdf_to_text
from utils.chunker import chunk_resume_text
from utils.validation import (
    validate_file_size,
    validate_pdf_type,
    validate_job_description
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables (GROQ_API_KEY)
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    Initializes embeddings model on startup (reused for all requests).
    """
    logger.info("Initializing embeddings model...")
    app.state.embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    logger.info("Embeddings initialized successfully")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Interview Question Generator API",
    description="Generate tailored interview questions from resumes and job descriptions",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Interview Question Generator API is running"
    }


@app.post("/generate-questions")
async def generate_questions(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Generate interview questions from a resume PDF and job description.
    
    Main processing flow:
    1. Validate inputs (file type, size, job description)
    2. Extract text from PDF resume
    3. Chunk resume text intelligently (based on length)
    4. Build FAISS vectorstore from chunks (in-memory)
    5. Retrieve top 3 relevant chunks using semantic search
    6. Generate questions using Groq LLM
    7. Parse JSON from LLM response
    8. Return questions as JSON
    
    Args:
        resume: PDF file containing the candidate's resume
        job_description: Text description of the job position
        
    Returns:
        JSON response: {"questions": [{"category": "...", "question": "..."}, ...]}
        
    Raises:
        HTTPException: For validation errors or processing failures
    """
    tmp_path = None
    
    try:
        # ============================================================
        # STEP 1: VALIDATE INPUTS
        # ============================================================
        logger.info(f"Received request: resume={resume.filename}, job_desc_length={len(job_description)}")
        
        validate_pdf_type(resume.filename)
        validate_file_size(resume.file)
        validate_job_description(job_description)
        
        # ============================================================
        # STEP 2: EXTRACT TEXT FROM PDF RESUME
        # ============================================================
        logger.info("Extracting text from PDF...")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await resume.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            resume_text = pdf_to_text(tmp_path)
            logger.info(f"Extracted {len(resume_text)} characters from PDF")
        except ValueError as e:
            logger.error(f"PDF parsing error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            # Clean up temp file immediately after extraction
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
                tmp_path = None
        
        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Resume PDF contains insufficient text. Please ensure the PDF has extractable text content."
            )
        
        # ============================================================
        # STEP 3: CHUNK RESUME TEXT INTELLIGENTLY
        # ============================================================
        # Chunking strategy adapts based on resume length:
        # - Short resumes: smaller chunks (500 chars)
        # - Medium resumes: standard chunks (1000 chars)
        # - Long resumes: larger chunks (1500 chars)
        logger.info("Chunking resume text...")
        try:
            chunks = chunk_resume_text(resume_text)
            if not chunks or len(chunks) == 0:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to chunk resume text"
                )
            logger.info(f"Created {len(chunks)} chunks")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Chunking error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing resume: {str(e)}"
            )
        
        # ============================================================
        # STEP 4: BUILD FAISS VECTORSTORE (IN-MEMORY)
        # ============================================================
        # Create embeddings for each chunk and build vectorstore
        # This enables semantic search to find relevant resume sections
        logger.info("Building FAISS vectorstore...")
        try:
            vectorstore = FAISS.from_texts(
                chunks,
                app.state.embeddings  # Reuse embeddings initialized on startup
            )
        except Exception as e:
            logger.error(f"Vectorstore creation error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating vectorstore: {str(e)}"
            )
        
        # ============================================================
        # STEP 5: RETRIEVE RELEVANT RESUME CHUNKS
        # ============================================================
        # Use semantic search to find top 3 chunks most relevant to job description
        logger.info("Retrieving relevant resume chunks using semantic search...")
        try:
            retrieved_docs = vectorstore.similarity_search(job_description, k=3)
            if not retrieved_docs:
                logger.warning("No relevant documents retrieved")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve relevant resume sections"
                )
            logger.info(f"Retrieved {len(retrieved_docs)} relevant chunks")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Similarity search error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error searching resume: {str(e)}"
            )
        
        # ============================================================
        # STEP 6: GENERATE QUESTIONS USING GROQ LLM
        # ============================================================
        # Send job description + relevant resume chunks to LLM
        # LLM generates tailored interview questions
        logger.info("Generating questions with Groq LLM...")
        try:
            llm_response = generate_questions_for_jd(job_description, retrieved_docs)
        except ValueError as e:
            # API key or validation error
            logger.error(f"LLM configuration error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"LLM generation error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate questions: {str(e)}"
            )
        
        if not llm_response:
            raise HTTPException(
                status_code=500,
                detail="LLM returned empty response"
            )
        
        logger.info(f"LLM Response (first 500 chars): {llm_response[:500]}")
        
        # ============================================================
        # STEP 7: PARSE JSON FROM LLM RESPONSE
        # ============================================================
        # Extract JSON array from LLM response (may be wrapped in markdown code blocks)
        logger.info("Extracting questions from LLM response...")
        questions = extract_questions(llm_response)
        
        if not questions or len(questions) == 0:
            logger.warning(f"Failed to extract questions. Raw response: {llm_response[:1000]}")
            raise HTTPException(
                status_code=500,
                detail="Failed to extract questions from LLM response. The response may not be in the expected JSON format."
            )
        
        logger.info(f"Successfully generated {len(questions)} questions")
        return JSONResponse(content={"questions": questions})
        
    except HTTPException:
        # Re-raise HTTP exceptions (already properly formatted)
        raise
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        # Ensure temp file is cleaned up even on error
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp file: {str(e)}")
