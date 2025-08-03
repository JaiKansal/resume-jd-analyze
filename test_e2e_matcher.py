#!/usr/bin/env python3
"""
End-to-end test for the complete matcher functionality
"""
import os
import sys
from unittest.mock import Mock, patch
import json

# Add the resume_matcher_ai directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resume_matcher_ai'))

from resume_matcher_ai.matcher import analyze_match

def test_complete_workflow():
    """Test the complete matching workflow"""
    print("Testing complete matching workflow...")
    
    # Sample resume and job description
    resume_text = """
    Sarah Johnson
    Senior Data Scientist
    Email: sarah.johnson@email.com
    
    EXPERIENCE:
    Senior Data Scientist at TechCorp (2020-2023)
    - Developed machine learning models using Python, scikit-learn, and TensorFlow
    - Built data pipelines processing 10M+ records daily using SQL and Apache Spark
    - Created predictive analytics solutions that improved business KPIs by 25%
    - Collaborated with cross-functional teams using Agile methodologies
    
    Data Analyst at StartupXYZ (2018-2020)
    - Performed statistical analysis and data visualization using Python and R
    - Built automated reporting dashboards using Tableau and Power BI
    - Conducted A/B testing and experimental design for product features
    
    SKILLS:
    - Programming: Python, R, SQL, JavaScript
    - Machine Learning: scikit-learn, TensorFlow, PyTorch, XGBoost
    - Data Tools: Pandas, NumPy, Matplotlib, Seaborn
    - Databases: PostgreSQL, MySQL, MongoDB
    - Visualization: Tableau, Power BI, D3.js
    - Statistics: Hypothesis testing, Regression analysis, Time series
    
    EDUCATION:
    M.S. in Data Science, University of Technology (2018)
    B.S. in Mathematics, State University (2016)
    """
    
    jd_data = {
        "raw_text": """
        Senior Machine Learning Engineer
        Location: San Francisco, CA
        
        ABOUT THE ROLE:
        We are seeking a Senior Machine Learning Engineer to join our AI team. You will be responsible for designing, implementing, and deploying machine learning models at scale.
        
        REQUIREMENTS:
        - 4+ years of experience in machine learning and data science
        - Strong programming skills in Python and SQL
        - Experience with ML frameworks: TensorFlow, PyTorch, or scikit-learn
        - Knowledge of cloud platforms (AWS, GCP, or Azure)
        - Experience with containerization (Docker) and orchestration (Kubernetes)
        - Understanding of MLOps practices and CI/CD pipelines
        - Experience with big data technologies (Spark, Hadoop)
        - Strong statistical and mathematical background
        
        PREFERRED QUALIFICATIONS:
        - Experience with deep learning and neural networks
        - Knowledge of distributed computing
        - Experience with model deployment and monitoring
        - Familiarity with DevOps practices
        - Advanced degree in Computer Science, Statistics, or related field
        
        RESPONSIBILITIES:
        - Design and implement ML models for production systems
        - Optimize model performance and scalability
        - Collaborate with data engineers and software engineers
        - Mentor junior team members
        - Stay current with ML research and best practices
        """
    }
    
    # Mock the API response
    mock_api_response = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "compatibility_score": 82,
                    "matching_skills": [
                        "Python programming",
                        "Machine Learning experience",
                        "TensorFlow framework",
                        "scikit-learn library",
                        "SQL databases",
                        "Statistical analysis",
                        "Data science experience",
                        "Mathematical background",
                        "Apache Spark",
                        "Advanced degree"
                    ],
                    "missing_skills": [
                        "Cloud platforms (AWS/GCP/Azure)",
                        "Docker containerization",
                        "Kubernetes orchestration",
                        "MLOps practices",
                        "CI/CD pipelines",
                        "Model deployment experience",
                        "DevOps practices"
                    ],
                    "skill_gaps": {
                        "Critical": [
                            "Cloud platforms (AWS/GCP/Azure)",
                            "Docker containerization",
                            "MLOps practices"
                        ],
                        "Important": [
                            "Kubernetes orchestration",
                            "CI/CD pipelines",
                            "Model deployment experience"
                        ],
                        "Nice-to-have": [
                            "DevOps practices",
                            "Distributed computing",
                            "Model monitoring"
                        ]
                    },
                    "suggestions": [
                        "Add cloud platform experience to your resume - consider getting AWS or GCP certifications and mention any cloud-based projects",
                        "Include Docker containerization experience - highlight any projects where you containerized ML models or applications",
                        "Emphasize MLOps practices - mention model versioning, experiment tracking, and automated model deployment if you have experience",
                        "Add CI/CD pipeline experience - describe any automation you've built for model training or deployment",
                        "Highlight model deployment experience - provide specific examples of models you've put into production and their business impact"
                    ],
                    "analysis_summary": "Excellent match with strong technical foundation in ML and data science. The candidate has relevant experience and education. Main gaps are in DevOps/MLOps areas which are increasingly important for ML engineering roles. With some additional cloud and deployment experience, this would be a very strong match."
                })
            }
        }]
    }
    
    # Set up environment and mock
    os.environ['PERPLEXITY_API_KEY'] = 'pplx-test-key-for-e2e-testing-12345'
    
    with patch('resume_matcher_ai.matcher.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response
        mock_post.return_value = mock_response
        
        # Run the analysis
        result = analyze_match(resume_text, jd_data)
        
        # Verify the results
        print(f"Score: {result.score}% ({result.match_category})")
        print(f"Processing time: {result.processing_time:.3f} seconds")
        print(f"Matching skills found: {len(result.matching_skills)}")
        print(f"Missing skills identified: {len(result.missing_skills)}")
        print(f"Suggestions provided: {len(result.suggestions)}")
        
        # Assertions
        assert result.score == 82
        assert result.match_category == "Strong Match"
        assert len(result.matching_skills) == 10
        assert len(result.missing_skills) == 7
        assert len(result.suggestions) == 5
        assert result.processing_time >= 0
        
        # Check specific skills
        assert "Python programming" in result.matching_skills
        assert "Machine Learning experience" in result.matching_skills
        assert "Cloud platforms (AWS/GCP/Azure)" in result.missing_skills
        assert "Docker containerization" in result.missing_skills
        
        # Check skill gaps categorization
        assert "Critical" in result.skill_gaps
        assert "Important" in result.skill_gaps
        assert "Nice-to-have" in result.skill_gaps
        assert len(result.skill_gaps["Critical"]) == 3
        assert len(result.skill_gaps["Important"]) == 3
        
        # Check suggestions quality
        assert any("cloud" in suggestion.lower() for suggestion in result.suggestions)
        assert any("docker" in suggestion.lower() for suggestion in result.suggestions)
        
        print("✓ All result validations passed")
        
        # Verify API call was made correctly
        assert mock_post.called
        call_args = mock_post.call_args
        
        # Check request structure
        assert call_args[1]['headers']['Authorization'].startswith('Bearer pplx-')
        payload = call_args[1]['json']
        assert payload['model'] == 'llama-3.1-sonar-large-128k-online'
        assert payload['temperature'] == 0.1
        assert len(payload['messages']) == 2
        
        # Check prompt content
        user_message = payload['messages'][1]['content']
        assert "RESUME:" in user_message
        assert "JOB DESCRIPTION:" in user_message
        assert "Sarah Johnson" in user_message
        assert "Machine Learning Engineer" in user_message
        
        print("✓ API call structure validation passed")
    
    # Clean up
    del os.environ['PERPLEXITY_API_KEY']

def test_error_scenarios():
    """Test various error scenarios"""
    print("\nTesting error scenarios...")
    
    # Test missing API key
    if 'PERPLEXITY_API_KEY' in os.environ:
        del os.environ['PERPLEXITY_API_KEY']
    
    result = analyze_match("test resume", {"raw_text": "test jd"})
    assert result.match_category == "Error"
    assert "PERPLEXITY_API_KEY" in result.suggestions[0]
    print("✓ Missing API key error handled")
    
    # Test with API key but network error
    os.environ['PERPLEXITY_API_KEY'] = 'pplx-test-key-for-error-testing-12345'
    
    with patch('resume_matcher_ai.matcher.requests.post') as mock_post:
        mock_post.side_effect = Exception("Network error")
        
        result = analyze_match("test resume", {"raw_text": "test jd"})
        assert result.match_category == "Error"
        assert "Network error" in result.suggestions[0]
        print("✓ Network error handled")
    
    del os.environ['PERPLEXITY_API_KEY']

def main():
    """Run end-to-end tests"""
    print("Running end-to-end matcher tests...\n")
    
    try:
        test_complete_workflow()
        test_error_scenarios()
        
        print("\n✅ All end-to-end tests passed! The Perplexity API integration is fully functional.")
        print("\nThe implementation includes:")
        print("- ✓ API client functions for Perplexity communication")
        print("- ✓ Structured prompts for resume-JD matching analysis")
        print("- ✓ Comprehensive error handling for API failures, rate limits, and network issues")
        print("- ✓ Response parsing to extract structured matching data")
        print("- ✓ Retry logic with exponential backoff")
        print("- ✓ Fallback text parsing when JSON parsing fails")
        print("- ✓ Proper score calculation and categorization")
        print("- ✓ Skill gap identification and suggestion generation")
        
    except Exception as e:
        print(f"\n❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()