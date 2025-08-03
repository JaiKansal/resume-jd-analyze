#!/usr/bin/env python3
"""
Test CLI functionality without PDF dependencies
"""
import os
import sys
from unittest.mock import patch, MagicMock
from resume_matcher_ai.main import (
    _validate_resume_file, 
    display_results, 
    handle_errors,
    _check_api_configuration,
    _ask_continue
)
from resume_matcher_ai.utils import MatchResult

def test_cli_validation():
    """Test CLI validation functions"""
    print("Testing CLI validation functions...")
    
    # Test file validation with non-existent file
    result = _validate_resume_file("nonexistent.pdf")
    print(f"✅ Non-existent file validation: {result}")
    assert isinstance(result, str), "Should return error message for non-existent file"
    
    # Test file validation with non-PDF file
    result = _validate_resume_file("sample_resume.txt")
    print(f"✅ Non-PDF file validation: {result}")
    assert isinstance(result, str), "Should return error message for non-PDF file"
    
    print("✅ All validation tests passed!")

def test_result_display():
    """Test result display formatting"""
    print("\nTesting result display formatting...")
    
    # Test with strong match
    strong_match = MatchResult(
        score=85,
        match_category="Strong Match",
        matching_skills=["Python", "React.js", "Node.js", "AWS"],
        missing_skills=["Docker", "Kubernetes"],
        skill_gaps={
            "Critical": ["Docker"],
            "Important": ["Kubernetes", "TypeScript"],
            "Nice-to-have": ["GraphQL"]
        },
        suggestions=[
            "Add Docker experience to your resume with specific examples of containerization projects",
            "Include Kubernetes skills in your technical skills section and mention orchestration experience",
            "Consider adding a DevOps section highlighting containerization and cloud deployment experience"
        ],
        processing_time=2.1
    )
    
    print("Displaying strong match results:")
    display_results(strong_match)
    
    # Test with poor match
    poor_match = MatchResult(
        score=25,
        match_category="Poor Match",
        matching_skills=["JavaScript"],
        missing_skills=["Python", "React", "Node.js", "AWS", "Docker"],
        skill_gaps={
            "Critical": ["Python", "React", "Node.js"],
            "Important": ["AWS", "Docker"],
            "Nice-to-have": ["TypeScript", "GraphQL"]
        },
        suggestions=[
            "Consider learning Python as it's essential for this role",
            "Gain experience with React.js for frontend development",
            "Add Node.js backend development skills to your skillset"
        ],
        processing_time=1.8
    )
    
    print("\nDisplaying poor match results:")
    display_results(poor_match)
    
    # Test with no skill gaps
    perfect_match = MatchResult(
        score=95,
        match_category="Strong Match",
        matching_skills=["Python", "React.js", "Node.js", "AWS", "Docker", "Kubernetes"],
        missing_skills=[],
        skill_gaps={
            "Critical": [],
            "Important": [],
            "Nice-to-have": []
        },
        suggestions=[
            "Your resume shows excellent alignment. Consider adding quantifiable achievements",
            "Optimize keyword usage by incorporating more industry-specific terminology",
            "Add metrics to demonstrate the impact of your technical contributions"
        ],
        processing_time=1.5
    )
    
    print("\nDisplaying perfect match results:")
    display_results(perfect_match)
    
    print("✅ Result display tests completed!")

def test_error_handling():
    """Test error handling with different error types"""
    print("\nTesting error handling...")
    
    # Test API key error
    print("Testing API key error handling:")
    handle_errors(Exception("Invalid API key. Please check your PERPLEXITY_API_KEY environment variable."))
    
    # Test rate limit error
    print("\nTesting rate limit error handling:")
    handle_errors(Exception("Rate limit exceeded. Please wait 60 seconds before retrying."))
    
    # Test network error
    print("\nTesting network error handling:")
    handle_errors(Exception("Failed to connect to Perplexity API. Please check your internet connection."))
    
    # Test PDF error
    print("\nTesting PDF error handling:")
    handle_errors(Exception("Error processing PDF file: corrupted or invalid PDF file"))
    
    # Test generic error
    print("\nTesting generic error handling:")
    handle_errors(Exception("Something unexpected happened"))
    
    print("✅ Error handling tests completed!")

def test_api_configuration():
    """Test API configuration checking"""
    print("\nTesting API configuration...")
    
    # Test without API key
    with patch.dict(os.environ, {}, clear=True):
        result = _check_api_configuration()
        print(f"✅ No API key test: {result}")
        assert result == False, "Should return False when no API key is set"
    
    print("✅ API configuration tests completed!")

def test_continue_prompt():
    """Test the continue prompt functionality"""
    print("\nTesting continue prompt...")
    
    # Mock user input for 'yes'
    with patch('builtins.input', return_value='y'):
        result = _ask_continue()
        print(f"✅ Continue prompt (yes): {result}")
        assert result == True, "Should return True for 'y' input"
    
    # Mock user input for 'no'
    with patch('builtins.input', return_value='n'):
        result = _ask_continue()
        print(f"✅ Continue prompt (no): {result}")
        assert result == False, "Should return False for 'n' input"
    
    print("✅ Continue prompt tests completed!")

def run_all_tests():
    """Run all CLI tests"""
    print("=" * 60)
    print("RUNNING CLI FUNCTIONALITY TESTS")
    print("=" * 60)
    
    test_cli_validation()
    test_result_display()
    test_error_handling()
    test_api_configuration()
    test_continue_prompt()
    
    print("\n" + "=" * 60)
    print("✅ ALL CLI TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()