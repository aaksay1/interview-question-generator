"""
Text chunking utilities optimized for resumes of different lengths.

Chunking strategy adapts based on resume length to optimize for:
- Short resumes: Preserve context with smaller chunks
- Medium resumes: Balanced chunking
- Long resumes: Efficient processing with larger chunks
"""
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
import logging

logger = logging.getLogger(__name__)


def chunk_resume_text(text: str, min_chunk_size: int = 500, max_chunk_size: int = 1500) -> List[str]:
    """
    Intelligently chunks resume text based on its length.
    
    Strategy:
    - Short resumes (< 2000 chars): Smaller chunks (500) with more overlap (150)
      → Preserves context for brief resumes
    - Medium resumes (2000-10000 chars): Standard chunks (1000) with overlap (200)
      → Balanced approach for typical resumes
    - Long resumes (> 10000 chars): Larger chunks (1500) with more overlap (300)
      → Efficient processing for detailed resumes
    
    Args:
        text: The resume text to chunk
        min_chunk_size: Minimum chunk size in characters (default: 500)
        max_chunk_size: Maximum chunk size in characters (default: 1500)
        
    Returns:
        List of text chunks ready for embedding and vectorstore
    """
    text_length = len(text)
    
    # Adjust chunking strategy based on resume length
    if text_length < 2000:
        # Short resume: smaller chunks, more overlap
        chunk_size = 500
        chunk_overlap = 150
        logger.info(f"Using small chunk strategy for short resume ({text_length} chars)")
    elif text_length < 10000:
        # Medium resume: standard chunking
        chunk_size = 1000
        chunk_overlap = 200
        logger.info(f"Using standard chunk strategy for medium resume ({text_length} chars)")
    else:
        # Long resume: larger chunks, more overlap
        chunk_size = 1500
        chunk_overlap = 300
        logger.info(f"Using large chunk strategy for long resume ({text_length} chars)")
    
    # Ensure chunk_size is within bounds
    chunk_size = max(min_chunk_size, min(chunk_size, max_chunk_size))
    chunk_overlap = min(chunk_overlap, chunk_size // 3)  # Overlap shouldn't exceed 1/3 of chunk size
    
    # Use RecursiveCharacterTextSplitter with smart separators
    # Tries to split on paragraphs first, then sentences, then words
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]  # Try to split on paragraphs first
    )
    
    chunks = splitter.split_text(text)
    logger.info(f"Split resume into {len(chunks)} chunks")
    
    return chunks
