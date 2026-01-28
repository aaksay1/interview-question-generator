"""
Simple text chunking for resumes.

Uses lightweight text splitting - no ML models required.
All intelligence is handled by Groq LLM.
"""
import re
from typing import List
import logging

logger = logging.getLogger(__name__)


def chunk_resume_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Split resume text into chunks using simple character-based splitting.
    
    This is a lightweight alternative to RecursiveCharacterTextSplitter.
    No ML dependencies - just simple text processing.
    
    Args:
        text: The resume text to chunk
        chunk_size: Target chunk size in characters (default: 1000)
        chunk_overlap: Overlap between chunks in characters (default: 200)
        
    Returns:
        List of text chunks
    """
    if not text or len(text.strip()) == 0:
        return []
    
    text = text.strip()
    text_length = len(text)
    
    # Adjust chunk size based on text length for efficiency
    if text_length < 2000:
        chunk_size = 500
        chunk_overlap = 100
    elif text_length < 10000:
        chunk_size = 1000
        chunk_overlap = 200
    else:
        chunk_size = 1200
        chunk_overlap = 250
    
    chunks = []
    start = 0
    
    while start < text_length:
        # Calculate end position
        end = start + chunk_size
        
        if end >= text_length:
            # Last chunk - take remaining text
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break
        
        # Try to break at a sentence boundary (period, newline, etc.)
        # Look for break points near the end
        break_chars = ['\n\n', '\n', '. ', '! ', '? ', '; ']
        best_break = end
        
        for break_char in break_chars:
            # Look backwards from end for a break character
            break_pos = text.rfind(break_char, start, end)
            if break_pos != -1 and break_pos > start + chunk_size * 0.5:  # Don't break too early
                best_break = break_pos + len(break_char)
                break
        
        # Extract chunk
        chunk = text[start:best_break].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = best_break - chunk_overlap
        if start < 0:
            start = best_break
    
    logger.info(f"Split resume into {len(chunks)} chunks (avg size: {sum(len(c) for c in chunks) // len(chunks) if chunks else 0} chars)")
    
    return chunks
