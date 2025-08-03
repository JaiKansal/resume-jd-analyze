#!/usr/bin/env python3
"""
Verification test for Task 6: Core matching and scoring logic
"""
import os
import sys
from unittest.mock import Mock, patch
import json

# Add the resume_matcher_ai directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resume_matcher_ai'))

from resume_matcher_ai.matcher import analyze_match, calculate_score
from resume_matcher_ai.utils import get_match_category, MatchResult

def test_analyze_match_orchestration():
    """Test that analyze_match orchestrates the matching process correctly"""
    print("Testing analyze_match orchestration...")
    
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
        
        # Verify the result structure
        assert isinstance(result, MatchResult)
        assert result.score == 75
        assert result.match_category == "Strong Match"
        assert "Python" in result.matching_skills
        assert "Docker" in result.missing_skills
        assert len(result.suggestions) >= 3
        assert result.processing_time > 0
        
        print("✓ analyze_match orchestration works correctly")
        
        # Clean up
        if 'PERPLEXITY_API_KEY' in os.environ:
            del os.environ['PERPLEXITY_API_KEY']

def test_score_calculation_logic():
    """Test score calculation generates 0-100% compatibility ratings"""
    print("\nTesting score calculation logic...")
    
    # Test various score values
    test_cases = [
        ('{"compatibility_score": 0}', 0),
        ('{"compatibility_score": 25}', 25),
        ('{"compatibility_score": 50}', 50),
        ('{"compatibility_score": 75}', 75),
        ('{"compatibility_score": 100}', 100),
        ('{"compatibility_score": 150}', 100),  # Should cap at 100
        ('{"compatibility_score": -10}', 0),    # Should floor at 0
        ('invalid json', 0),                    # Should handle errors
    ]
    
    for response, expected in test_cases:
        score = calculate_score(response)
        assert score == expected, f"Expected {expected}, got {score} for response: {response}"
    
    print("✓ Score calculation logic works correctly (0-100% range)")

def test_skill_matching_identification():
    """Test skill matching identification finds overlapping skills"""
    print("\nTesting skill matching identification...")
    
    mock_response = '''
    {
        "compatibility_score": 80,
        "matching_skills": ["Python", "Machine Learning", "SQL", "Git", "Agile"],
        "missing_skills": ["Docker", "Kubernetes"],
        "skill_gaps": {
            "Critical": ["Docker"],
            "Important": ["Kubernetes"],
            "Nice-to-have": []
        },
        "suggestions": ["Add containerization experience"]
    }
    '''
    
    with patch('resume_matcher_ai.matcher.call_perplexity_api') as mock_api:
        mock_api.return_value = mock_response
        
        os.environ['PERPLEXITY_API_KEY'] = 'pplx-test-key-for-testing-purposes-only'
        
        result = analyze_match(
            "Python ML engineer with SQL and Git experience", 
            {"raw_text": "Need Python developer with ML, SQL, Docker skills"}
        )
        
        # Verify skill matching identification
        assert len(result.matching_skills) == 5
        assert "Python" in result.matching_skills
        assert "Machine Learning" in result.matching_skills
        assert "SQL" in result.matching_skills
        assert "Git" in result.matching_skills
        assert "Agile" in result.matching_skills
        
        print("✓ Skill matching identification works correctly")
        
        # Clean up
        if 'PERPLEXITY_API_KEY' in os.environ:
            del os.environ['PERPLEXITY_API_KEY']

def test_score_categorization():
    """Test score categorization (Poor/Moderate/Strong Match)"""
    print("\nTesting score categorization...")
    
    # Test categorization ranges
    test_cases = [
        (0, "Poor Match"),
        (15, "Poor Match"),
        (29, "Poor Match"),
        (30, "Moderate Match"),
        (50, "Moderate Match"),
        (70, "Moderate Match"),
        (71, "Strong Match"),
        (85, "Strong Match"),
        (100, "Strong Match"),
    ]
    
    for score, expected_category in test_cases:
        category = get_match_category(score)
        assert category == expected_category, f"Score {score} should be '{expected_category}', got '{category}'"
    
    print("✓ Score categorization works correctly")

