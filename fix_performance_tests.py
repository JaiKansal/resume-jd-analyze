#!/usr/bin/env python3
"""
Script to fix performance test mocking
"""

# Read the performance test file
with open('test_performance_30_second.py', 'r') as f:
    content = f.read()

# Replace all instances of the old mocking pattern with the new one
old_pattern = """            # Mock both validation and PDF extraction
            with patch('resume_matcher_ai.main._validate_resume_file') as mock_validate, \\
                 patch('resume_matcher_ai.resume_parser.extract_text_from_pdf') as mock_extract:
                mock_validate.return_value = True"""

new_pattern = """            # Mock all validation and PDF extraction functions
            with patch('resume_matcher_ai.main._validate_resume_file') as mock_validate, \\
                 patch('resume_matcher_ai.resume_parser._validate_pdf_file_comprehensive') as mock_pdf_validate, \\
                 patch('resume_matcher_ai.resume_parser.extract_text_from_pdf') as mock_extract:
                mock_validate.return_value = True
                mock_pdf_validate.return_value = None  # This function returns None on success"""

# Replace all occurrences
content = content.replace(old_pattern, new_pattern)

# Also fix the pattern that doesn't have the main validation mock
old_pattern2 = """                # Mock both validation and PDF extraction
                with patch('resume_matcher_ai.main._validate_resume_file') as mock_validate, \\
                     patch('resume_matcher_ai.resume_parser.extract_text_from_pdf') as mock_extract:
                    mock_validate.return_value = True"""

new_pattern2 = """                # Mock all validation and PDF extraction functions
                with patch('resume_matcher_ai.main._validate_resume_file') as mock_validate, \\
                     patch('resume_matcher_ai.resume_parser._validate_pdf_file_comprehensive') as mock_pdf_validate, \\
                     patch('resume_matcher_ai.resume_parser.extract_text_from_pdf') as mock_extract:
                    mock_validate.return_value = True
                    mock_pdf_validate.return_value = None  # This function returns None on success"""

content = content.replace(old_pattern2, new_pattern2)

# Write the updated content back
with open('test_performance_30_second.py', 'w') as f:
    f.write(content)

print("Fixed performance test mocking patterns")