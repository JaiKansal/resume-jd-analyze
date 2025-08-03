#!/usr/bin/env python3
"""
Test script for Perplexity API integration in matcher.py
"""
import os
import sys
from unittest.mock import Mock, patch
import json

# Add the resume_matcher_ai directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resume_matcher_ai'))

from resume_matcher_ai.matcher import (
    call_perplexity_api,
    analyze_match,
    calculate_score,
    identify_gaps,
    generate_suggestions,
    _parse_api_response,
    _fallback_text_parsing
)

def test_parse_api_response():
    """Test JSON response parsing"""
    print("Testing API response parsing...")
    
    # Test valid JSON response
    valid_json = '''
    {
        "compatibility_score": 75,
        "matching_skills": ["Python", "Machine Learning", "SQL"],
        "missing_skills": ["Docker", "Kubernetes"],
        "skill_gaps": {
            "Critical": ["Docker"],
            "Important": ["Kubernetes"],
            "Nice-to-have": ["AWS"]
        },
        "suggestions": ["Add Docker experience", "Include Kubernetes projects"],
        "analysis_summary": "Good match with some gaps"
    }
    '''
    
    result = _parse_api_response(valid_json)
    assert result['compatibility_score'] == 75
    assert "Python" in result['matching_skills']
    assert "Docker" in result['missing_skills']
    print("✓ Valid JSON parsing works")
    
    # Test JSON with extra text
    json_with_text = "Here's the analysis:\n" + valid_json + "\nThat's the complete analysis."
    result = _parse_api_response(json_with_text)
    assert result['compatibility_score'] == 75
    print("✓ JSON extraction from text works")
    
    # Test invalid JSON (should use fallback)
    invalid_json = "This is not JSON at all. Score: 60%"
    result = _parse_api_response(invalid_json)
    assert result['compatibility_score'] == 60  # Should extract from text
    print("✓ Fallback text parsing works")

def test_fallback_text_parsing():
    """Test fallback text parsing"""
    print("\nTesting fallback text parsing...")
    
    text_response = "The compatibility score is 85%. This is a strong match."
    result = _fallback_text_parsing(text_response)
    assert result['compatibility_score'] == 85
    print("✓ Score extraction from text works")
    
    text_without_score = "This is just some text without any score."
    result = _fallback_text_parsing(text_without_score)
    assert result['compatibility_score'] == 0
    print("✓ Handles text without score")

def test_calculate_score():
    """Test score calculation"""
    print("\nTesting score calculation...")
    
    valid_response = '{"compatibility_score": 92}'
    score = calculate_score(valid_response)
    assert score == 92
    print("✓ Score calculation works")
    
    # Test score bounds
    high_score_response = '{"compatibility_score": 150}'
    score = calculate_score(high_score_response)
    assert score == 100  # Should cap at 100
    print("✓ Score capping works")
    
    invalid_response = "invalid json"
    score = calculate_score(invalid_response)
    assert score == 0  # Should return 0 for invalid response
    print("✓ Invalid response handling works")

def test_identify_gaps():
    """Test gap identification"""
    print("\nTesting gap identification...")
    
    response_with_gaps = '''
    {
        "missing_skills": ["Docker", "Kubernetes", "AWS"]
    }
    '''
    
    gaps = identify_gaps("resume text", {"raw_text": "jd text"}, response_with_gaps)
    assert "Docker" in gaps
    assert "Kubernetes" in gaps
    assert len(gaps) == 3
    print("✓ Gap identification works")

def test_generate_suggestions():
    """Test suggestion generation"""
    print("\nTesting suggestion generation...")
    
    response_with_suggestions = '''
    {
        "suggestions": [
            "Add Docker containerization experience",
            "Include cloud platform certifications",
            "Highlight DevOps practices"
        ]
    }
    '''
    
    suggestions = generate_suggestions(["Docker"], response_with_suggestions)
    assert len(suggestions) == 3
    assert "Docker" in suggestions[0]
    print("✓ Suggestion generation works")

@patch('resume_matcher_ai.matcher.requests.post')
def test_api_error_handling(mock_post):
    """Test API error handling"""
    print("\nTesting API error handling...")
    
    # Test timeout error
    mock_post.side_effect = Exception("Connection timeout")
    
    # Set up environment variable for testing
    os.environ['PERPLEXITY_API_KEY'] = 'pplx-test-key-for-testing-purposes-only'
    
    try:
        call_perplexity_api("test prompt")
        assert False, "Should have raised an exception"
    except Exception as e:
        assert "Connection timeout" in str(e)
        print("✓ Timeout error handling works")
    
    # Clean up
    if 'PERPLEXITY_API_KEY' in os.environ:
        del os.environ['PERPLEXITY_API_KEY']

def test_analyze_match_error_handling():
    """Test analyze_match error handling"""
    print("\nTesting analyze_match error handling...")
    
    # Test with missing API key
    if 'PERPLEXITY_API_KEY' in os.environ:
        del os.environ['PERPLEXITY_API_KEY']
    
    result = analyze_match("resume text", {"raw_text": "jd text"})
    assert result.match_category == "Error"
    assert "PERPLEXITY_API_KEY" in result.suggestions[0]
    print("✓ Missing API key error handling works")

def main():
    """Run all tests"""
    print("Running Perplexity API integration tests...\n")
    
    try:
        test_parse_api_response()
        test_fallback_text_parsing()
        test_calculate_score()
        test_identify_gaps()
        test_generate_suggestions()
        test_api_error_handling()
        test_analyze_match_error_handling()
        
        print("\n✅ All tests passed! Perplexity API integration is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()