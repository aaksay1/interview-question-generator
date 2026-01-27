"""
Validation utilities for file uploads and input validation.

Validates:
- File size (max 5MB)
- File type (PDF only)
- Job description length (10-10,000 characters)
"""
from fastapi import HTTPException
from typing import BinaryIO

# Constants
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
MIN_JOB_DESCRIPTION_LENGTH = 10
MAX_JOB_DESCRIPTION_LENGTH = 10000


def validate_file_size(file: BinaryIO, max_size: int = MAX_FILE_SIZE) -> None:
    """
    Validates that the uploaded file does not exceed the maximum size.
    
    Args:
        file: The file object to validate
        max_size: Maximum allowed file size in bytes (default: 5MB)
        
    Raises:
        HTTPException: 413 status if file size exceeds the limit
    """
    # Read file to check size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File size ({file_size / (1024*1024):.2f}MB) exceeds maximum allowed size ({max_size / (1024*1024)}MB)"
        )


def validate_pdf_type(filename: str) -> None:
    """
    Validates that the uploaded file is a PDF.
    
    Args:
        filename: The name of the uploaded file
        
    Raises:
        HTTPException: 400 status if file is not a PDF
    """
    if not filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are allowed."
        )


def validate_job_description(job_description: str) -> None:
    """
    Validates that the job description meets length requirements.
    
    Args:
        job_description: The job description text to validate
        
    Raises:
        HTTPException: 400 status if job description is invalid
    """
    if not job_description or not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )
    
    job_description = job_description.strip()
    
    if len(job_description) < MIN_JOB_DESCRIPTION_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Job description is too short. Minimum {MIN_JOB_DESCRIPTION_LENGTH} characters required."
        )
    
    if len(job_description) > MAX_JOB_DESCRIPTION_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Job description is too long. Maximum {MAX_JOB_DESCRIPTION_LENGTH} characters allowed."
        )
