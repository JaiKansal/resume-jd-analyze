#!/usr/bin/env python3
"""
Test script for Task 7: Gap Analysis and Suggestions Implementation
Tests Requirements 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from resume_matcher_ai.matcher import (
    identify_skill_gaps_by_priority,
    generate_enhanced_suggestions,
    _generate_fallback_suggestions,
    _enhance_suggestions_with_specifics,
    _parse_api_response
)
from resume_matcher_ai.utils import MatchResult

def test_skill_gaps_prioritization():
    """Test Requirements 4.2 and 4.3: Skill gap prioritization and categorization"""
    print("Testing skill gap prioritization and categorization...")
    
    # Mock API response with skill gaps
    mock_api_response = '''
    {
        "compatibility_score": 65,
        "matching_skills": ["Python", "SQL", "Problem Solving"],
        "missing_skills": ["Docker", "Kubernetes", "AWS", "React", "Machine Learning"],
        "skill_gaps": {
            "Critical": ["Docker", "Kubernetes"],
            "Important": ["AWS", "React"],
            "Nice-to-have": ["Machine Learning"]
        },
        "suggestions": ["Add containerization experience", "Include cloud platform skills"],
        "analysis_summary": "Good technical foundation but missing key DevOps skills"
    }
    '''
    
    # Test skill gap identification
    skill_gaps = identify_skill_gaps_by_priority("Sample resume text", {"raw_text": "Sample JD"}, mock_api_response)
    
    # Verify structure (Requirement 4.3)
    assert isinstance(skill_gaps, dict), "Skill gaps should be a dictionary"
    assert "Critical" in skill_gaps, "Should have Critical category"
    assert "Important" in skill_gaps, "Should have Important category"
    assert "Nice-to-have" in skill_gaps, "Should have Nice-to-have category"
    
    # Verify content (Requirement 4.2)
    assert "Docker" in skill_gaps["Critical"], "Docker should be in Critical skills"
    assert "Kubernetes" in skill_gaps["Critical"], "Kubernetes should be in Critical skills"
    assert "AWS" in skill_gaps["Important"], "AWS should be in Important skills"
    assert "Machine Learning" in skill_gaps["Nice-to-have"], "ML should be in Nice-to-have skills"
    
    print("✓ Skill gap prioritization and categorization working correctly")

def test_no_missing_skills_scenario():
    """Test Requirement 4.4: Display message when no missing skills"""
    print("Testing no missing skills scenario...")
    
    # Mock API response with no skill gaps
    mock_api_response = '''
    {
        "compatibility_score": 85,
        "matching_skills": ["Python", "SQL", "Docker", "AWS"],
        "missing_skills": [],
        "skill_gaps": {
            "Critical": [],
            "Important": [],
            "Nice-to-have": []
        },
        "suggestions": ["Optimize keyword usage", "Add metrics to achievements"],
        "analysis_summary": "Strong match with all key skills present"
    }
    '''
    
    skill_gaps = identify_skill_gaps_by_priority("Sample resume", {"raw_text": "Sample JD"}, mock_api_response)
    
    # Verify all categories are empty (Requirement 4.4)
    total_gaps = sum(len(skills) for skills in skill_gaps.values())
    assert total_gaps == 0, "Should have no skill gaps when all skills are present"
    
    print("✓ No missing skills scenario handled correctly")

def test_enhanced_suggestions_generation():
    """Test Requirements 5.1, 5.2, 5.3: Enhanced suggestion generation"""
    print("Testing enhanced suggestion generation...")
    
    skill_gaps = {
        "Critical": ["Docker", "Kubernetes"],
        "Important": ["AWS"],
        "Nice-to-have": ["Machine Learning"]
    }
    
    mock_api_response = '''
    {
        "suggestions": ["Add containerization skills", "Include cloud experience"]
    }
    '''
    
    # Test with moderate score (30-70%)
    suggestions = generate_enhanced_suggestions("Resume text", {"raw_text": "JD text"}, skill_gaps, 50, mock_api_response)
    
    # Verify minimum number of suggestions (Requirement 5.1)
    assert len(suggestions) >= 3, f"Should have at least 3 suggestions, got {len(suggestions)}"
    
    # Verify suggestions are strings and not empty
    for suggestion in suggestions:
        assert isinstance(suggestion, str), "All suggestions should be strings"
        assert len(suggestion.strip()) > 0, "Suggestions should not be empty"
    
    print("✓ Enhanced suggestion generation working correctly")

def test_suggestions_for_strong_match():
    """Test Requirement 5.4: Optimization suggestions for strong matches"""
    print("Testing suggestions for strong matches...")
    
    skill_gaps = {
        "Critical": [],
        "Important": ["Advanced Analytics"],
        "Nice-to-have": ["Machine Learning"]
    }
    
    mock_api_response = '''
    {
        "suggestions": ["Optimize resume format", "Add quantifiable metrics"]
    }
    '''
    
    # Test with high score (>70%) - should get optimization suggestions
    suggestions = generate_enhanced_suggestions("Resume text", {"raw_text": "JD text"}, skill_gaps, 85, mock_api_response)
    
    # Verify we get optimization-focused suggestions for strong matches
    suggestion_text = " ".join(suggestions).lower()
    optimization_keywords = ["optimize", "enhance", "improve", "strengthen", "metrics", "achievements"]
    
    has_optimization_focus = any(keyword in suggestion_text for keyword in optimization_keywords)
    assert has_optimization_focus, "Strong matches should receive optimization-focused suggestions"
    
    print("✓ Strong match optimization suggestions working correctly")

def test_fallback_suggestions():
    """Test fallback suggestion generation when API fails"""
    print("Testing fallback suggestion generation...")
    
    skill_gaps = {
        "Critical": ["Python", "SQL"],
        "Important": ["Docker"],
        "Nice-to-have": ["Machine Learning"]
    }
    
    # Test fallback suggestions for different score ranges
    poor_suggestions = _generate_fallback_suggestions(skill_gaps, 20)
    moderate_suggestions = _generate_fallback_suggestions(skill_gaps, 50)
    strong_suggestions = _generate_fallback_suggestions(skill_gaps, 80)
    
    # Verify all generate suggestions
    assert len(poor_suggestions) >= 3, "Poor match should have at least 3 suggestions"
    assert len(moderate_suggestions) >= 3, "Moderate match should have at least 3 suggestions"
    assert len(strong_suggestions) >= 3, "Strong match should have at least 3 suggestions"
    
    # Verify critical skills are mentioned in suggestions
    poor_text = " ".join(poor_suggestions).lower()
    assert "python" in poor_text or "sql" in poor_text, "Critical skills should be mentioned in suggestions"
    
    print("✓ Fallback suggestion generation working correctly")

def test_suggestion_enhancement_with_specifics():
    """Test Requirement 5.3: Specific suggestions with recommended phrases"""
    print("Testing suggestion enhancement with specifics...")
    
    base_suggestions = [
        "Add more technical skills to your resume",
        "Improve your experience descriptions",
        "Add a professional summary section"
    ]
    
    skill_gaps = {
        "Critical": ["Docker", "Kubernetes"],
        "Important": ["AWS"],
        "Nice-to-have": []
    }
    
    enhanced = _enhance_suggestions_with_specifics(base_suggestions, skill_gaps, 60)
    
    # Verify suggestions are enhanced with specifics
    enhanced_text = " ".join(enhanced).lower()
    
    # Should include specific skills
    assert "docker" in enhanced_text or "kubernetes" in enhanced_text, "Should include specific critical skills"
    
    # Should include recommended phrases
    phrase_indicators = ["led cross-functional", "implemented solutions", "collaborated with", "core competencies"]
    has_specific_phrases = any(phrase in enhanced_text for phrase in phrase_indicators)
    assert has_specific_phrases, "Should include specific recommended phrases"
    
    print("✓ Suggestion enhancement with specifics working correctly")

def test_api_response_parsing():
    """Test robust API response parsing"""
    print("Testing API response parsing...")
    
    # Test valid JSON response
    valid_response = '''
    {
        "compatibility_score": 75,
        "matching_skills": ["Python", "SQL"],
        "missing_skills": ["Docker"],
        "skill_gaps": {
            "Critical": ["Docker"],
            "Important": ["AWS"],
            "Nice-to-have": []
        },
        "suggestions": ["Add containerization skills"],
        "analysis_summary": "Good match"
    }
    '''
    
    parsed = _parse_api_response(valid_response)
    assert parsed["compatibility_score"] == 75, "Should parse score correctly"
    assert "Python" in parsed["matching_skills"], "Should parse matching skills"
    assert "Docker" in parsed["skill_gaps"]["Critical"], "Should parse skill gaps"
    
    # Test response with extra text (common with AI APIs)
    messy_response = '''Here is the analysis:
    {
        "compatibility_score": 60,
        "matching_skills": ["Java"],
        "missing_skills": ["Spring"],
        "skill_gaps": {
            "Critical": ["Spring"],
            "Important": [],
            "Nice-to-have": []
        },
        "suggestions": ["Add Spring framework experience"]
    }
    Additional notes here.'''
    
    parsed_messy = _parse_api_response(messy_response)
    assert parsed_messy["compatibility_score"] == 60, "Should parse score from messy response"
    assert "Java" in parsed_messy["matching_skills"], "Should parse skills from messy response"
    
    print("✓ API response parsing working correctly")

def run_all_tests():
    """Run all gap analysis and suggestions tests"""
    print("=" * 60)
    print("TESTING TASK 7: GAP ANALYSIS AND SUGGESTIONS")
    print("=" * 60)
    
    try:
        test_skill_gaps_prioritization()
        test_no_missing_skills_scenario()
        test_enhanced_suggestions_generation()
        test_suggestions_for_strong_match()
        test_fallback_suggestions()
        test_suggestion_enhancement_with_specifics()
        test_api_response_parsing()
        
        print("\n" + "=" * 60)
        print("✅ ALL TASK 7 TESTS PASSED!")
        print("Gap analysis and suggestions implementation is working correctly.")
        print("Requirements 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4 are satisfied.")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)