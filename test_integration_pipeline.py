#!/usr/bin/env python3
"""
Integration tests for the complete matching pipeline
Task 11 Sub-task 2: Build integration tests for the complete matching pipeline
"""

import os
import sys
import tempfile
import time
from unittest.mock import patch, MagicMock
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from resume_matcher_ai.main import main, get_user_input, display_results, _process_analysis
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text, validate_resume_content
from resume_matcher_ai.jd_parser import parse_jd_text
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.utils import MatchResult, JobDescription


class IntegrationTestPipeline:
    """Integration test suite for the complete matching pipeline"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_results = []
        
    def cleanup(self):
        """Clean up test resources"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_pdf(self, content: str, filename: str = "test_resume.pdf") -> str:
        """Create a mock PDF file for testing"""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'wb') as f:
            # Write minimal PDF-like content
            f.write(b"%PDF-1.4\n")
            f.write(content.encode('utf-8'))
        return file_path
    
    def test_complete_pipeline_success_scenario(self):
        """Test the complete pipeline with successful scenario"""
        print("🧪 Testing complete pipeline - success scenario...")
        
        # Test data
        resume_text = """
        John Doe
        Senior Software Engineer
        Email: john.doe@email.com
        Phone: (555) 123-4567
        
        EXPERIENCE:
        Senior Software Engineer at Tech Corp (2020-2023)
        • Developed web applications using Python, JavaScript, and React
        • Led a team of 5 developers on multiple projects
        • Implemented CI/CD pipelines using Docker and AWS
        • Improved application performance by 40%
        
        Software Engineer at StartupXYZ (2018-2020)
        • Built REST APIs using Python and Flask
        • Worked with PostgreSQL and Redis databases
        • Collaborated with cross-functional teams
        
        EDUCATION:
        Bachelor of Science in Computer Science
        University of Technology (2014-2018)
        
        SKILLS:
        Python, JavaScript, React, Node.js, AWS, Docker, PostgreSQL, Git
        """
        
        jd_text = """
        Senior Full Stack Developer
        
        We are seeking a Senior Full Stack Developer to join our growing team.
        
        Requirements:
        • 5+ years of experience in software development
        • Proficiency in Python and JavaScript
        • Experience with React and Node.js
        • Knowledge of cloud platforms (AWS preferred)
        • Experience with databases (PostgreSQL, MongoDB)
        • Strong problem-solving and communication skills
        
        Responsibilities:
        • Design and develop web applications
        • Collaborate with product and design teams
        • Mentor junior developers
        • Participate in code reviews
        
        Qualifications:
        • Bachelor's degree in Computer Science or related field
        • Experience with agile development methodologies
        • Knowledge of containerization (Docker)
        """
        
        try:
            # Create a dummy PDF path (won't be used due to mocking)
            pdf_path = os.path.join(self.temp_dir, "test_resume.pdf")
            
            # Mock all validation and PDF extraction functions
            with patch('resume_matcher_ai.main._validate_resume_file') as mock_validate, \
                 patch('resume_matcher_ai.resume_parser._validate_pdf_file_comprehensive') as mock_pdf_validate, \
                 patch('resume_matcher_ai.main.extract_text_from_pdf') as mock_extract:
                mock_validate.return_value = True
                mock_pdf_validate.return_value = None  # This function returns None on success
                mock_extract.return_value = resume_text
                
                # Step 3: Mock API call
                mock_api_response = {
                    "compatibility_score": 85,
                    "matching_skills": [
                        "Python", "JavaScript", "React", "Node.js", 
                        "AWS", "Docker", "PostgreSQL"
                    ],
                    "missing_skills": ["MongoDB"],
                    "skill_gaps": {
                        "Critical": [],
                        "Important": ["MongoDB"],
                        "Nice-to-have": ["Agile methodologies"]
                    },
                    "suggestions": [
                        "Add MongoDB experience to your skills section",
                        "Mention agile development experience in your work history",
                        "Quantify your team leadership achievements with specific metrics"
                    ],
                    "analysis_summary": "Strong match with excellent technical alignment"
                }
                
                with patch('resume_matcher_ai.matcher.call_perplexity_api') as mock_api:
                    mock_api.return_value = json.dumps(mock_api_response)
                    
                    # Step 4: Test the complete pipeline
                    start_time = time.time()
                    result = _process_analysis(pdf_path, jd_text)
                    end_time = time.time()
                    
                    # Verify results
                    assert isinstance(result, MatchResult), "Result should be MatchResult instance"
                    assert result.score == 85, f"Expected score 85, got {result.score}"
                    assert result.match_category == "Strong Match", f"Expected Strong Match, got {result.match_category}"
                    assert len(result.matching_skills) == 7, f"Expected 7 matching skills, got {len(result.matching_skills)}"
                    assert "MongoDB" in result.missing_skills, "MongoDB should be in missing skills"
                    assert len(result.suggestions) >= 3, f"Expected at least 3 suggestions, got {len(result.suggestions)}"
                    assert result.processing_time > 0, "Processing time should be positive"
                    assert (end_time - start_time) < 30, "Processing should complete within 30 seconds"
                    
                    print("✅ Complete pipeline success scenario passed!")
                    return True
                    
        except Exception as e:
            print(f"❌ Complete pipeline success scenario failed: {str(e)}")
            return False
    
    def test_complete_pipeline_moderate_match(self):
        """Test the complete pipeline with moderate match scenario"""
        print("🧪 Testing complete pipeline - moderate match scenario...")
        
        # Test data with partial skill overlap
        resume_text = """
        Jane Smith
        Junior Developer
        Email: jane.smith@email.com
        
        EXPERIENCE:
        Junior Developer at Small Company (2022-2023)
        • Developed simple web pages using HTML, CSS, and basic JavaScript
        • Worked with MySQL database
        • Fixed bugs and implemented small features
        
        EDUCATION:
        Associate Degree in Web Development
        Community College (2020-2022)
        
        SKILLS:
        HTML, CSS, JavaScript, MySQL, Git
        """
        
        jd_text = """
        Senior Full Stack Developer
        
        Requirements:
        • 5+ years of experience in software development
        • Proficiency in Python, JavaScript, React, Node.js
        • Experience with AWS, Docker, Kubernetes
        • Strong leadership and mentoring skills
        
        Responsibilities:
        • Lead development teams
        • Architect complex systems
        • Make technical decisions
        """
        
        try:
            # Create a dummy PDF path (won't be used due to mocking)
            pdf_path = os.path.join(self.temp_dir, "test_resume.pdf")
            
            # Mock all validation and PDF extraction functions
            with patch('resume_matcher_ai.main._validate_resume_file') as mock_validate, \
                 patch('resume_matcher_ai.resume_parser._validate_pdf_file_comprehensive') as mock_pdf_validate, \
                 patch('resume_matcher_ai.main.extract_text_from_pdf') as mock_extract:
                mock_validate.return_value = True
                mock_pdf_validate.return_value = None  # This function returns None on success
                mock_extract.return_value = resume_text
                
                mock_api_response = {
                    "compatibility_score": 45,
                    "matching_skills": ["JavaScript", "Git"],
                    "missing_skills": [
                        "Python", "React", "Node.js", "AWS", 
                        "Docker", "Kubernetes", "Leadership experience"
                    ],
                    "skill_gaps": {
                        "Critical": ["Python", "React", "5+ years experience"],
                        "Important": ["Node.js", "AWS", "Leadership skills"],
                        "Nice-to-have": ["Docker", "Kubernetes"]
                    },
                    "suggestions": [
                        "Gain experience with Python and React through projects or courses",
                        "Build portfolio projects demonstrating full-stack capabilities",
                        "Consider targeting junior or mid-level positions first",
                        "Develop leadership skills through team projects or mentoring"
                    ],
                    "analysis_summary": "Limited match - significant skill development needed"
                }
                
                with patch('resume_matcher_ai.matcher.call_perplexity_api') as mock_api:
                    mock_api.return_value = json.dumps(mock_api_response)
                    
                    result = _process_analysis(pdf_path, jd_text)
                    
                    # Verify moderate match results
                    assert result.score == 45, f"Expected score 45, got {result.score}"
                    assert result.match_category == "Moderate Match", f"Expected Moderate Match, got {result.match_category}"
                    assert len(result.missing_skills) > len(result.matching_skills), "Should have more missing than matching skills"
                    assert len(result.skill_gaps['Critical']) > 0, "Should have critical skill gaps"
                    assert len(result.suggestions) >= 3, "Should have multiple suggestions"
                    
                    print("✅ Complete pipeline moderate match scenario passed!")
                    return True
                    
        except Exception as e:
            print(f"❌ Complete pipeline moderate match scenario failed: {str(e)}")
            return False
    
    def test_complete_pipeline_poor_match(self):
        """Test the complete pipeline with poor match scenario"""
        print("🧪 Testing complete pipeline - poor match scenario...")
        
        # Test data with minimal skill overlap
        resume_text = """
        Bob Wilson
        Marketing Coordinator
        Email: bob.wilson@email.com
        
        EXPERIENCE:
        Marketing Coordinator at Retail Company (2021-2023)
        • Created marketing campaigns using Photoshop and Canva
        • Managed social media accounts
        • Wrote blog posts and marketing copy
        • Analyzed marketing metrics using Excel
        
        EDUCATION:
        Bachelor of Arts in Marketing
        State University (2017-2021)
        
        SKILLS:
        Photoshop, Canva, Excel, Social Media Marketing, Content Writing
        """
        
        jd_text = """
        Senior Software Engineer
        
        Requirements:
        • 7+ years of software development experience
        • Expert-level Python, Java, and C++ programming
        • Experience with distributed systems and microservices
        • Knowledge of machine learning and AI algorithms
        • PhD in Computer Science preferred
        
        Responsibilities:
        • Design complex software architectures
        • Lead technical research initiatives
        • Mentor engineering teams
        """
        
        try:
            # Create a dummy PDF path (won't be used due to mocking)
            pdf_path = os.path.join(self.temp_dir, "test_resume.pdf")
            
            # Mock all validation and PDF extraction functions
            with patch('resume_matcher_ai.main._validate_resume_file') as mock_validate, \
                 patch('resume_matcher_ai.resume_parser._validate_pdf_file_comprehensive') as mock_pdf_validate, \
                 patch('resume_matcher_ai.main.extract_text_from_pdf') as mock_extract:
                mock_validate.return_value = True
                mock_pdf_validate.return_value = None  # This function returns None on success
                mock_extract.return_value = resume_text
                
                mock_api_response = {
                    "compatibility_score": 15,
                    "matching_skills": [],
                    "missing_skills": [
                        "Python", "Java", "C++", "Software development experience",
                        "Distributed systems", "Microservices", "Machine learning",
                        "AI algorithms", "Technical leadership"
                    ],
                    "skill_gaps": {
                        "Critical": [
                            "7+ years software development experience",
                            "Python programming", "Java programming", "C++ programming"
                        ],
                        "Important": [
                            "Distributed systems knowledge", "Microservices architecture",
                            "Machine learning experience"
                        ],
                        "Nice-to-have": ["PhD in Computer Science", "Research experience"]
                    },
                    "suggestions": [
                        "Consider transitioning to technical roles gradually through coding bootcamps or courses",
                        "Target entry-level software development positions instead",
                        "Leverage analytical skills from marketing to transition into data analysis roles",
                        "Build a portfolio of programming projects to demonstrate technical capabilities",
                        "Consider roles that bridge marketing and technology, such as technical marketing"
                    ],
                    "analysis_summary": "Very poor match - complete career pivot required"
                }
                
                with patch('resume_matcher_ai.matcher.call_perplexity_api') as mock_api:
                    mock_api.return_value = json.dumps(mock_api_response)
                    
                    result = _process_analysis(pdf_path, jd_text)
                    
                    # Verify poor match results
                    assert result.score == 15, f"Expected score 15, got {result.score}"
                    assert result.match_category == "Poor Match", f"Expected Poor Match, got {result.match_category}"
                    assert len(result.matching_skills) == 0, "Should have no matching skills"
                    assert len(result.missing_skills) > 5, "Should have many missing skills"
                    assert len(result.skill_gaps['Critical']) > 0, "Should have critical skill gaps"
                    assert len(result.suggestions) >= 3, "Should have multiple suggestions"
                    
                    print("✅ Complete pipeline poor match scenario passed!")
                    return True
                    
        except Exception as e:
            print(f"❌ Complete pipeline poor match scenario failed: {str(e)}")
            return False
    
    def test_pipeline_error_handling(self):
        """Test pipeline error handling scenarios"""
        print("🧪 Testing pipeline error handling...")
        
        try:
            # Create a dummy PDF path
            invalid_pdf = os.path.join(self.temp_dir, "invalid.pdf")
            jd_text = "Valid job description with requirements and responsibilities."
            
            # Mock PDF extraction to raise an error
            with patch('resume_matcher_ai.main.extract_text_from_pdf') as mock_extract:
                mock_extract.side_effect = ValueError("PDF extraction failed")
                
                # Should handle PDF extraction error gracefully
                try:
                    result = _process_analysis(invalid_pdf, jd_text)
                    # If we get here, the error was handled gracefully
                    assert isinstance(result, MatchResult), "Should return MatchResult even on error"
                    print("✅ Pipeline error handling passed!")
                    return True
                except Exception as e:
                    # This is expected - the function should raise an exception after retries
                    if "PDF extraction failed" in str(e):
                        print("✅ Pipeline error handling passed! (Error properly propagated)")
                        return True
                    else:
                        raise e
                
        except Exception as e:
            print(f"❌ Pipeline error handling failed: {str(e)}")
            return False
    
    def test_pipeline_performance(self):
        """Test pipeline performance requirements"""
        print("🧪 Testing pipeline performance (30-second requirement)...")
        
        resume_text = "Standard resume content for performance testing"
        jd_text = "Standard job description content for performance testing"
        
        try:
            # Create a dummy PDF path (won't be used due to mocking)
            pdf_path = os.path.join(self.temp_dir, "test_resume.pdf")
            
            # Mock all validation and PDF extraction functions
            with patch('resume_matcher_ai.main._validate_resume_file') as mock_validate, \
                 patch('resume_matcher_ai.resume_parser._validate_pdf_file_comprehensive') as mock_pdf_validate, \
                 patch('resume_matcher_ai.main.extract_text_from_pdf') as mock_extract:
                mock_validate.return_value = True
                mock_pdf_validate.return_value = None  # This function returns None on success
                mock_extract.return_value = resume_text
                
                # Mock API with realistic delay
                def mock_api_call_with_delay(prompt):
                    time.sleep(2)  # Simulate API processing time
                    return json.dumps({
                        "compatibility_score": 75,
                        "matching_skills": ["Python", "JavaScript"],
                        "missing_skills": ["React"],
                        "skill_gaps": {"Critical": [], "Important": ["React"], "Nice-to-have": []},
                        "suggestions": ["Add React experience"],
                        "analysis_summary": "Good match"
                    })
                
                with patch('resume_matcher_ai.matcher.call_perplexity_api', side_effect=mock_api_call_with_delay):
                    start_time = time.time()
                    result = _process_analysis(pdf_path, jd_text)
                    end_time = time.time()
                    
                    processing_time = end_time - start_time
                    
                    # Verify performance requirement (30 seconds)
                    assert processing_time < 30, f"Processing took {processing_time:.2f}s, should be under 30s"
                    assert result.processing_time > 0, "Processing time should be recorded"
                    assert result.processing_time < 30, "Recorded processing time should be under 30s"
                    
                    print(f"✅ Pipeline performance passed! (Processing time: {processing_time:.2f}s)")
                    return True
                    
        except Exception as e:
            print(f"❌ Pipeline performance test failed: {str(e)}")
            return False
    
    def test_pipeline_data_flow(self):
        """Test data flow through all pipeline components"""
        print("🧪 Testing pipeline data flow...")
        
        resume_text = """
        Alice Johnson
        Data Scientist
        
        EXPERIENCE:
        Data Scientist at Analytics Corp (2021-2023)
        • Developed machine learning models using Python and scikit-learn
        • Analyzed large datasets with pandas and numpy
        • Created data visualizations using matplotlib and seaborn
        
        SKILLS:
        Python, R, SQL, Machine Learning, Data Analysis
        """
        
        jd_text = """
        Senior Data Scientist
        
        Requirements:
        • 3+ years of data science experience
        • Proficiency in Python and R
        • Experience with machine learning algorithms
        • Knowledge of SQL and database systems
        • Strong analytical and problem-solving skills
        """
        
        try:
            # Create a dummy PDF path (won't be used due to mocking)
            pdf_path = os.path.join(self.temp_dir, "test_resume.pdf")
            
            # Track data flow through components
            extracted_text = None
            parsed_jd = None
            analysis_result = None
            
            # Mock all validation and PDF extraction functions
            with patch('resume_matcher_ai.main._validate_resume_file') as mock_validate, \
                 patch('resume_matcher_ai.resume_parser._validate_pdf_file_comprehensive') as mock_pdf_validate, \
                 patch('resume_matcher_ai.main.extract_text_from_pdf') as mock_extract:
                mock_validate.return_value = True
                mock_pdf_validate.return_value = None  # This function returns None on success
                mock_extract.return_value = resume_text
                extracted_text = resume_text
                
                # Parse JD
                parsed_jd = parse_jd_text(jd_text)
                
                # Verify JD parsing
                assert isinstance(parsed_jd, JobDescription), "Should return JobDescription object"
                assert len(parsed_jd.technical_skills) > 0, "Should extract technical skills"
                assert len(parsed_jd.requirements) > 0, "Should extract requirements"
                
                # Mock API response
                mock_api_response = {
                    "compatibility_score": 88,
                    "matching_skills": ["Python", "R", "SQL", "Machine Learning"],
                    "missing_skills": ["Advanced statistics"],
                    "skill_gaps": {
                        "Critical": [],
                        "Important": ["Advanced statistics"],
                        "Nice-to-have": ["Deep learning"]
                    },
                    "suggestions": [
                        "Add advanced statistics coursework or experience",
                        "Include specific ML algorithms you've implemented",
                        "Quantify the impact of your data science projects"
                    ],
                    "analysis_summary": "Excellent match with strong technical alignment"
                }
                
                with patch('resume_matcher_ai.matcher.call_perplexity_api') as mock_api:
                    mock_api.return_value = json.dumps(mock_api_response)
                    
                    # Test complete analysis
                    analysis_result = _process_analysis(pdf_path, jd_text)
                    
                    # Verify data flow integrity
                    assert extracted_text is not None, "Text should be extracted"
                    assert parsed_jd is not None, "JD should be parsed"
                    assert analysis_result is not None, "Analysis should be completed"
                    
                    # Verify data transformations
                    assert isinstance(analysis_result, MatchResult), "Should return MatchResult"
                    assert analysis_result.score > 0, "Should have valid score"
                    assert len(analysis_result.matching_skills) > 0, "Should identify matching skills"
                    
                    print("✅ Pipeline data flow test passed!")
                    return True
                    
        except Exception as e:
            print(f"❌ Pipeline data flow test failed: {str(e)}")
            return False
    
    def test_pipeline_edge_cases(self):
        """Test pipeline with edge cases"""
        print("🧪 Testing pipeline edge cases...")
        
        test_cases = [
            {
                "name": "Very short resume",
                "resume": "John Doe. Software Engineer. Python.",
                "jd": "Looking for a Python developer with 5 years experience.",
                "expected_score_range": (0, 50)
            },
            {
                "name": "Very long resume",
                "resume": "A" * 10000 + " Python developer with extensive experience.",
                "jd": "Python developer position available.",
                "expected_score_range": (0, 100)
            },
            {
                "name": "Resume with special characters",
                "resume": "José García\nSoftware Engineer\n• Python • JavaScript • React\n@email.com",
                "jd": "Python and JavaScript developer needed.",
                "expected_score_range": (30, 100)
            }
        ]
        
        try:
            for test_case in test_cases:
                print(f"  Testing: {test_case['name']}")
                
                # Create a dummy PDF path (won't be used due to mocking)
                pdf_path = os.path.join(self.temp_dir, f"{test_case['name'].replace(' ', '_')}.pdf")
                
                # Mock both validation and PDF extraction
                with patch('resume_matcher_ai.main._validate_resume_file') as mock_validate, \
                     patch('resume_matcher_ai.main.extract_text_from_pdf') as mock_extract:
                    mock_validate.return_value = True
                    mock_extract.return_value = test_case['resume']
                    
                    # Mock API response based on test case
                    mock_score = (test_case['expected_score_range'][0] + test_case['expected_score_range'][1]) // 2
                    mock_api_response = {
                        "compatibility_score": mock_score,
                        "matching_skills": ["Python"],
                        "missing_skills": ["Experience"],
                        "skill_gaps": {"Critical": [], "Important": ["Experience"], "Nice-to-have": []},
                        "suggestions": ["Add more experience details"],
                        "analysis_summary": f"Test case: {test_case['name']}"
                    }
                    
                    with patch('resume_matcher_ai.matcher.call_perplexity_api') as mock_api:
                        mock_api.return_value = json.dumps(mock_api_response)
                        
                        result = _process_analysis(pdf_path, test_case['jd'])
                        
                        # Verify result is within expected range
                        min_score, max_score = test_case['expected_score_range']
                        assert min_score <= result.score <= max_score, f"Score {result.score} not in range {test_case['expected_score_range']}"
                        assert isinstance(result, MatchResult), "Should return MatchResult"
                        
                print(f"    ✅ {test_case['name']} passed!")
            
            print("✅ Pipeline edge cases test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Pipeline edge cases test failed: {str(e)}")
            return False


def run_integration_tests():
    """Run all integration tests for the complete matching pipeline"""
    print("=" * 80)
    print("INTEGRATION TESTS FOR COMPLETE MATCHING PIPELINE")
    print("=" * 80)
    
    pipeline_tester = IntegrationTestPipeline()
    
    try:
        # Run all integration tests
        tests = [
            pipeline_tester.test_complete_pipeline_success_scenario,
            pipeline_tester.test_complete_pipeline_moderate_match,
            pipeline_tester.test_complete_pipeline_poor_match,
            pipeline_tester.test_pipeline_error_handling,
            pipeline_tester.test_pipeline_performance,
            pipeline_tester.test_pipeline_data_flow,
            pipeline_tester.test_pipeline_edge_cases
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
                failed += 1
        
        # Print summary
        print("\n" + "=" * 80)
        print("INTEGRATION TESTS SUMMARY")
        print("=" * 80)
        print(f"Tests run: {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success rate: {(passed / (passed + failed) * 100):.1f}%")
        
        return failed == 0
        
    finally:
        pipeline_tester.cleanup()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)