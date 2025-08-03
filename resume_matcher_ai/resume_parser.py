"""
Resume parsing functionality for extracting text from PDF files
"""
# Try lightweight PDF processing libraries for Streamlit Cloud compatibility
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    PyPDF2 = None

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    pdfplumber = None

# PyMuPDF disabled for Streamlit Cloud compatibility
PYMUPDF_AVAILABLE = False
fitz = None

import re
import os
from typing import Optional


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF resume using multiple PDF processing libraries
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text content from the PDF
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is not a valid PDF or is corrupted
        PermissionError: If the file cannot be accessed due to permissions
        Exception: For other PDF processing errors
    """
    # Comprehensive file validation
    _validate_pdf_file_comprehensive(file_path)
    
    # Try different PDF processing libraries in order of preference
    extraction_errors = []
    
    # Try PyMuPDF first (best quality)
    if PYMUPDF_AVAILABLE:
        try:
            return _extract_with_pymupdf(file_path)
        except Exception as e:
            extraction_errors.append(f"PyMuPDF failed: {str(e)}")
    
    # Try pdfplumber second (good for complex layouts)
    if PDFPLUMBER_AVAILABLE:
        try:
            return _extract_with_pdfplumber(file_path)
        except Exception as e:
            extraction_errors.append(f"pdfplumber failed: {str(e)}")
    
    # Try PyPDF2 as last resort (basic but reliable)
    if PYPDF2_AVAILABLE:
        try:
            return _extract_with_pypdf2(file_path)
        except Exception as e:
            extraction_errors.append(f"PyPDF2 failed: {str(e)}")
    
    # If all methods failed
    error_msg = f"Failed to extract text from PDF: {file_path}\n"
    error_msg += "All PDF processing methods failed:\n"
    for error in extraction_errors:
        error_msg += f"• {error}\n"
    
    if not any([PYMUPDF_AVAILABLE, PDFPLUMBER_AVAILABLE, PYPDF2_AVAILABLE]):
        error_msg += "\nNo PDF processing libraries are available. Please install one of:\n"
        error_msg += "• pip install PyMuPDF\n"
        error_msg += "• pip install pdfplumber\n"
        error_msg += "• pip install PyPDF2\n"
    
    raise Exception(error_msg)


def _extract_with_pymupdf(file_path: str) -> str:
    """Extract text using PyMuPDF (fitz)"""
    
    try:
        # Open the PDF document with error handling
        doc = None
        try:
            doc = fitz.open(file_path)
        except fitz.FileDataError as e:
            raise ValueError(
                f"The PDF file appears to be corrupted or invalid: {file_path}\n"
                f"Error details: {str(e)}\n"
                f"Please try with a different PDF file or re-save your resume as a new PDF."
            )
        except fitz.EmptyFileError:
            raise ValueError(
                f"The PDF file is empty: {file_path}\n"
                f"Please ensure your resume PDF contains content."
            )
        except Exception as e:
            raise Exception(
                f"Failed to open PDF file: {file_path}\n"
                f"Error: {str(e)}\n"
                f"Please check if the file is a valid PDF and not password-protected."
            )
        
        # Check if PDF is empty or has no pages
        if doc.page_count == 0:
            doc.close()
            raise ValueError(
                f"PDF file has no pages: {file_path}\n"
                f"Please ensure your resume PDF contains at least one page with content."
            )
        
        # Extract text from all pages with enhanced error handling
        text_content = []
        extraction_errors = []
        
        for page_num in range(doc.page_count):
            try:
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():  # Only add non-empty pages
                    text_content.append(text)
            except Exception as e:
                extraction_errors.append(f"Page {page_num + 1}: {str(e)}")
                continue
        
        doc.close()
        
        # Check if any text was extracted
        full_text = "\n".join(text_content)
        
        if not full_text.strip():
            error_msg = f"No text could be extracted from the PDF: {file_path}\n"
            if extraction_errors:
                error_msg += f"Extraction errors encountered:\n" + "\n".join(extraction_errors) + "\n"
            error_msg += (
                "This could happen if:\n"
                "• The PDF contains only images (scanned document)\n"
                "• The PDF is password-protected\n"
                "• The PDF uses unsupported fonts or encoding\n"
                "• The PDF file is corrupted\n\n"
                "Solutions:\n"
                "• Try re-saving your resume as a new PDF\n"
                "• Ensure the PDF contains selectable text (not just images)\n"
                "• Remove any password protection from the PDF"
            )
            raise ValueError(error_msg)
        
        # Validate extracted content quality
        if len(full_text.strip()) < 50:
            raise ValueError(
                f"Extracted text is too short ({len(full_text)} characters): {file_path}\n"
                f"This may indicate a problem with the PDF content or format.\n"
                f"Please ensure your resume contains substantial text content."
            )
        
        return full_text
        
    except (ValueError, FileNotFoundError, PermissionError, ImportError):
        # Re-raise our custom exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected exceptions with helpful context
        raise Exception(
            f"Unexpected error while processing PDF file: {file_path}\n"
            f"Error: {str(e)}\n"
            f"Please try with a different PDF file or contact support if the problem persists."
        )


def _extract_with_pdfplumber(file_path: str) -> str:
    """Extract text using pdfplumber"""
    text_content = []
    
    with pdfplumber.open(file_path) as pdf:
        if len(pdf.pages) == 0:
            raise ValueError(f"PDF file has no pages: {file_path}")
        
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                text_content.append(text)
    
    full_text = "\n".join(text_content)
    
    if not full_text.strip():
        raise ValueError(f"No text could be extracted from PDF: {file_path}")
    
    if len(full_text.strip()) < 50:
        raise ValueError(f"Extracted text is too short: {file_path}")
    
    return full_text


def _extract_with_pypdf2(file_path: str) -> str:
    """Extract text using PyPDF2"""
    text_content = []
    
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        if len(pdf_reader.pages) == 0:
            raise ValueError(f"PDF file has no pages: {file_path}")
        
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text and text.strip():
                text_content.append(text)
    
    full_text = "\n".join(text_content)
    
    if not full_text.strip():
        raise ValueError(f"No text could be extracted from PDF: {file_path}")
    
    if len(full_text.strip()) < 50:
        raise ValueError(f"Extracted text is too short: {file_path}")
    
    return full_text


def _validate_pdf_file_comprehensive(file_path: str) -> None:
    """
    Comprehensive PDF file validation with detailed error messages
    
    Args:
        file_path: Path to the PDF file to validate
        
    Raises:
        FileNotFoundError: If file doesn't exist with helpful suggestions
        ValueError: If file is invalid with specific reasons
        PermissionError: If file cannot be accessed
    """
    # Check if file path is provided
    if not file_path or not file_path.strip():
        raise ValueError("No file path provided. Please specify a valid PDF file path.")
    
    # Normalize the file path
    file_path = os.path.expanduser(file_path.strip())
    
    # Check if file exists
    if not os.path.exists(file_path):
        # Provide helpful suggestions based on the path
        suggestions = []
        
        # Check if it's a relative path issue
        if not os.path.isabs(file_path):
            abs_path = os.path.abspath(file_path)
            suggestions.append(f"• Try using the absolute path: {abs_path}")
        
        # Check if parent directory exists
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            suggestions.append(f"• The directory doesn't exist: {parent_dir}")
        
        # Check for common file extension issues
        if not file_path.lower().endswith('.pdf'):
            suggestions.append("• Make sure the file has a .pdf extension")
        
        # Check if similar files exist in the directory
        if parent_dir and os.path.exists(parent_dir):
            try:
                files = os.listdir(parent_dir)
                pdf_files = [f for f in files if f.lower().endswith('.pdf')]
                if pdf_files:
                    suggestions.append(f"• PDF files found in directory: {', '.join(pdf_files[:3])}")
            except PermissionError:
                suggestions.append("• Cannot access the directory due to permissions")
        
        error_msg = f"Resume file not found: {file_path}\n"
        if suggestions:
            error_msg += "Suggestions:\n" + "\n".join(suggestions)
        
        raise FileNotFoundError(error_msg)
    
    # Check if it's a file (not a directory)
    if os.path.isdir(file_path):
        raise ValueError(
            f"The specified path is a directory, not a file: {file_path}\n"
            f"Please specify the full path to your PDF resume file."
        )
    
    # Check file extension
    if not file_path.lower().endswith('.pdf'):
        file_ext = os.path.splitext(file_path)[1].lower()
        error_msg = f"File must be a PDF (found {file_ext or 'no extension'}): {file_path}\n"
        
        if file_ext in ['.doc', '.docx']:
            error_msg += "Word documents are not supported. Please save your resume as a PDF."
        elif file_ext in ['.txt', '.rtf']:
            error_msg += "Text files are not supported. Please save your resume as a PDF."
        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
            error_msg += "Image files are not supported. Please save your resume as a PDF with selectable text."
        else:
            error_msg += "Please ensure your resume is saved as a PDF file."
        
        raise ValueError(error_msg)
    
    # Check file permissions
    if not os.access(file_path, os.R_OK):
        raise PermissionError(
            f"Cannot read the file due to insufficient permissions: {file_path}\n"
            f"Please check the file permissions and ensure you have read access."
        )
    
    # Check file size
    try:
        file_size = os.path.getsize(file_path)
        
        if file_size == 0:
            raise ValueError(
                f"The PDF file is empty (0 bytes): {file_path}\n"
                f"Please ensure your resume PDF contains content."
            )
        
        # Check for reasonable file size limits
        max_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_size:
            size_mb = file_size / (1024 * 1024)
            raise ValueError(
                f"PDF file is too large ({size_mb:.1f}MB, maximum 50MB): {file_path}\n"
                f"Please compress your PDF or use a smaller file."
            )
        
        # Warn about very small files that might not contain much content
        min_size = 1024  # 1KB
        if file_size < min_size:
            # This is a warning, not an error - let the text extraction handle it
            pass
            
    except OSError as e:
        raise Exception(
            f"Cannot access file information: {file_path}\n"
            f"Error: {str(e)}\n"
            f"Please check if the file exists and is accessible."
        )


def clean_resume_text(raw_text: str) -> str:
    """
    Remove formatting artifacts and normalize text
    
    Args:
        raw_text: Raw text extracted from PDF
        
    Returns:
        Cleaned and normalized text
    """
    if not raw_text:
        return ""
    
    text = raw_text
    
    # Remove excessive whitespace and normalize line breaks
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple empty lines to double
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    
    # Remove common PDF artifacts (but preserve bullet points)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)  # Control characters
    
    # Clean up bullet points and formatting - normalize first, then format
    text = re.sub(r'[·▪▫◦‣⁃]', '•', text)  # Normalize bullet points to standard bullet
    text = re.sub(r'^[\s]*[•\-\*]+\s*', '• ', text, flags=re.MULTILINE)  # Normalize list items
    
    # Remove excessive punctuation
    text = re.sub(r'[.]{3,}', '...', text)  # Multiple dots
    text = re.sub(r'[-]{3,}', '---', text)  # Multiple dashes
    text = re.sub(r'[_]{3,}', '___', text)  # Multiple underscores
    
    # Clean up email and phone formatting artifacts
    text = re.sub(r'(\w+)@(\w+)', r'\1@\2', text)  # Fix broken emails
    text = re.sub(r'(\d{3})\s*[-.]?\s*(\d{3})\s*[-.]?\s*(\d{4})', r'\1-\2-\3', text)  # Normalize phone numbers
    
    # Remove page numbers and headers/footers (common patterns)
    text = re.sub(r'^\s*Page\s+\d+\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)  # Standalone numbers
    
    # Clean up section headers (remove excessive formatting)
    text = re.sub(r'^([A-Z\s]{3,}):?\s*$', lambda m: m.group(1).title() + ':', text, flags=re.MULTILINE)
    
    # Remove excessive blank lines again after all cleaning
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Trim and ensure single trailing newline
    text = text.strip()
    
    return text


def validate_resume_content(text: str) -> bool:
    """
    Ensure extracted text is meaningful and contains resume-like content
    
    Args:
        text: Cleaned text content
        
    Returns:
        True if content appears to be a valid resume, False otherwise
    """
    if not text or not isinstance(text, str):
        return False
    
    # Check minimum length (resumes should have substantial content)
    if len(text.strip()) < 100:
        return False
    
    # Check word count (typical resumes have 200+ words)
    words = text.split()
    if len(words) < 50:
        return False
    
    # Look for common resume indicators (at least 2 should be present)
    resume_indicators = [
        r'\b(experience|work\s+experience|employment)\b',
        r'\b(education|degree|university|college|school)\b',
        r'\b(skills|technical\s+skills|competencies)\b',
        r'\b(email|phone|address|contact)\b',
        r'\b(resume|cv|curriculum\s+vitae)\b',
        r'\b(objective|summary|profile)\b',
        r'\b(projects?|achievements?|accomplishments?)\b',
        r'\b(certifications?|licenses?|awards?)\b',
        r'\b(languages?|references?)\b',
        r'\d{4}\s*[-–]\s*(\d{4}|present|current)',  # Date ranges
        r'@\w+\.\w+',  # Email pattern
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'  # Phone pattern
    ]
    
    indicator_count = 0
    text_lower = text.lower()
    
    for pattern in resume_indicators:
        if re.search(pattern, text_lower, re.IGNORECASE):
            indicator_count += 1
    
    # Require at least 2 resume indicators
    if indicator_count < 2:
        return False
    
    # Check for reasonable text structure (not just random characters)
    # Count sentences (rough estimate)
    sentences = re.split(r'[.!?]+', text)
    meaningful_sentences = [s for s in sentences if len(s.strip().split()) >= 3]
    
    if len(meaningful_sentences) < 5:
        return False
    
    # Check character distribution (should be mostly letters, numbers, and common punctuation)
    total_chars = len(text)
    alphanumeric_chars = len(re.findall(r'[a-zA-Z0-9]', text))
    
    if total_chars > 0 and (alphanumeric_chars / total_chars) < 0.6:
        return False
    
    return True