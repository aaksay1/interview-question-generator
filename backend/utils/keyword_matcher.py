"""
Lightweight keyword-based chunk selection.

This replaces embeddings/FAISS for memory efficiency.
Uses simple keyword matching to find relevant resume chunks.
Groq LLM handles all intelligence - this is just a lightweight filter.
"""
import re
from typing import List
import logging

logger = logging.getLogger(__name__)


def extract_keywords(text: str, min_length: int = 4) -> set:
    """
    Extract meaningful keywords from text.
    
    Args:
        text: Text to extract keywords from
        min_length: Minimum keyword length
        
    Returns:
        Set of lowercase keywords
    """
    # Remove common stop words and extract words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }
    
    # Extract words (alphanumeric, at least min_length chars)
    words = re.findall(r'\b[a-zA-Z]{%d,}\b' % min_length, text.lower())
    
    # Filter out stop words and return unique keywords
    keywords = {word for word in words if word not in stop_words and len(word) >= min_length}
    
    return keywords


def score_chunk_relevance(chunk: str, job_keywords: set) -> float:
    """
    Score how relevant a chunk is to the job description using keyword matching.
    
    Args:
        chunk: Resume chunk text
        job_keywords: Set of keywords extracted from job description
        
    Returns:
        Relevance score (0.0 to 1.0)
    """
    if not job_keywords:
        return 0.0
    
    chunk_keywords = extract_keywords(chunk)
    
    # Calculate overlap
    if not chunk_keywords:
        return 0.0
    
    overlap = len(job_keywords & chunk_keywords)
    total_unique = len(job_keywords | chunk_keywords)
    
    # Jaccard similarity
    if total_unique == 0:
        return 0.0
    
    score = overlap / total_unique
    
    # Boost score if chunk contains multiple matching keywords
    if overlap > 0:
        score += (overlap / len(job_keywords)) * 0.3  # Bonus for high overlap
    
    return min(score, 1.0)  # Cap at 1.0


def select_relevant_chunks(chunks: List[str], job_description: str, k: int = 5) -> List[str]:
    """
    Select top k most relevant chunks using lightweight keyword matching.
    
    This replaces FAISS semantic search for memory efficiency.
    Groq LLM will handle all intelligence - this just filters chunks.
    
    Args:
        chunks: List of resume text chunks
        job_description: Job description text
        k: Number of chunks to return (default: 5)
        
    Returns:
        List of top k most relevant chunks
    """
    if not chunks:
        return []
    
    if len(chunks) <= k:
        # Return all chunks if we have fewer than k
        return chunks
    
    # Extract keywords from job description
    job_keywords = extract_keywords(job_description)
    
    if not job_keywords:
        # If no keywords, return first k chunks
        logger.warning("No keywords extracted from job description, returning first chunks")
        return chunks[:k]
    
    # Score each chunk
    scored_chunks = [
        (score_chunk_relevance(chunk, job_keywords), chunk)
        for chunk in chunks
    ]
    
    # Sort by score (descending) and take top k
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    selected = [chunk for _, chunk in scored_chunks[:k]]
    
    logger.info(f"Selected {len(selected)} chunks from {len(chunks)} using keyword matching")
    
    return selected
