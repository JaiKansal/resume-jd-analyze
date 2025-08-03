"""
Unit tests for resume parsing functionality
"""
import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
import fitz  # PyMuPDF

from resume_matcher_ai.resume_parser import (
    extract_text_from_pdf,
    clean_resume_text,
    validate_resume_content
)


class TestResumeParser(unittest.TestCase):
    """Test cases for resume parsing functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Sample resume text for testing
        self.sample_resume_text = """
John Doe
Software Engineer
john.doe@email.com | (555) 123-4567

EXPERIENCE
Senior Software Engineer | Tech Corp | 2020 - Present
• Developed web applications using Python and JavaScript
• Led team of 5 developers on major projects
• Improved system performance by 40%

Software Developer | StartupXYZ | 2018 - 2020
• Built REST APIs using Django and Flask
• Collaborated with cross-functional teams
• Implemented automated testing procedures

EDUCATION
Bachelor of Science in Computer Science
University of Technology | 2014 - 2018
GPA: 3.8/4.0

SKILLS
• Programming Languages: Python, JavaScript, Java, C++
• Frameworks: Django, React, Node.js
• Databases: PostgreSQL, MongoDB
• Tools: Git, Docker, AWS

PROJECTS
E-commerce Platform
• Built full-stack web application with 10,000+ users
• Technologies: React, Django, PostgreSQL
"""
        
        # Sample cleaned text for validation testing
        self.cleaned_resume_text = """John Doe
Software Engineer
john.doe@email.com | 555-123-4567

Experience:
Senior Software Engineer | Tech Corp | 2020 - Present
• Developed web applications using Python and JavaScript
• Led team of 5 developers on major projects
• Improved system performance by 40%

Software Developer | StartupXYZ | 2018 - 2020
• Built REST APIs using Django and Flask
• Collaborated with cross-functional teams
• Implemented automated testing procedures

Education:
Bachelor of Science in Computer Science
University of Technology | 2014 - 2018
GPA: 3.8/4.0

Skills:
• Programming Languages: Python, JavaScript, Java, C++
• Frameworks: Django, React, Node.js
• Databases: PostgreSQL, MongoDB
• Tools: Git, Docker, AWS

Projects:
E-commerce Platform
• Built full-stack web application with 10,000+ users
• Technologies: React, Django, PostgreSQL"""

    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temporary files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def create_test_pdf(self, content: str, filename: str = "test_resume.pdf") -> str:
        """Create a test PDF file with given content"""
        file_path = os.path.join(self.temp_dir, filename)
        
        # Create a simple PDF with the content
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), content, fontsize=12)
        doc.save(file_path)
        doc.close()
        
        return file_path

    def test_extract_text_from_pdf_success(self):
        """Test successful PDF text extraction"""
        # Create test PDF
        pdf_path = self.create_test_pdf(self.sample_resume_text)
        
        # Extract text
        result = extract_text_from_pdf(pdf_path)
        
        # Verify text was extracted
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        self.assertIn("John Doe", result)
        self.assertIn("Software Engineer", result)
        self.assertIn("john.doe@email.com", result)

    def test_extract_text_from_pdf_file_not_found(self):
        """Test error handling for non-existent file"""
        with self.assertRaises(FileNotFoundError) as context:
            extract_text_from_pdf("nonexistent_file.pdf")
        
        self.assertIn("Resume file not found", str(context.exception))

    def test_extract_text_from_pdf_invalid_extension(self):
        """Test error handling for non-PDF file"""
        # Create a text file with .txt extension
        txt_path = os.path.join(self.temp_dir, "test.txt")
        with open(txt_path, 'w') as f:
            f.write("This is not a PDF")
        
        with self.assertRaises(ValueError) as context:
            extract_text_from_pdf(txt_path)
        
        self.assertIn("File must be a PDF", str(context.exception))

    def test_extract_text_from_pdf_empty_pdf(self):
        """Test error handling for empty PDF"""
        # Create empty PDF
        empty_pdf_path = os.path.join(self.temp_dir, "empty.pdf")
        doc = fitz.open()
        doc.save(empty_pdf_path)
        doc.close()
        
        with self.assertRaises(ValueError) as context:
            extract_text_from_pdf(empty_pdf_path)
        
        self.assertIn("PDF file is empty", str(context.exception))

    def test_extract_text_from_pdf_no_text_content(self):
        """Test error handling for PDF with no extractable text"""
        # Create PDF with no text (just blank page)
        blank_pdf_path = os.path.join(self.temp_dir, "blank.pdf")
        doc = fitz.open()
        doc.new_page()  # Add blank page
        doc.save(blank_pdf_path)
        doc.close()
        
        with self.assertRaises(ValueError) as context:
            extract_text_from_pdf(blank_pdf_path)
        
        self.assertIn("No text could be extracted", str(context.exception))

    @patch('fitz.open')
    def test_extract_text_from_pdf_corrupted_file(self, mock_fitz_open):
        """Test error handling for corrupted PDF"""
        mock_fitz_open.side_effect = fitz.FileDataError("Corrupted file")
        
        # Create a dummy file to pass the existence check
        dummy_path = os.path.join(self.temp_dir, "corrupted.pdf")
        with open(dummy_path, 'w') as f:
            f.write("dummy")
        
        with self.assertRaises(ValueError) as context:
            extract_text_from_pdf(dummy_path)
        
        self.assertIn("Corrupted or invalid PDF file", str(context.exception))

    def test_clean_resume_text_basic_cleaning(self):
        """Test basic text cleaning functionality"""
        dirty_text = """John    Doe


Software   Engineer

john.doe@email.com   |   (555)   123-4567


EXPERIENCE


