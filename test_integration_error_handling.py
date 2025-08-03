#!/usr/bin/env python3
"""
Integration test to verify error handling works in the main application flow
"""
import os
import sys
import tempfile

# Add the resume_matcher_ai module to the path
sys.path.append('resume_matcher_ai')

from resume_matcher_ai.main import _validate_resume_file, _process_analysis
from resume_matcher_ai.resume_parser import extract_text_from_pdf
from resume_matcher_ai.jd_parser import parse_jd_text

def test_resume_validation_integration():
    """Test resume validation in the main application context"""
    print("🧪 Testing resume validation integration...")
    
    # Test with non-existent file
    result = _validate_resume_file('nonexistent.pdf')
    if result is True:
        print("❌ Should have returned error message for non-existent file")
        return False
    
    if "not found" not in result.lower():
        print(f"❌ Error message should mention 'not found': {result}")
        return False
    
    print("✅ Resume validation correctly handles non-existent files")
    
    # Test with wrong extension
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
        tmp_file.write(b'test content')
        tmp_file_path = tmp_file.name
    
    try:
        result = _validate_resume_file(tmp_file_path)
        if result is True:
            print("❌ Should have returned error message for wrong extension")
            return False
        
        if "must be a pdf" not in result.lower():
            print(f"❌ Error message should mention PDF requirement: {result}")
            return False
        
        print("✅ Resume validation correctly handles wrong file extensions")
    finally:
        os.unlink(tmp_file_path)
    
    return True

def test_jd_parsing_integration():
    """Test job description parsing with error handling"""
    print("\n🧪 Testing job description parsing integration...")
    
    # Test with empty JD
    try:
        parse_jd_text('')
        print("❌ Should have raised ValueError for empty JD")
        return False
    except ValueError as e:
        if "empty" not in str(e).lower():
            print(f"❌ Error message should mention 'empty': {e}")
            return False
        print("✅ JD parsing correctly handles empty input")
    
    # Test with valid JD
    valid_jd = """
    Senior Software Engineer
    
    We are looking for a Senior Software Engineer to join our growing team.
    
    Key Responsibilities:
    - Design and develop scalable web applications
    - Work with Python, JavaScript, React, and Node.js
    - Collaborate with product managers and designers
    - Mentor junior developers
    
    Requirements:
    - Bachelor's degree in Computer Science or related field
    - 5+ years of experience in software development
    - Strong proficiency in Python and JavaScript
    - Experience with React, Node.js, and SQL databases
    - Excellent communication and problem-solving skills
    
    Nice to have:
    - Experience with AWS or other cloud platforms
    - Knowledge of Docker and Kubernetes
    - Previous experience in a startup environment
    """
    
    try:
        jd_data = parse_jd_text(valid_jd)
        if not jd_data.title or not jd_data.requirements:
            print("❌ JD parsing should extract title and requirements")
            return False
        print("✅ JD parsing correctly handles valid input")
    except Exception as e:
        print(f"❌ JD parsing failed with valid input: {e}")
        return False
    
    return True

def test_error_propagation():
    """Test that errors are properly propagated through the system"""
    print("\n🧪 Testing error propagation...")
    
    # Test that file errors are properly caught and handled
    try:
        # This should fail gracefully without crashing
        result = _validate_resume_file('definitely_nonexistent_file.pdf')
        if result is True:
            print("❌ Should have returned error for non-existent file")
            return False
        print("✅ File errors are properly handled and returned")
    except Exception as e:
        print(f"❌ File validation should not raise exceptions: {e}")
        return False
    
    return True

def main():
    """Run integration tests for error handling"""
    print("🚀 Starting error handling integration tests...\n")
    
    tests = [
        ("Resume Validation Integration", test_resume_validation_integration),
        ("Job Description Parsing Integration", test_jd_parsing_integration),
        ("Error Propagation", test_error_propagation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name} tests passed")
                passed += 1
            else:
                print(f"❌ {test_name} tests failed")
        except Exception as e:
            print(f"❌ {test_name} tests failed with exception: {e}")
    
    print(f"\n📊 Integration Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        print("\n✅ Comprehensive error handling implementation is working correctly!")
        return True
    else:
        print("⚠️  Some integration tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)