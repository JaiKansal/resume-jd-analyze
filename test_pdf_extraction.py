#!/usr/bin/env python3
"""
Test script to verify PDF extraction functionality
"""

from resume_matcher_ai.resume_parser import extract_text_from_pdf

def test_pdf_extraction_without_pymupdf():
    """Test that PDF extraction properly handles missing PyMuPDF"""
    print("Testing PDF extraction without PyMuPDF...")
    
    try:
        result = extract_text_from_pdf("sample_resume.pdf")
        print("❌ Expected ImportError but function succeeded")
    except ImportError as e:
        print(f"✓ Correctly raised ImportError: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_pdf_extraction_without_pymupdf()