def test_integration_with_real_data():
    """Test integration with realistic resume and JD data"""
    print("\nTesting integration with realistic data...")
    
    sample_resume = """
    John Doe
    Software Engineer
    john.doe@email.com | (555) 123-4567
    
    EXPERIENCE
    Senior Software Engineer - Tech Corp (2020-2023)
    • Developed Python applications using Django and Flask
    • Implemented machine learning models using scikit-learn
    • Worked with SQL databases (PostgreSQL, MySQL)
    • Used Git for version control and collaborated in Agile teams
    
    SKILLS
    • Programming: Python, JavaScript, Java
    • Databases: SQL, PostgreSQL, MySQL
    • Machine Learning: scikit-learn, pandas, numpy
    • Tools: Git, Docker (basic), Linux
    """
    
    sample_jd = """
    Senior Python Developer
    
    We are looking for an experienced Python developer to join our team.
    
    Requirements:
    • 3+ years of Python development experience
    • Strong knowledge of Django or Flask frameworks
    • Experience with machine learning libraries
    • Proficiency in SQL and database design
    • Docker containerization experience
    • Kubernetes orchestration knowledge
    • AWS cloud platform experience
    
    Nice to have:
    • JavaScript knowledge
    • Agile methodology experience
    """
    
    # Mock a realistic API response
    mock_response = '''
    {
        "compatibility_score": 78,
        "matching_skills": [
            "Python development",
            "Django/Flask frameworks", 
            "Machine learning",
            "SQL databases",
            "JavaScript",
            "Agile methodology"
        ],
        "missing_skills": [
            "Docker containerization",
            "Kubernetes orchestration", 
            "AWS cloud platform"
        ],
        "skill_gaps": {
            "Critical": ["Docker containerization"],
            "Important": ["Kubernetes orchestration", "AWS cloud platform"],
            "Nice-to-have": []
        },
        "suggestions": [
            "Add specific Docker containerization projects to demonstrate hands-on experience",
            "Include Kubernetes orchestration experience or relevant coursework",
            "Highlight any AWS cloud platform usage or certifications",
            "Expand on machine learning model deployment experience"
        ],
        "analysis_summary": "Strong technical match with good Python and ML background, but missing key DevOps and cloud skills"
    }
    '''
    
    with patch('resume_matcher_ai.matcher.call_perplexity_api') as mock_api:
        mock_api.return_value = mock_response
        
        os.environ['PERPLEXITY_API_KEY'] = 'pplx-test-key-for-testing-purposes-only'
        
        result = analyze_match(sample_resume, {"raw_text": sample_jd})
        
        # Verify comprehensive analysis
        assert result.score == 78
        assert result.match_category == "Strong Match"
        assert len(result.matching_skills) == 6
        assert len(result.missing_skills) == 3
        assert len(result.suggestions) == 4
        assert "Docker" in result.missing_skills[0]
        assert "Critical" in result.skill_gaps
        assert len(result.skill_gaps["Critical"]) == 1
        
        print("✓ Integration with realistic data works correctly")
        
        # Clean up
        if 'PERPLEXITY_API_KEY' in os.environ:
            del os.environ['PERPLEXITY_API_KEY']

def main():
    """Run all verification tests for Task 6"""
    print("🔍 Verifying Task 6: Core matching and scoring logic\n")
    
    try:
        test_analyze_match_orchestration()
        test_score_calculation_logic()
        test_skill_matching_identification()
        test_score_categorization()
        test_integration_with_real_data()
        
        print("\n✅ Task 6 verification complete! All core matching and scoring functionality is working correctly.")
        print("\nTask 6 Sub-tasks Status:")
        print("✅ Implement the main analyze_match function that orchestrates the matching process")
        print("✅ Create score calculation logic to generate 0-100% compatibility ratings")
        print("✅ Build skill matching identification to find overlapping skills")
        print("✅ Add score categorization (Poor/Moderate/Strong Match) based on percentage ranges")
        
    except Exception as e:
        print(f"\n❌ Task 6 verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()