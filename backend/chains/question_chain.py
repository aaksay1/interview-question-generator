"""
LLM chain for generating interview questions from job descriptions and resumes.

ARCHITECTURE: Groq-only - no local ML models
- All intelligence handled by Groq LLM
- Receives simple text chunks (no Document objects, no embeddings)
- Groq handles all reasoning and relevance matching
"""
import os
import logging
from typing import List, Union

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

# ============================================================
# PROMPT TEMPLATES
# ============================================================

SYSTEM_PROMPT = """You are a hiring manager conducting a real interview.

Your task is to generate interview questions that test whether
the candidate truly understands and can defend the experience
listed on their resume, in relation to the job description.

Rules:
- Questions must reference the candidate's experience implicitly or explicitly
- Avoid generic questions
- Prefer follow-up and depth-probing questions
- Output must be realistic and role-specific
- Return ONLY valid JSON - no markdown, no explanations"""

QUESTION_PROMPT_TEMPLATE = """Job description:
{job_description}

Relevant resume sections:
{resume_context}

Generate 5 interview questions that a real interviewer would ask.

Return ONLY valid JSON (no markdown code blocks, no explanations):
[
  {{
    "category": "Technical | Behavioral | Role-Specific",
    "question": "string"
  }}
]"""


def get_groq_api_key() -> str:
    """
    Retrieves the Groq API key from environment variables.
    
    Returns:
        The Groq API key string
        
    Raises:
        ValueError: If GROQ_API_KEY is not set in environment variables
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Please set it in your .env file or environment."
        )
    return api_key


def generate_questions_for_jd(job_description: str, resume_chunks: List[Union[str, any]]) -> str:
    """
    Generates interview questions using Groq LLM.
    
    ARCHITECTURE: No local ML models
    - Receives simple text chunks (strings) from keyword matching
    - Groq LLM handles all intelligence and relevance
    - No embeddings, no FAISS, no Document objects
    
    Flow:
    1. Get API key from environment
    2. Initialize ChatGroq LLM
    3. Convert resume chunks to text (handles both strings and objects)
    4. Format prompt with job description + resume context
    5. Call LLM with system + user messages
    6. Extract text content from AIMessage response
    
    Args:
        job_description: Job description text
        resume_chunks: List of strings (or objects with page_content) from keyword matching
        
    Returns:
        LLM response as string (contains JSON array of questions)
        
    Raises:
        ValueError: If GROQ_API_KEY is not set or resume context is empty
        Exception: If LLM call fails
    """
    try:
        # Get API key from environment
        api_key = get_groq_api_key()
        
        # Initialize LLM with Groq
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.4,  # Lower temperature for more consistent output
            groq_api_key=api_key
        )

        # Convert chunks to strings (handles both strings and Document-like objects)
        # No FAISS anymore - chunks are simple strings from keyword matching
        resume_texts = [
            chunk if isinstance(chunk, str) else (
                chunk.page_content if hasattr(chunk, "page_content") else str(chunk)
            )
            for chunk in resume_chunks
        ]
        resume_context = "\n\n".join(resume_texts)
        
        # Validate that we have resume context
        if not resume_context or not resume_context.strip():
            logger.warning("Resume context is empty or contains no text")
            raise ValueError("Resume context is empty. Cannot generate questions.")

        # Format prompt with job description and resume context
        prompt = QUESTION_PROMPT_TEMPLATE.format(
            job_description=job_description,
            resume_context=resume_context
        )

        # Prepare messages for LLM
        # System message sets the role and behavior
        # Human message contains the actual prompt
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        
        # Call LLM
        logger.info("Calling Groq LLM to generate questions...")
        response = llm.invoke(messages)

        # Extract content from AIMessage object
        # LangChain returns AIMessage objects, not plain strings
        if hasattr(response, 'content'):
            response_text = response.content
        elif isinstance(response, str):
            response_text = response
        else:
            # Fallback: try to convert to string
            response_text = str(response)
        
        logger.info(f"Received LLM response (length: {len(response_text)} chars)")
        return response_text
        
    except ValueError as e:
        # Re-raise validation errors
        raise
    except Exception as e:
        logger.error(f"Error calling Groq LLM: {str(e)}")
        raise Exception(f"Failed to generate questions: {str(e)}")