Senior Software Engineer"""
        
        cleaned = clean_resume_text(dirty_text)
        
        # Check that excessive whitespace is removed
        self.assertNotIn("    ", cleaned)  # No multiple spaces
        self.assertNotIn("\n\n\n", cleaned)  # No triple newlines
        
        # Check that content is preserved
        self.assertIn("John Doe", cleaned)
        self.assertIn("Software Engineer", cleaned)

    def test_clean_resume_text_bullet_points(self):
        """Test bullet point normalization"""
        text_with_bullets = """Skills:
• Python
· JavaScript
▪ Java
▫ C++
◦ Go"""
        
        cleaned = clean_resume_text(text_with_bullets)
        
        # All bullet points should be normalized to •
        self.assertIn("• Python", cleaned)
        self.assertIn("• JavaScript", cleaned)
        self.assertIn("• Java", cleaned)

    def test_clean_resume_text_phone_normalization(self):
        """Test phone number normalization"""
        text_with_phones = """Contact:
555 123 4567
(555) 123-4567
555.123.4567"""
        
        cleaned = clean_resume_text(text_with_phones)
        
        # Phone numbers should be normalized to xxx-xxx-xxxx format
        self.assertIn("555-123-4567", cleaned)

    def test_clean_resume_text_empty_input(self):
        """Test cleaning empty or None input"""
        self.assertEqual(clean_resume_text(""), "")
        self.assertEqual(clean_resume_text(None), "")

    def test_clean_resume_text_excessive_punctuation(self):
        """Test removal of excessive punctuation"""
        text_with_punctuation = """Summary....
Experience-------
Skills___________"""
        
        cleaned = clean_resume_text(text_with_punctuation)
        
        self.assertIn("Summary...", cleaned)
        self.assertIn("Experience---", cleaned)
        self.assertIn("Skills___", cleaned)

    def test_validate_resume_content_valid_resume(self):
        """Test validation of valid resume content"""
        result = validate_resume_content(self.cleaned_resume_text)
        self.assertTrue(result)

    def test_validate_resume_content_empty_text(self):
        """Test validation of empty text"""
        self.assertFalse(validate_resume_content(""))
        self.assertFalse(validate_resume_content(None))

    def test_validate_resume_content_too_short(self):
        """Test validation of text that's too short"""
        short_text = "John Doe"
        self.assertFalse(validate_resume_content(short_text))

    def test_validate_resume_content_insufficient_words(self):
        """Test validation of text with too few words"""
        few_words = "John Doe Software Engineer Email Phone"
        self.assertFalse(validate_resume_content(few_words))

    def test_validate_resume_content_missing_indicators(self):
        """Test validation of text without resume indicators"""
        non_resume_text = """This is just a regular document with lots of text
that doesn't contain any resume-specific information or keywords.
It has enough words and length but lacks the structure and content
that would indicate it's actually a resume document."""
        
        self.assertFalse(validate_resume_content(non_resume_text))

    def test_validate_resume_content_with_email_and_experience(self):
        """Test validation with minimal but valid resume indicators"""
        minimal_resume = """John Smith
john.smith@email.com
555-123-4567

Work Experience:
Software Developer at Tech Company from 2020 to present.
Developed applications and worked with teams.

Education:
Bachelor's degree in Computer Science from University.

Skills:
Python, JavaScript, and other programming languages.
Experience with databases and web development frameworks."""
        
        self.assertTrue(validate_resume_content(minimal_resume))

    def test_validate_resume_content_poor_character_distribution(self):
        """Test validation of text with poor character distribution"""
        poor_text = "@@@@####$$$$%%%%^^^^&&&&****(((())))____++++=====----"
        # Add enough length to pass length checks
        poor_text = poor_text * 10 + " some words here to meet word count requirements"
        
        self.assertFalse(validate_resume_content(poor_text))

    def test_validate_resume_content_insufficient_sentences(self):
        """Test validation of text with too few meaningful sentences"""
        few_sentences = """John Doe. Email. Phone. Experience. Education."""
        # Add more words to meet word count
        few_sentences += " " + " ".join(["word"] * 50)
        
        self.assertFalse(validate_resume_content(few_sentences))

    def test_integration_pdf_to_validation(self):
        """Test complete pipeline from PDF extraction to validation"""
        # Create test PDF with valid resume content
        pdf_path = self.create_test_pdf(self.sample_resume_text)
        
        # Extract text
        extracted_text = extract_text_from_pdf(pdf_path)
        
        # Clean text
        cleaned_text = clean_resume_text(extracted_text)
        
        # Validate content
        is_valid = validate_resume_content(cleaned_text)
        
        # All steps should succeed
        self.assertIsInstance(extracted_text, str)
        self.assertGreater(len(extracted_text), 0)
        self.assertIsInstance(cleaned_text, str)
        self.assertTrue(is_valid)

    def test_multiple_page_pdf(self):
        """Test PDF with multiple pages"""
        # Create multi-page PDF
        pdf_path = os.path.join(self.temp_dir, "multipage.pdf")
        doc = fitz.open()
        
        # Page 1
        page1 = doc.new_page()
        page1.insert_text((50, 50), "John Doe\nSoftware Engineer\nPage 1 content", fontsize=12)
        
        # Page 2
        page2 = doc.new_page()
        page2.insert_text((50, 50), "Experience and Education\nPage 2 content", fontsize=12)
        
        doc.save(pdf_path)
        doc.close()
        
        # Extract text
        result = extract_text_from_pdf(pdf_path)
        
        # Should contain content from both pages
        self.assertIn("Page 1 content", result)
        self.assertIn("Page 2 content", result)


if __name__ == '__main__':
    unittest.main()