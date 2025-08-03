#!/usr/bin/env python3
"""
Integration test for Task 7 implementation
Tests the complete pipeline with enhanced gap analysis and suggestions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.utils import MatchResult

def test_complete_gap_analysis_pipeline():
    """Test the complete pipeline with gap analysis and suggestions"""
    print("Testing complete gap analysis pipeline...")
    
    # Sample resume text
    resume_text = """
    John Doe
    Software Developer
    
    Experience:
    - 3 years of Python development
    - Built web applications using Flask
    - Experience with SQL databases
    - Worked on team projects using Git
    
    Skills:
    - Python, SQL, Flask, Git, HTML, CSS
    - Problem solving and teamwork
    """
    
    # Sample job description
    jd_data = {
        "raw_text": """
        Senior Python Developer Position
        
        Requirements:
        - 3+ years Python experience (Required)
        - Docker and Kubernetes experience (Required)
        - AWS cloud platform knowledge (Important)
        - React frontend development (Important)
        - Machine Learning experience (Nice to have)
        - Strong problem-solving skills
        - Team collaboration experience
        
        Responsibilities:
        - Develop scalable Python applications
        - Deploy applications using containerization
        - Work with cloud infrastructure
        - Collaborate with cross-functional teams
        """
    }
    
    # Mock the API call to avoid actual API usage in tests
    def mock_api_response():
        return '''
        {
            "compatibility_score": 65,
            "matching_skills": ["Python (3+ years experience)", "SQL databases", "Problem solving", "Team collaboration"],
            "missing_skills": ["Docker", "Kubernetes", "AWS", "React", "Machine Learning"],
            "skill_gaps": {
                "Critical": ["Docker", "Kubernetes"],
                "Important": ["AWS", "React"],
                "Nice-to-have": ["Machine Learning"]
            },
            "suggestions": [
                "Add containerization experience with Docker and Kubernetes to your skills section",
                "Include cloud platform experience, particularly AWS, in your technical skills",
                "Consider adding frontend development experience with React",
                "Enhance your experience descriptions with specific metrics and achievements"
            ],
            "analysis_summary": "Good Python foundation but missing key DevOps and cloud skills required for senior role"
        }
        '''
    
    # Patch the API call for testing
    import resume_matcher_ai.matcher as matcher_module
    original_call = matcher_module.call_perplexity_api
    matcher_module.call_perplexity_api = lambda prompt: mock_api_response()
    
    try:
        # Run the analysis
        result = analyze_match(resume_text, jd_data)
        
        # Verify the result structure
        assert isinstance(result, MatchResult), "Should return MatchResult object"
        
        # Test Requirements 4.1, 4.2, 4.3: Gap analysis
        assert isinstance(result.skill_gaps, dict), "Skill gaps should be a dictionary"
        assert "Critical" in result.skill_gaps, "Should have Critical category"
        assert "Important" in result.skill_gaps, "Should have Important category"
        assert "Nice-to-have" in result.skill_gaps, "Should have Nice-to-have category"
        
        # Verify gap prioritization (Requirement 4.2)
        assert "Docker" in result.skill_gaps["Critical"], "Docker should be critical"
        assert "Kubernetes" in result.skill_gaps["Critical"], "Kubernetes should be critical"
        assert "AWS" in result.skill_gaps["Important"], "AWS should be important"
        assert "Machine Learning" in result.skill_gaps["Nice-to-have"], "ML should be nice-to-have"
        
        # Test Requirement 5.1: At least 3 suggestions
        assert len(result.suggestions) >= 3, f"Should have at least 3 suggestions, got {len(result.suggestions)}"
        
        # Test Requirement 5.2: Focus on missing skills and improvements
        suggestions_text = " ".join(result.suggestions).lower()
        assert "docker" in suggestions_text or "kubernetes" in suggestions_text, "Should mention critical missing skills"
        
        # Test Requirement 5.3: Specific recommendations
        has_specific_recommendations = any(
            len(suggestion.split()) > 5 for suggestion in result.suggestions
        )
        assert has_specific_recommendations, "Should have detailed, specific suggestions"
        
        # Verify other components still work
        assert result.score > 0, "Should have a valid score"
        assert result.match_category in ["Poor Match", "Moderate Match", "Strong Match"], "Should have valid category"
        assert len(result.matching_skills) > 0, "Should have matching skills"
        assert result.processing_time > 0, "Should have processing time"
        
        print("✓ Complete gap analysis pipeline working correctly")
        return True
        
    finally:
        # Restore original API call
        matcher_module.call_perplexity_api = original_call

def test_no_gaps_scenario():
    """Test Requirement 4.4: All key skills present scenario"""
    print("Testing no gaps scenario...")
    
    resume_text = "Experienced developer with Python, Docker, Kubernetes, AWS, React"
    jd_data = {"raw_text": "Looking for Python developer with Docker, Kubernetes experience"}
    
    # Mock response with no gaps
    def mock_no_gaps_response():
        return '''
        {
            "compatibility_score": 90,
            "matching_skills": ["Python", "Docker", "Kubernetes"],
            "missing_skills": [],
            "skill_gaps": {
                "Critical": [],
                "Important": [],
                "Nice-to-have": []
            },
            "suggestions": [
                "Your resume shows excellent alignment with the role requirements",
                "Consider adding quantifiable achievements to strengthen your impact statements",
                "Optimize keyword usage by incorporating more industry-specific terminology"
            ],
            "analysis_summary": "Excellent match with all key skills present"
        }
        '''
    
    import resume_matcher_ai.matcher as matcher_module
    original_call = matcher_module.call_perplexity_api
    matcher_module.call_perplexity_api = lambda prompt: mock_no_gaps_response()
    
    try:
        result = analyze_match(resume_text, jd_data)
        
        # Verify no gaps scenario (Requirement 4.4)
        total_gaps = sum(len(skills) for skills in result.skill_gaps.values())
        assert total_gaps == 0, "Should have no skill gaps when all skills are present"
        
        # Should still have suggestions (optimization for strong matches - Requirement 5.4)
        assert len(result.suggestions) >= 3, "Should still provide optimization suggestions"
        
        print("✓ No gaps scenario handled correctly")
        return True
        
    finally:
        matcher_module.call_perplexity_api = original_call

def run_integration_tests():
    """Run all integration tests for Task 7"""
    print("=" * 60)
    print("TASK 7 INTEGRATION TESTS")
    print("=" * 60)
    
    try:
        test_complete_gap_analysis_pipeline()
        test_no_gaps_scenario()
        
        print("\n" + "=" * 60)
        print("✅ ALL TASK 7 INTEGRATION TESTS PASSED!")
        print("Gap analysis and suggestions are fully integrated and working.")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)