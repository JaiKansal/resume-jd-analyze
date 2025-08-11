"""
PDF text extraction utilities
"""

import PyPDF2
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_file) -> Optional[str]:
    """Extract text from uploaded PDF file"""
    
    try:
        # Reset file pointer
        pdf_file.seek(0)
        
        # Create PDF reader
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        
        # Extract text from all pages
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"
        
        # Clean up text
        text = text.strip()
        
        if not text:
            logger.warning("No text extracted from PDF")
            return None
        
        logger.info(f"Extracted {len(text)} characters from PDF")
        return text
        
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        return None

def validate_pdf_file(pdf_file) -> bool:
    """Validate if uploaded file is a valid PDF"""
    
    try:
        pdf_file.seek(0)
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        
        # Check if we can read at least one page
        if len(pdf_reader.pages) > 0:
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(f"PDF validation failed: {e}")
        return False