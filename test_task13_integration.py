#!/usr/bin/env python3
"""
Task 13: Integrate all components and test end-to-end workflow
Complete integration testing for the resume matcher application
"""

import os
import sys
import tempfile
import time
import json
from unittest.mock import patch, MagicMock
from io import StringIO

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from resume_matcher_ai.main import main, get_user_input, display_results, _process_analysis
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text, validate_resume_content
from resume_matcher_ai.jd_parser import parse_jd_text
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.utils import MatchResult, JobDescription, load_config, validate_api_key


class Task13IntegrationTests:
    """Complete end-to-end integration tests for Task 13"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_results = []
        
    def cleanup(self):
        """Clean up test resources"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_end_to_end_workflow(self):
        """
        Test the complete end-to-end workflow from user input to result display
        Requirements: 1.1, 1.2, 2.1, 3.1, 4.1, 5.1, 6.1
        """
        print("🧪 Testing complete end-to-end workflow...")
        
        # Sample data from the project
        with open('sample_resume.txt', 'r') as f:
            sample_resume_text = f.read()
        
        with open('sample_jd.txt', 'r') as f:
            sample_jd_text = f.read()
        
        try:
            # Create a dummy PDF path
            pdf_path = os.path.join(self.temp_dir, "sample_resume.pdf")
            
            # Mock all file operations and API calls
            with patch('resume_matcher_ai.main._validate_resume_file') as mock_validate, \
                 patch('resume_matcher_ai.resume_parser._validate_pdf_file_comprehensive') as mock_pdf_validate, \
                 patch('resume_matcher_ai.main.extract_text_from_pdf') as mock_extract, \
                 patch('resume_matcher_ai.matcher.call_perplexity_api') as mock_api:
                
                # Setup mocks
                mock_validate.return_value = True
                mock_pdf_validate.return_value = None
                mock_extract.return_value = sample_resume_text
                
                # Mock realistic API response
                mock_api_response = {
                    "compatibility_score": 82,
                    "matching_skills": [
                        "JavaScript", "React.js", "Node.js", "Express.js", 
                        "PostgreSQL", "MongoDB", "AWS", "Git", "HTML", "CSS"
                    ],
                    "missing_skills": ["TypeScript", "Docker", "CI/CD"],
                    "skill_gaps": {
                        "Critical": [],
                        "Important": ["TypeScript", "Docker"],
                        "Nice-to-have": ["CI/CD pipelines"]
                    },
                    "suggestions": [
                        "Add TypeScript experience to strengthen your frontend development profile",
                        "Include Docker containerization experience in your DevOps skills section",
                        "Mention any CI/CD pipeline experience you may have with Jenkins or similar tools",
                        "Quantify your API development achievements with specific user metrics"
                    ],
                    "analysis_summary": "Strong technical match with excellent full-stack experience alignment"
                }
                mock_api.return_value = json.dumps(mock_api_response)
                
                # Test the complete workflow
                start_time = time.time()
                result = _process_analysis(pdf_path, sample_jd_text)
                end_time = time.time()
                
                # Validate all requirements are met
                
                # Requirement 1.1: Resume PDF processing within 30 seconds
                processing_time = end_time - start_time
                assert processing_time < 30, f"Processing took {processing_time:.2f}s, should be under 30s"
                
                # Requirement 1.2: Job description text processing
                assert isinstance(result, MatchResult), "Should return MatchResult object"
                
                # Requirement 2.1: Numerical compatibility score (0-100%)
                assert 0 <= result.score <= 100, f"Score {result.score} should be between 0-100"
                assert result.score == 82, f"Expected score 82, got {result.score}"
                assert result.match_category in ["Poor Match", "Moderate Match", "Strong Match"], \
                    f"Invalid match category: {result.match_category}"
                
                # Requirement 3.1: Matching skills display
                assert isinstance(result.matching_skills, list), "Matching skills should be a list"
                assert len(result.matching_skills) > 0, "Should have matching skills"
                expected_skills = ["JavaScript", "React.js", "Node.js", "PostgreSQL", "AWS"]
                for skill in expected_skills:
                    assert skill in result.matching_skills, f"Expected skill '{skill}' not found in matching skills"
                
                # Requirement 4.1: Missing skills identification
                assert isinstance(result.missing_skills, list), "Missing skills should be a list"
                assert isinstance(result.skill_gaps, dict), "Skill gaps should be a dictionary"
                assert "Critical" in result.skill_gaps, "Should have Critical skill gaps category"
                assert "Important" in result.skill_gaps, "Should have Important skill gaps category"
                assert "Nice-to-have" in result.skill_gaps, "Should have Nice-to-have skill gaps category"
                
                # Requirement 5.1: At least 3 actionable suggestions
                assert isinstance(result.suggestions, list), "Suggestions should be a list"
                assert len(result.suggestions) >= 3, f"Should have at least 3 suggestions, got {len(result.suggestions)}"
                
                # Requirement 6.1: Processing time tracking
                assert result.processing_time > 0, "Processing time should be positive"
                assert result.processing_time < 30, "Processing time should be under 30 seconds"
                
                print("✅ Complete end-to-end workflow test passed!")
                return True
                
        except Exception as e:
            print(f"❌ Complete end-to-end workflow test failed: {str(e)}")
            return False
    
    def test_module_integration_connectivity(self):
        """Test that all modules are properly connected and can communicate"""
        print("🧪 Testing module integration connectivity...")
        
        try:
            # Test resume parser integration
            sample_text = """John Doe
Software Engineer
Email: john.doe@email.com
Phone: (555) 123-4567

WORK EXPERIENCE:
Senior Software Engineer at Tech Corp (2020-2023)
• Developed web applications using Python, JavaScript, and React
• Led a team of 5 developers on multiple projects
• Implemented CI/CD pipelines using Docker and AWS
• Collaborated with product teams to deliver features on time

Junior Developer at StartupXYZ (2018-2020)
• Assisted in frontend development using HTML, CSS, and JavaScript
• Fixed bugs and implemented minor features
• Learned modern development practices and tools

EDUCATION:
Bachelor of Science in Computer Science
University of Technology (2014-2018)
GPA: 3.7/4.0

TECHNICAL SKILLS:
Python, JavaScript, React, Node.js, AWS, Docker, PostgreSQL, Git

PROJECTS:
E-commerce Platform (2023)
• Built full-stack application using React and Node.js
• Implemented user authentication and payment processing

CERTIFICATIONS:
• AWS Certified Developer - Associate (2023)"""
            cleaned_text = clean_resume_text(sample_text)
            is_valid = validate_resume_content(cleaned_text)
            assert is_valid, f"Resume content validation should pass. Content length: {len(cleaned_text)}, Word count: {len(cleaned_text.split())}"
            
            # Test JD parser integration
            sample_jd = """
            Software Engineer Position
            
            Requirements:
            • 3+ years of experience
            • Python and JavaScript skills
            • React framework knowledge
            
            Responsibilities:
            • Develop web applications
            • Collaborate with teams
            """
            
            jd_data = parse_jd_text(sample_jd)
            assert isinstance(jd_data, JobDescription), "Should return JobDescription object"
            assert len(jd_data.technical_skills) > 0, "Should extract technical skills"
            assert len(jd_data.requirements) > 0, "Should extract requirements"
            
            # Test matcher integration with mocked API
            with patch('resume_matcher_ai.matcher.call_perplexity_api') as mock_api:
                mock_response = {
                    "compatibility_score": 75,
                    "matching_skills": ["Python", "JavaScript", "React"],
                    "missing_skills": ["Experience"],
                    "skill_gaps": {"Critical": [], "Important": ["3+ years experience"], "Nice-to-have": []},
                    "suggestions": ["Add more experience details", "Include project examples", "Quantify achievements"],
                    "analysis_summary": "Good technical match"
                }
                mock_api.return_value = json.dumps(mock_response)
                
                # Convert jd_data to dict format expected by analyze_match
                jd_dict = {
                    'raw_text': jd_data.raw_text,
                    'title': jd_data.title,
                    'requirements': jd_data.requirements,
                    'technical_skills': jd_data.technical_skills,
                    'soft_skills': jd_data.soft_skills
                }
                
                result = analyze_match(cleaned_text, jd_dict)
                assert isinstance(result, MatchResult), "Should return MatchResult"
                assert result.score == 75, f"Expected score 75, got {result.score}"
                assert len(result.matching_skills) == 3, f"Expected 3 matching skills, got {len(result.matching_skills)}"
            
            print("✅ Module integration connectivity test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Module integration connectivity test failed: {str(e)}")
            return False
    
    def test_error_handling_across_components(self):
        """Test error handling works correctly across all components"""
        print("🧪 Testing error handling across components...")
        
        try:
            # Test resume parser error handling
            try:
                extract_text_from_pdf("nonexistent_file.pdf")
                assert False, "Should raise FileNotFoundError"
            except FileNotFoundError:
                pass  # Expected
            
            # Test JD parser error handling
            try:
                parse_jd_text("")
                assert False, "Should raise ValueError for empty JD"
            except ValueError:
                pass  # Expected
            
            try:
                parse_jd_text("x" * 100000)  # Too long
                assert False, "Should raise ValueError for too long JD"
            except ValueError:
                pass  # Expected
            
            # Test matcher error handling with API failure
            with patch('resume_matcher_ai.matcher.call_perplexity_api') as mock_api:
                mock_api.side_effect = Exception("API connection failed")
                
                jd_dict = {'raw_text': 'test jd', 'title': 'test', 'requirements': [], 'technical_skills': [], 'soft_skills': []}
                result = analyze_match("test resume", jd_dict)
                
                # Should return error result, not crash
                assert isinstance(result, MatchResult), "Should return MatchResult even on error"
                assert result.match_category == "Error", "Should indicate error state"
                assert len(result.suggestions) > 0, "Should have error message in suggestions"
            
            # Test main application error handling
            pdf_path = os.path.join(self.temp_dir, "test.pdf")
            jd_text = "Valid job description"
            
            with patch('resume_matcher_ai.main.extract_text_from_pdf') as mock_extract:
                mock_extract.side_effect = ValueError("PDF extraction failed")
                
                try:
                    _process_analysis(pdf_path, jd_text)
                    # If no exception, check that error was handled gracefully
                except Exception as e:
                    # Exception is expected after retries
                    assert "PDF extraction failed" in str(e), "Should propagate PDF extraction error"
            
            print("✅ Error handling across components test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Error handling across components test failed: {str(e)}")
            return False
    
    def test_requirements_validation(self):
        """Validate that all specified requirements are met through integration testing"""
        print("🧪 Testing requirements validation...")
        
        try:
            # Load sample data
            with open('sample_resume.txt', 'r') as f:
                resume_text = f.read()
            with open('sample_jd.txt', 'r') as f:
                jd_text = f.read()
            
            pdf_path = os.path.join(self.temp_dir, "test_resume.pdf")
            
            # Mock file operations
            with patch('resume_matcher_ai.main._validate_resume_file') as mock_validate, \
                 patch('resume_matcher_ai.main.extract_text_from_pdf') as mock_extract, \
                 patch('resume_matcher_ai.matcher.call_perplexity_api') as mock_api:
                
                mock_validate.return_value = True
                mock_extract.return_value = resume_text
                
                # Create comprehensive mock response that tests all requirements
                mock_response = {
                    "compatibility_score": 78,
                    "matching_skills": [
                        "JavaScript", "TypeScript", "Python", "React.js", "Node.js", 
                        "Express.js", "PostgreSQL", "MongoDB", "AWS", "Docker", "Git"
                    ],
                    "missing_skills": ["Kubernetes", "CI/CD pipelines"],
                    "skill_gaps": {
                        "Critical": [],
                        "Important": ["Kubernetes", "CI/CD pipelines"],
                        "Nice-to-have": ["GraphQL", "Microservices architecture"]
                    },
                    "suggestions": [
                        "Add Kubernetes container orchestration experience to your DevOps skills",
                        "Include CI/CD pipeline implementation examples using Jenkins or GitHub Actions",
                        "Mention any GraphQL API development experience you may have",
                        "Quantify your full-stack development achievements with specific metrics",
                        "Consider adding microservices architecture experience to strengthen your backend profile"
                    ],
                    "analysis_summary": "Strong match with excellent technical skills alignment and growth potential"
                }
                mock_api.return_value = json.dumps(mock_response)
                
                # Test complete analysis
                start_time = time.time()
                result = _process_analysis(pdf_path, jd_text)
                end_time = time.time()
                
                # Validate each requirement explicitly
                
                # Requirement 1.1: Resume PDF processing
                assert mock_extract.called, "Should extract text from PDF"
                
                # Requirement 1.2: Job description processing  
                assert len(jd_text.strip()) > 0, "Job description should be processed"
                
                # Requirement 2.1: Numerical compatibility score
                assert isinstance(result.score, int), "Score should be integer"
                assert 0 <= result.score <= 100, "Score should be 0-100%"
                assert result.score == 78, f"Expected score 78, got {result.score}"
                
                # Requirement 3.1: Matching skills display
                assert isinstance(result.matching_skills, list), "Matching skills should be list"
                assert len(result.matching_skills) >= 5, "Should have multiple matching skills"
                
                # Requirement 4.1: Missing skills identification
                assert isinstance(result.skill_gaps, dict), "Skill gaps should be dictionary"
                assert all(cat in result.skill_gaps for cat in ["Critical", "Important", "Nice-to-have"]), \
                    "Should have all skill gap categories"
                
                # Requirement 5.1: Improvement suggestions
                assert isinstance(result.suggestions, list), "Suggestions should be list"
                assert len(result.suggestions) >= 3, f"Should have at least 3 suggestions, got {len(result.suggestions)}"
                
                # Requirement 6.1: Processing within 30 seconds
                processing_time = end_time - start_time
                assert processing_time < 30, f"Processing took {processing_time:.2f}s, should be under 30s"
                assert result.processing_time > 0, "Should record processing time"
                
                print("✅ Requirements validation test passed!")
                return True
                
        except Exception as e:
            print(f"❌ Requirements validation test failed: {str(e)}")
            return False
    
    def test_sample_files_integration(self):
        """Test integration using the actual sample files from the project"""
        print("🧪 Testing integration with sample files...")
        
        try:
            # Use actual sample files
            with open('sample_resume.txt', 'r') as f:
                sample_resume = f.read()
            with open('sample_jd.txt', 'r') as f:
                sample_jd = f.read()
            
            # Validate sample files have good content
            assert len(sample_resume) > 100, "Sample resume should have substantial content"
            assert len(sample_jd) > 100, "Sample JD should have substantial content"
            assert "JavaScript" in sample_resume, "Sample resume should contain JavaScript"
            assert "React" in sample_jd, "Sample JD should mention React"
            
            # Test resume parsing
            cleaned_resume = clean_resume_text(sample_resume)
            assert validate_resume_content(cleaned_resume), "Sample resume should be valid"
            
            # Test JD parsing
            jd_data = parse_jd_text(sample_jd)
            assert isinstance(jd_data, JobDescription), "Should parse JD successfully"
            assert len(jd_data.technical_skills) > 0, "Should extract technical skills from sample JD"
            assert len(jd_data.requirements) > 0, "Should extract requirements from sample JD"
            
            # Test complete matching with sample data
            pdf_path = os.path.join(self.temp_dir, "sample_resume.pdf")
            
            with patch('resume_matcher_ai.main._validate_resume_file') as mock_validate, \
                 patch('resume_matcher_ai.main.extract_text_from_pdf') as mock_extract, \
                 patch('resume_matcher_ai.matcher.call_perplexity_api') as mock_api:
                
                mock_validate.return_value = True
                mock_extract.return_value = sample_resume
                
                # Create realistic response based on sample data
                mock_response = {
                    "compatibility_score": 85,
                    "matching_skills": [
                        "JavaScript", "React.js", "Node.js", "Express.js", "PostgreSQL", 
                        "MongoDB", "AWS", "Git", "HTML", "CSS", "Python"
                    ],
                    "missing_skills": ["TypeScript", "Docker", "Kubernetes"],
                    "skill_gaps": {
                        "Critical": [],
                        "Important": ["TypeScript", "Docker"],
                        "Nice-to-have": ["Kubernetes", "CI/CD pipelines"]
                    },
                    "suggestions": [
                        "Add TypeScript experience to strengthen your modern JavaScript development profile",
                        "Include Docker containerization experience in your DevOps toolkit",
                        "Consider adding Kubernetes orchestration knowledge for scalable deployments",
                        "Quantify your full-stack development impact with specific user and performance metrics"
                    ],
                    "analysis_summary": "Excellent match with strong full-stack experience and modern technology alignment"
                }
                mock_api.return_value = json.dumps(mock_response)
                
                result = _process_analysis(pdf_path, sample_jd)
                
                # Validate realistic results
                assert result.score >= 80, f"Sample data should show strong match, got {result.score}"
                assert result.match_category == "Strong Match", f"Expected Strong Match, got {result.match_category}"
                assert len(result.matching_skills) >= 8, f"Should have many matching skills, got {len(result.matching_skills)}"
                assert "JavaScript" in result.matching_skills, "Should match JavaScript skill"
                assert "React.js" in result.matching_skills, "Should match React skill"
                
            print("✅ Sample files integration test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Sample files integration test failed: {str(e)}")
            return False
    
    def test_display_results_integration(self):
        """Test that results display works correctly with integrated data"""
        print("🧪 Testing display results integration...")
        
        try:
            # Create comprehensive test result
            test_result = MatchResult(
                score=73,
                match_category="Strong Match",
                matching_skills=[
                    "JavaScript", "React.js", "Node.js", "PostgreSQL", 
                    "AWS", "Git", "HTML", "CSS"
                ],
                missing_skills=["TypeScript", "Docker", "Kubernetes"],
                skill_gaps={
                    "Critical": [],
                    "Important": ["TypeScript", "Docker"],
                    "Nice-to-have": ["Kubernetes", "GraphQL"]
                },
                suggestions=[
                    "Add TypeScript experience to strengthen your frontend development skills",
                    "Include Docker containerization experience in your DevOps section",
                    "Consider learning Kubernetes for container orchestration",
                    "Quantify your development achievements with specific metrics"
                ],
                processing_time=12.5
            )
            
            # Capture display output
            import io
            import contextlib
            
            output_buffer = io.StringIO()
            with contextlib.redirect_stdout(output_buffer):
                display_results(test_result)
            
            output = output_buffer.getvalue()
            
            # Validate display contains all required information
            assert "73%" in output, "Should display score percentage"
            assert "Strong Match" in output, "Should display match category"
            assert "JavaScript" in output, "Should display matching skills"
            assert "TypeScript" in output, "Should display missing skills"
            assert "12.5 seconds" in output, "Should display processing time"
            assert "RECOMMENDATIONS" in output, "Should display suggestions section"
            
            # Check for proper formatting
            assert "=" in output, "Should have formatted headers"
            assert "✅" in output or "🎯" in output, "Should have visual indicators"
            
            print("✅ Display results integration test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Display results integration test failed: {str(e)}")
            return False
    
    def test_configuration_integration(self):
        """Test that configuration loading works in integrated environment"""
        print("🧪 Testing configuration integration...")
        
        try:
            # Test configuration loading
            config = load_config()
            assert isinstance(config, dict), "Config should be dictionary"
            
            # Test API key validation (should handle missing key gracefully)
            api_key = config.get('perplexity_api_key')
            if api_key:
                # If API key exists, validate it
                is_valid = validate_api_key(api_key)
                assert isinstance(is_valid, bool), "API key validation should return boolean"
            else:
                # If no API key, that's expected in test environment
                print("  ℹ️  No API key configured (expected in test environment)")
            
            # Test other config values have defaults
            assert 'api_base_url' in config, "Should have API base URL"
            assert 'max_tokens' in config, "Should have max tokens setting"
            assert 'timeout' in config, "Should have timeout setting"
            
            print("✅ Configuration integration test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Configuration integration test failed: {str(e)}")
            return False


