#!/usr/bin/env python3
"""
Debug script for Task 6 issues
"""
import os
import sys
from unittest.mock import Mock, patch

# Add the resume_matcher_ai directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resume_matcher_ai'))

from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.utils import get_match_category

def debug_match_category():
    """Debug the match category issue"""
    print("Debugging match category...")
    
    # Test the get_match_category function directly
    print(f"Score 75 -> Category: {get_match_category(75)}")
    print(f"Score 30 -> Category: {get_match_category(30)}")
    print(f"Score 70 -> Category: {get_match_category(70)}")
    print(f"Score 71 -> Category: {get_match_category(71)}")
    
    # Mock API response
    mock_api_response = '''
    {
        "compatibility_score": 75,
        "matching_skills": ["Python", "Machine Learning", "SQL"],
        "missing_skills": ["Docker", "Kubernetes"],
        "skill_gaps": {
            "Critical": ["Docker"],
            "Important": ["Kubernetes"],
            "Nice-to-have": ["AWS"]
        },
        "suggestions": [
            "Add Docker containerization experience to your resume",
            "Include Kubernetes orchestration projects",
            "Highlight cloud platform experience"
        ],
        "analysis_summary": "Good technical match with some infrastructure gaps"
    }
    '''
    
    with patch('resume_matcher_ai.matcher.call_perplexity_api') as mock_api:
        mock_api.return_value = mock_api_response
        
        # Set up API key for testing
        os.environ['PERPLEXITY_API_KEY'] = 'pplx-test-key-for-testing-purposes-only'
        
        result = analyze_match(
            "Python developer with ML experience", 
            {"raw_text": "Looking for Python developer with Docker skills"}
        )
        
        print(f"Result score: {result.score}")
        print(f"Result match_category: {result.match_category}")
        print(f"Expected category for score 75: {get_match_category(75)}")
        
        # Clean up
        if 'PERPLEXITY_API_KEY' in os.environ:
            del os.environ['PERPLEXITY_API_KEY']

if __name__ == "__main__":
    debug_match_category()