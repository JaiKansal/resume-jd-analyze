#!/usr/bin/env python3
"""
Integration test for Perplexity API with mock responses
"""
import os
import sys
from unittest.mock import Mock, patch
import json

# Add the resume_matcher_ai directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resume_matcher_ai'))

from resume_matcher_ai.matcher import analyze_match, call_perplexity_api
from resume_matcher_ai.utils import format_prompt

def create_mock_api_response():
    """Create a realistic mock API response"""
    return {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "compatibility_score": 78,
                    "matching_skills": [
                        "Python programming",
                        "Machine Learning",
                        "Data Analysis",
                        "SQL databases",
                        "Problem solving"
                    ],
                    "missing_skills": [
                        "Docker containerization",
                        "Kubernetes orchestration",
                        "AWS cloud services",
                        "CI/CD pipelines"
                    ],
                    "skill_gaps": {
                        "Critical": ["Docker containerization", "AWS cloud services"],
                        "Important": ["Kubernetes orchestration", "CI/CD pipelines"],
                        "Nice-to-have": ["Terraform", "Monitoring tools"]
                    },
                    "suggestions": [
                        "Add Docker containerization experience to your resume, mentioning specific projects where you used Docker",
                        "Include AWS cloud services experience, particularly EC2, S3, and Lambda functions",
                        "Highlight any CI/CD pipeline work, even if informal, using tools like GitHub Actions or Jenkins",
                        "Consider adding a section about DevOps practices and infrastructure as code",
                        "Quantify your machine learning projects with specific metrics and business impact"
                    ],
                    "analysis_summary": "Strong technical foundation with good Python and ML skills. Main gaps are in DevOps and cloud infrastructure areas which are important for this role."
                })
            }
        }]
    }

@patch('resume_matcher_ai.matcher.requests.post')
def test_full_integration(mock_post):
    """Test full integration with mocked API response"""
    print("Testing full Perplexity API integration...")
    
    # Set up environment
    os.environ['PERPLEXITY_API_KEY'] = 'pplx-test-key-for-integration-testing-12345'
    
    # Mock successful API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = create_mock_api_response()
    mock_post.return_value = mock_response
    
    # Sample data
    resume_text = """
    John Doe
    Software Engineer
    
    Experience:
    - 3 years Python development
    - Machine learning projects using scikit-learn and pandas
    - SQL database design and optimization
    - Data analysis and visualization
    
    Skills:
    - Python, SQL, JavaScript
    - Machine Learning, Data Science
    - Problem solving, Team collaboration
    """
    
    jd_data = {
        "raw_text": """
        Senior Software Engineer - ML Platform
        
        Requirements:
        - 3+ years Python development
        - Machine Learning experience
        - Docker containerization
        - AWS cloud services
        - Kubernetes orchestration
        - CI/CD pipeline experience
        - SQL databases
        
        Responsibilities:
        - Build ML infrastructure
        - Deploy models to production
        - Maintain cloud infrastructure
        """
    }
    
    # Test the full analyze_match function
    result = analyze_match(resume_text, jd_data)
    
    # Verify results
    assert result.score == 78
    assert result.match_category == "Strong Match"
    assert len(result.matching_skills) == 5
    assert "Python programming" in result.matching_skills
    assert "Docker containerization" in result.missing_skills
    assert len(result.suggestions) == 5
    assert "Docker" in result.suggestions[0]
    assert result.processing_time > 0
    
    print(f"✓ Score: {result.score}% ({result.match_category})")
    print(f"✓ Matching skills: {len(result.matching_skills)} found")
    print(f"✓ Missing skills: {len(result.missing_skills)} identified")
    print(f"✓ Suggestions: {len(result.suggestions)} provided")
    print(f"✓ Processing time: {result.processing_time:.2f} seconds")
    
    # Verify API was called correctly
    assert mock_post.called
    call_args = mock_post.call_args
    
    # Check headers
    headers = call_args[1]['headers']
    assert 'Authorization' in headers
    assert headers['Authorization'].startswith('Bearer pplx-')
    assert headers['Content-Type'] == 'application/json'
    
    # Check payload structure
    payload = call_args[1]['json']
    assert payload['model'] == 'sonar'
    assert len(payload['messages']) == 2
    assert payload['messages'][0]['role'] == 'system'
    assert payload['messages'][1]['role'] == 'user'
    assert 'RESUME:' in payload['messages'][1]['content']
    assert 'JOB DESCRIPTION:' in payload['messages'][1]['content']
    
    print("✓ API call structure is correct")
    
    # Clean up
    del os.environ['PERPLEXITY_API_KEY']

@patch('resume_matcher_ai.matcher.requests.post')
def test_rate_limit_handling(mock_post):
    """Test rate limit error handling"""
    print("\nTesting rate limit handling...")
    
    os.environ['PERPLEXITY_API_KEY'] = 'pplx-test-key-for-rate-limit-testing-12345'
    
    # Mock rate limit response
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.headers = {'Retry-After': '60'}
    mock_post.return_value = mock_response
    
    result = analyze_match("test resume", {"raw_text": "test jd"})
    
    assert result.match_category == "Error"
    assert "Rate limit exceeded" in result.suggestions[0]
    assert "60 seconds" in result.suggestions[0]
    
    print("✓ Rate limit error handling works")
    
    del os.environ['PERPLEXITY_API_KEY']

@patch('resume_matcher_ai.matcher.requests.post')
def test_server_error_handling(mock_post):
    """Test server error handling"""
    print("\nTesting server error handling...")
    
    os.environ['PERPLEXITY_API_KEY'] = 'pplx-test-key-for-server-error-testing-12345'
    
    # Mock server error response
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_post.return_value = mock_response
    
    result = analyze_match("test resume", {"raw_text": "test jd"})
    
    assert result.match_category == "Error"
    assert "server error" in result.suggestions[0].lower()
    
    print("✓ Server error handling works")
    
    del os.environ['PERPLEXITY_API_KEY']

def test_prompt_formatting():
    """Test prompt formatting"""
    print("\nTesting prompt formatting...")
    
    resume_text = "John Doe, Software Engineer with Python experience"
    jd_text = "Looking for Python developer with 3+ years experience"
    
    prompt = format_prompt(resume_text, jd_text)
    
    assert "RESUME:" in prompt
    assert "JOB DESCRIPTION:" in prompt
    assert "JSON format" in prompt
    assert "compatibility_score" in prompt
    assert resume_text in prompt
    assert jd_text in prompt
    
    print("✓ Prompt formatting is correct")

def main():
    """Run all integration tests"""
    print("Running Perplexity API integration tests...\n")
    
    try:
        test_full_integration()
        test_rate_limit_handling()
        test_server_error_handling()
        test_prompt_formatting()
        
        print("\n✅ All integration tests passed! Perplexity API integration is fully functional.")
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()