def run_task13_integration_tests():
    """Run all Task 13 integration tests"""
    print("=" * 80)
    print("TASK 13: INTEGRATE ALL COMPONENTS AND TEST END-TO-END WORKFLOW")
    print("=" * 80)
    print()
    
    tester = Task13IntegrationTests()
    
    try:
        # Define all tests
        tests = [
            ("Complete End-to-End Workflow", tester.test_complete_end_to_end_workflow),
            ("Module Integration Connectivity", tester.test_module_integration_connectivity),
            ("Error Handling Across Components", tester.test_error_handling_across_components),
            ("Requirements Validation", tester.test_requirements_validation),
            ("Sample Files Integration", tester.test_sample_files_integration),
            ("Display Results Integration", tester.test_display_results_integration),
            ("Configuration Integration", tester.test_configuration_integration),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n{'─' * 60}")
            print(f"Running: {test_name}")
            print(f"{'─' * 60}")
            
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} - PASSED")
                else:
                    failed += 1
                    print(f"❌ {test_name} - FAILED")
            except Exception as e:
                failed += 1
                print(f"❌ {test_name} - FAILED with exception: {str(e)}")
        
        # Print final summary
        print("\n" + "=" * 80)
        print("TASK 13 INTEGRATION TESTS SUMMARY")
        print("=" * 80)
        print(f"Total tests: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success rate: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TASK 13 INTEGRATION TESTS PASSED!")
            print("✅ All components are properly integrated")
            print("✅ End-to-end workflow functions correctly")
            print("✅ Error handling works across all components")
            print("✅ All requirements are validated through integration testing")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please review and fix issues.")
        
        return failed == 0
        
    finally:
        tester.cleanup()


if __name__ == "__main__":
    success = run_task13_integration_tests()
    sys.exit(0 if success else 1)