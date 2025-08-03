#!/usr/bin/env python3
"""
Script to fix integration test mocking with correct import path
"""

# Read the integration test file
with open('test_integration_pipeline.py', 'r') as f:
    content = f.read()

# Replace the incorrect mocking path with the correct one
old_pattern = "patch('resume_matcher_ai.resume_parser.extract_text_from_pdf')"
new_pattern = "patch('resume_matcher_ai.main.extract_text_from_pdf')"

# Replace all occurrences
content = content.replace(old_pattern, new_pattern)

# Write the updated content back
with open('test_integration_pipeline.py', 'w') as f:
    f.write(content)

print("Fixed integration test mocking paths")