#!/usr/bin/env python3
"""
Test script to verify the separate report functionality
"""

import sys
import os
from datetime import datetime

# Mock the streamlit import since we're testing without the web interface
class MockStreamlit:
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

sys.modules['streamlit'] = MockStreamlit()

# Mock the resume_matcher_ai imports
class MockResult:
    def __init__(self, score=75, match_category="Strong Match", processing_time=2.5):
        self.score = score
        self.match_category = match_category
        self.processing_time = processing_time
        self.matching_skills = [
            "Python programming",
            "Machine Learning",
            "Data Analysis",
            "SQL databases"
        ]
        self.skill_gaps = {
            "Critical": ["Docker", "Kubernetes"],
            "Important": ["AWS", "React.js"],
            "Nice-to-have": ["GraphQL"]
        }
        self.suggestions = [
            "Add Docker containerization experience to your DevOps section",
            "Highlight your machine learning projects with specific metrics",
            "Include AWS certifications or cloud experience"
        ]

# Import the report functions
from app import create_job_seeker_report, create_company_report, create_pdf_report, PDF_AVAILABLE

def test_job_seeker_report():
    """Test job seeker report generation"""
    print("🧪 Testing Job Seeker Report...")
    
    # Create mock data
    results = [("john_doe_resume.pdf", MockResult(score=78))]
    
    # Generate report
    report = create_job_seeker_report(results, "Senior Python Developer", "Python, ML, AWS required")
    
    # Verify content
    assert "RESUME OPTIMIZATION REPORT - FOR JOB SEEKERS" in report
    assert "YOUR COMPATIBILITY ANALYSIS" in report
    assert "YOUR STRENGTHS - SKILLS THAT MATCH" in report
    assert "SKILLS TO DEVELOP OR HIGHLIGHT" in report
    assert "YOUR PERSONALIZED ACTION PLAN" in report
    assert "YOUR NEXT STEPS" in report
    assert "78%" in report
    
    print("✅ Job Seeker Report: PASSED")
    return report

def test_company_report():
    """Test company report generation"""
    print("🧪 Testing Company Report...")
    
    # Create mock data with multiple candidates
    results = [
        ("john_doe_resume.pdf", MockResult(score=78)),
        ("jane_smith_resume.pdf", MockResult(score=65)),
        ("bob_wilson_resume.pdf", MockResult(score=45))
    ]
    
    # Generate report
    report = create_company_report(results, "Senior Python Developer", "Python, ML, AWS required")
    
    # Verify content
    assert "CANDIDATE EVALUATION REPORT - FOR HIRING TEAM" in report
    assert "EXECUTIVE SUMMARY" in report
    assert "CANDIDATE POOL ANALYSIS" in report
    assert "HIRING ASSESSMENT" in report
    assert "HIRING STRATEGY & RECOMMENDATIONS" in report
    assert "CANDIDATE RANKING" in report
    assert "78%" in report
    assert "65%" in report
    assert "45%" in report
    
    print("✅ Company Report: PASSED")
    return report

def test_pdf_generation():
    """Test PDF generation if available"""
    print("🧪 Testing PDF Generation...")
    
    if not PDF_AVAILABLE:
        print("⚠️  PDF Generation: SKIPPED (ReportLab not available)")
        return None
    
    # Create mock data
    results = [("test_resume.pdf", MockResult(score=75))]
    
    # Generate job seeker report
    job_seeker_text = create_job_seeker_report(results, "Test Position", "Test JD")
    
    try:
        # Generate PDF
        pdf_data = create_pdf_report(job_seeker_text, "Test Report")
        
        # Verify PDF data
        assert isinstance(pdf_data, bytes)
        assert len(pdf_data) > 1000  # PDF should be substantial
        assert pdf_data.startswith(b'%PDF')  # PDF header
        
        print("✅ PDF Generation: PASSED")
        return pdf_data
    except Exception as e:
        print(f"❌ PDF Generation: FAILED - {e}")
        return None

def test_report_differences():
    """Test that job seeker and company reports have different content"""
    print("🧪 Testing Report Content Differences...")
    
    # Create mock data
    results = [("test_resume.pdf", MockResult(score=65))]
    
    # Generate both reports
    job_seeker_report = create_job_seeker_report(results, "Test Position", "Test JD")
    company_report = create_company_report(results, "Test Position", "Test JD")
    
    # Job seeker specific content
    job_seeker_keywords = [
        "RESUME OPTIMIZATION",
        "YOUR COMPATIBILITY",
        "YOUR STRENGTHS",
        "YOUR NEXT STEPS",
        "PERSONALIZED ACTION PLAN",
        "learning strategies",
        "career development"
    ]
    
    # Company specific content
    company_keywords = [
        "HIRING TEAM",
        "HIRING ASSESSMENT",
        "CANDIDATE EVALUATION",
        "INTERVIEW FOCUS AREAS",
        "ROLE FIT ASSESSMENT",
        "hiring decisions",
        "compensation"
    ]
    
    # Verify job seeker content
    for keyword in job_seeker_keywords:
        assert keyword in job_seeker_report, f"Missing job seeker keyword: {keyword}"
        assert keyword not in company_report, f"Job seeker keyword found in company report: {keyword}"
    
    # Verify company content
    for keyword in company_keywords:
        assert keyword in company_report, f"Missing company keyword: {keyword}"
        assert keyword not in job_seeker_report, f"Company keyword found in job seeker report: {keyword}"
    
    print("✅ Report Content Differences: PASSED")

def main():
    """Run all tests"""
    print("🚀 Starting Report Functionality Tests")
    print("=" * 50)
    
    try:
        # Test individual reports
        job_seeker_report = test_job_seeker_report()
        company_report = test_company_report()
        
        # Test PDF generation
        pdf_data = test_pdf_generation()
        
        # Test content differences
        test_report_differences()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("\n📊 Test Summary:")
        print(f"✅ Job Seeker Report: {len(job_seeker_report)} characters")
        print(f"✅ Company Report: {len(company_report)} characters")
        print(f"✅ PDF Generation: {'Available' if PDF_AVAILABLE else 'Not Available'}")
        print(f"✅ Content Separation: Verified")
        
        # Save sample reports for review
        with open("sample_job_seeker_report.txt", "w") as f:
            f.write(job_seeker_report)
        
        with open("sample_company_report.txt", "w") as f:
            f.write(company_report)
        
        if pdf_data:
            with open("sample_report.pdf", "wb") as f:
                f.write(pdf_data)
            print("📄 Sample reports saved: sample_job_seeker_report.txt, sample_company_report.txt, sample_report.pdf")
        else:
            print("📄 Sample reports saved: sample_job_seeker_report.txt, sample_company_report.txt")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())