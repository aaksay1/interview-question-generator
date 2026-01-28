"""
FastAPI backend for generating interview questions from resumes and job descriptions.

ARCHITECTURE: No local ML models - all intelligence via Groq API
- No embeddings, no FAISS, no HuggingFace, no PyTorch
- Lightweight keyword matching for chunk selection
- Groq LLM handles all reasoning and relevance
- Optimized for Render Free Tier (512MB RAM)

Main Flow:
1. Resume PDF → Extract text → Chunk text
2. Chunks → Keyword matching (lightweight, no ML)
3. Job description + Selected chunks → Groq LLM
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
from dotenv import load_dotenv

from chains.question_chain import generate_questions_for_jd
from utils.parsing import extract_questions
from utils.pdf_parser import pdf_to_text
from utils.chunker import chunk_resume_text
from utils.keyword_matcher import select_relevant_chunks
from utils.validation import (
    validate_file_size,
    validate_pdf_type,
    validate_job_description,
    validate_resume_text_length
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
    No ML models loaded - fast cold start (<2s).
    """
    logger.info("Application starting (no ML models - fast startup)")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Interview Question Generator API",
    description="Generate tailored interview questions from resumes and job descriptions (ML-free architecture)",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://interview-question-generator-mocha.vercel.app",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Interview Question Generator API is running (ML-free architecture)",
        "architecture": "Groq-only (no local ML models)"
    }


@app.post("/generate-questions")
async def generate_questions(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Generate interview questions from a resume PDF and job description.
    
    Architecture: No local ML models
    - Uses lightweight keyword matching for chunk selection
    - Groq LLM handles all intelligence and reasoning
    - Memory-efficient for Render Free Tier (512MB RAM)
    
    Main processing flow:
    1. Validate inputs (file type, size, text length)
    2. Extract text from PDF resume
    3. Chunk resume text (simple text splitting)
    4. Select relevant chunks using keyword matching (no embeddings)
    5. Generate questions using Groq LLM
    6. Parse JSON from LLM response
    7. Return questions as JSON
    
    Args:
        resume: PDF file containing the candidate's resume (max 2MB)
        job_description: Text description of the job position (10-10,000 chars)
        
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
        validate_file_size(resume.file)  # Max 2MB
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
        
        # Validate resume text length (memory safety)
        validate_resume_text_length(resume_text)
        
        # ============================================================
        # STEP 3: CHUNK RESUME TEXT (SIMPLE TEXT SPLITTING)
        # ============================================================
        # Lightweight chunking - no ML models required
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
        # STEP 4: SELECT RELEVANT CHUNKS (KEYWORD MATCHING)
        # ============================================================
        # Lightweight keyword matching - no embeddings, no FAISS
        # Groq LLM will handle all intelligence - this just filters chunks
        logger.info("Selecting relevant chunks using keyword matching...")
        try:
            selected_chunks = select_relevant_chunks(chunks, job_description, k=5)
            if not selected_chunks:
                logger.warning("No chunks selected, using first few chunks")
                selected_chunks = chunks[:3]  # Fallback to first 3 chunks
            logger.info(f"Selected {len(selected_chunks)} relevant chunks")
        except Exception as e:
            logger.error(f"Chunk selection error: {str(e)}")
            # Fallback: use first 5 chunks
            selected_chunks = chunks[:5]
            logger.info(f"Using fallback: first {len(selected_chunks)} chunks")
        
        # ============================================================
        # STEP 5: GENERATE QUESTIONS USING GROQ LLM
        # ============================================================
        # Groq handles all intelligence - receives job description + selected chunks
        logger.info("Generating questions with Groq LLM...")
        try:
            # Pass chunks as simple strings (not Document objects)
            llm_response = generate_questions_for_jd(job_description, selected_chunks)
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
        # STEP 6: PARSE JSON FROM LLM RESPONSE
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
