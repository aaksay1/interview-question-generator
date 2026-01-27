"""
PDF parsing utilities with robust error handling.

Handles PDF text extraction with support for:
- Blank pages (skipped with warning)
- Corrupted files (clear error messages)
- Image-based PDFs (warning if text is minimal)
"""
import logging
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

logger = logging.getLogger(__name__)


def pdf_to_text(file_path: str) -> str:
    """
    Extracts text from a PDF file with error handling.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text from the PDF (pages joined with double newlines)
        
    Raises:
        ValueError: If PDF cannot be read or contains no extractable text
        PdfReadError: If PDF is corrupted or invalid
    """
    try:
        reader = PdfReader(file_path)
        text_parts = []
        
        # Handle empty PDFs
        if len(reader.pages) == 0:
            raise ValueError("PDF file contains no pages")
        
        # Extract text from each page, skipping blank pages
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_parts.append(page_text.strip())
                else:
                    logger.warning(f"Page {i + 1} appears to be blank or contains no extractable text")
            except Exception as e:
                logger.warning(f"Error extracting text from page {i + 1}: {str(e)}")
                continue
        
        if not text_parts:
            raise ValueError("PDF file contains no extractable text")
        
        extracted_text = "\n\n".join(text_parts)
        
        # Validate that we got meaningful text
        if len(extracted_text.strip()) < 50:
            logger.warning("Extracted text is very short. PDF may be image-based or corrupted.")
        
        return extracted_text
        
    except PdfReadError as e:
        logger.error(f"Error reading PDF file: {str(e)}")
        raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error parsing PDF: {str(e)}")
        raise ValueError(f"Failed to parse PDF file: {str(e)}")
