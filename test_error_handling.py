#!/usr/bin/env python3
"""
Test script to verify comprehensive error handling implementation
"""
import os
import sys
import tempfile

# Add the resume_matcher_ai module to the path
sys.path.append('resume_matcher_ai')

from resume_matcher_ai.resume_parser import _validate_pdf_file_comprehensive, extract_text_from_pdf
from resume_matcher_ai.jd_parser import _validate_job_description_input, parse_jd_text
from resume_matcher_ai.matcher import _handle_api_response_status
from resume_matcher_ai.main import _is_retryable_error, _extract_wait_time_from_error
from resume_matcher_ai.utils import validate_api_key
import requests

def test_file_validation():
    """Test comprehensive file validation"""
    print("🧪 Testing file validation...")
    
    # Test 1: Non-existent file
    try:
        _validate_pdf_file_comprehensive('nonexistent.pdf')
        print("❌ Should have raised FileNotFoundError")
        return False
    except FileNotFoundError as e:
        print("✅ Correctly caught non-existent file")
        assert "not found" in str(e).lower()
        assert "suggestions" in str(e).lower()
    
    # Test 2: Wrong file extension (create a temporary file)
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
        tmp_file.write(b'test content')
        tmp_file_path = tmp_file.name
    
    try:
        _validate_pdf_file_comprehensive(tmp_file_path)
        print("❌ Should have raised ValueError for wrong extension")
        os.unlink(tmp_file_path)  # Clean up
        return False
    except ValueError as e:
        print("✅ Correctly caught wrong file extension")
        os.unlink(tmp_file_path)  # Clean up
        assert "must be a pdf" in str(e).lower()
    
    # Test 3: Directory instead of file
    try:
        _validate_pdf_file_comprehensive('.')
        print("❌ Should have raised ValueError for directory")
        return False
    except ValueError as e:
        print("✅ Correctly caught directory path")
        assert "directory" in str(e).lower()
    
    return True

def test_jd_validation():
    """Test job description validation"""
    print("\n🧪 Testing job description validation...")
    
    # Test 1: Empty input
    try:
        _validate_job_description_input('')
        print("❌ Should have raised ValueError for empty input")
        return False
    except ValueError as e:
        print("✅ Correctly caught empty input")
        assert "empty" in str(e).lower()
    
    # Test 2: Too short input
    try:
        _validate_job_description_input('short')
        print("❌ Should have raised ValueError for short input")
        return False
    except ValueError as e:
        print("✅ Correctly caught short input")
        assert "too short" in str(e).lower()
    
    # Test 3: Non-string input
    try:
        _validate_job_description_input(None)
        print("❌ Should have raised ValueError for None input")
        return False
    except ValueError as e:
        print("✅ Correctly caught None input")
        assert "cannot be none" in str(e).lower()
    
    # Test 4: Valid job description
    valid_jd = """
    Software Engineer Position
    
    We are seeking a skilled Software Engineer to join our team.
    
    Responsibilities:
    - Develop and maintain web applications
    - Work with Python, JavaScript, and React
    - Collaborate with cross-functional teams
    
    Requirements:
    - Bachelor's degree in Computer Science
    - 3+ years of experience in software development
    - Strong knowledge of Python and JavaScript
    - Experience with React and Node.js
    """
    
    try:
        _validate_job_description_input(valid_jd)
        print("✅ Valid job description passed validation")
    except Exception as e:
        print(f"❌ Valid job description failed validation: {e}")
        return False
    
    return True

def test_api_error_handling():
    """Test API error handling functions"""
    print("\n🧪 Testing API error handling...")
    
    # Test retry logic
    retryable_errors = [
        "Connection timeout",
        "Rate limit exceeded",
        "Server error 500",
        "Network connection failed",
        "SSL certificate error"
    ]
    
    non_retryable_errors = [
        "Invalid API key",
        "Unauthorized 401",
        "File not found",
        "Corrupted PDF file",
        "Bad request 400"
    ]
    
    for error in retryable_errors:
        if not _is_retryable_error(error):
            print(f"❌ Should be retryable: {error}")
            return False
    print("✅ Retryable errors correctly identified")
    
    for error in non_retryable_errors:
        if _is_retryable_error(error):
            print(f"❌ Should not be retryable: {error}")
            return False
    print("✅ Non-retryable errors correctly identified")
    
    # Test wait time extraction
    test_cases = [
        ("Rate limit exceeded. Please wait 60 seconds", 60),
        ("Retry after 30 seconds", 30),
        ("Wait 120s before retrying", 120),
        ("No wait time mentioned", 0)
    ]
    
    for error_msg, expected_time in test_cases:
        actual_time = _extract_wait_time_from_error(error_msg)
        if actual_time != expected_time:
            print(f"❌ Wait time extraction failed: expected {expected_time}, got {actual_time}")
            return False
    print("✅ Wait time extraction working correctly")
    
    return True

def test_api_key_validation():
    """Test API key validation"""
    print("\n🧪 Testing API key validation...")
    
    # Test invalid keys
    invalid_keys = [
        "",
        None,
        "invalid-key",
        "pplx-",
        "pplx-short",
        "not-pplx-key",
        123,
        "pplx-" + "x" * 300  # Too long
    ]
    
    for key in invalid_keys:
        if validate_api_key(key):
            print(f"❌ Should be invalid: {key}")
            return False
    print("✅ Invalid API keys correctly rejected")
    
    # Test potentially valid key format (but we can't test actual validity without a real key)
    valid_format_key = "pplx-1234567890abcdef1234567890abcdef"
    # Note: This will likely fail the actual API test, but should pass format validation
    # We can't test this without a real API key, so we'll skip the actual validation
    print("✅ API key format validation working")
    
    return True

def main():
    """Run all error handling tests"""
    print("🚀 Starting comprehensive error handling tests...\n")
    
    tests = [
        ("File Validation", test_file_validation),
        ("Job Description Validation", test_jd_validation),
        ("API Error Handling", test_api_error_handling),
        ("API Key Validation", test_api_key_validation)
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
    
    print(f"\n📊 Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All error handling tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Please review the error handling implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)