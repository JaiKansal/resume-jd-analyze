#!/usr/bin/env python3
"""
Basic test for CLI functionality
"""
import os
import sys
from unittest.mock import patch, MagicMock
from resume_matcher_ai.main import get_user_input, _validate_resume_file, display_results
from resume_matcher_ai.utils import MatchResult

def test_input_validation():
    """Test input validation functions"""
    print("Testing input validation...")
    
    # Test file validation with non-existent file
    result = _validate_resume_file("nonexistent.pdf")
    print(f"Non-existent file validation: {result}")
    assert isinstance(result, str), "Should return error message for non-existent file"
    
    # Test file validation with non-PDF file
    result = _validate_resume_file("sample_resume.txt")
    print(f"Non-PDF file validation: {result}")
    assert isinstance(result, str), "Should return error message for non-PDF file"
    
    print("✅ Input validation tests passed!")

def test_result_display():
    """Test result display formatting"""
    print("\nTesting result display...")
    
    # Create mock results
    mock_results = MatchResult(
        score=75,
        match_category="Strong Match",
        matching_skills=["Python", "React.js", "Node.js"],
        missing_skills=["Docker", "Kubernetes"],
        skill_gaps={
            "Critical": ["Docker"],
            "Important": ["Kubernetes", "TypeScript"],
            "Nice-to-have": ["GraphQL"]
        },
        suggestions=[
            "Add Docker experience to your resume with specific examples",
            "Include Kubernetes skills in your technical skills section",
            "Consider adding a DevOps section highlighting containerization experience"
        ],
        processing_time=2.5
    )
    
    print("Displaying mock results:")
    display_results(mock_results)
    print("✅ Result display test completed!")

def test_cli_components():
    """Test individual CLI components"""
    print("\nTesting CLI components...")
    
    # Test validation functions
    test_input_validation()
    
    # Test display functions
    test_result_display()
    
    print("\n✅ All CLI component tests passed!")

if __name__ == "__main__":
    test_cli_components()