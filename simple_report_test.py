#!/usr/bin/env python3
"""
Simple test to verify report functions exist and have correct structure
"""

def test_app_structure():
    """Test that the app.py file has the correct structure"""
    print("🧪 Testing App Structure...")
    
    with open("app.py", "r") as f:
        content = f.read()
    
    # Check for required functions
    required_functions = [
        "def create_job_seeker_report(",
        "def create_company_report(",
        "def create_pdf_report(",
        "PDF_AVAILABLE"
    ]
    
    for func in required_functions:
        if func in content:
            print(f"✅ Found: {func}")
        else:
            print(f"❌ Missing: {func}")
            return False
    
    # Check for job seeker specific content
    job_seeker_content = [
        "RESUME OPTIMIZATION REPORT - FOR JOB SEEKERS",
        "YOUR COMPATIBILITY ANALYSIS",
        "YOUR STRENGTHS - SKILLS THAT MATCH",
        "SKILLS TO DEVELOP OR HIGHLIGHT",
        "YOUR PERSONALIZED ACTION PLAN",
        "YOUR NEXT STEPS"
    ]
    
    for content_check in job_seeker_content:
        if content_check in content:
            print(f"✅ Job Seeker Content: {content_check[:30]}...")
        else:
            print(f"❌ Missing Job Seeker Content: {content_check}")
            return False
    
    # Check for company specific content
    company_content = [
        "CANDIDATE EVALUATION REPORT - FOR HIRING TEAM",
        "EXECUTIVE SUMMARY",
        "CANDIDATE POOL ANALYSIS",
        "HIRING ASSESSMENT",
        "HIRING STRATEGY & RECOMMENDATIONS",
        "INTERVIEW FOCUS AREAS"
    ]
    
    for content_check in company_content:
        if content_check in content:
            print(f"✅ Company Content: {content_check[:30]}...")
        else:
            print(f"❌ Missing Company Content: {content_check}")
            return False
    
    # Check for UI elements
    ui_elements = [
        "Select report type:",
        "Job Seeker Report (Resume Optimization)",
        "Company Report (Hiring Decision)",
        "CSV Summary",
        "Text Report", 
        "PDF Report"
    ]
    
    for ui_element in ui_elements:
        if ui_element in content:
            print(f"✅ UI Element: {ui_element}")
        else:
            print(f"❌ Missing UI Element: {ui_element}")
            return False
    
    print("✅ App Structure: PASSED")
    return True

def test_requirements():
    """Test that requirements.txt includes reportlab"""
    print("\n🧪 Testing Requirements...")
    
    with open("requirements.txt", "r") as f:
        content = f.read()
    
    if "reportlab" in content:
        print("✅ ReportLab dependency found in requirements.txt")
        return True
    else:
        print("❌ ReportLab dependency missing from requirements.txt")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Simple Report Tests")
    print("=" * 50)
    
    try:
        # Test app structure
        structure_ok = test_app_structure()
        
        # Test requirements
        requirements_ok = test_requirements()
        
        if structure_ok and requirements_ok:
            print("\n" + "=" * 50)
            print("🎉 ALL TESTS PASSED!")
            print("\n📊 Implementation Summary:")
            print("✅ Separate Job Seeker and Company reports implemented")
            print("✅ PDF generation functionality added")
            print("✅ UI updated with report type selection")
            print("✅ ReportLab dependency included")
            print("\n🚀 Ready to test with: streamlit run app.py")
            return 0
        else:
            print("\n❌ SOME TESTS FAILED")
            return 1
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1

if __name__ == "__main__":
    exit(main())