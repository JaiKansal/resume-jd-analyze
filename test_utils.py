#!/usr/bin/env python3
"""
Test script for utils.py functions
"""
import os
import sys
from unittest.mock import Mock, patch

# Add the resume_matcher_ai directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resume_matcher_ai'))

from resume_matcher_ai.utils import (
    validate_api_key,
    load_config,
    format_prompt,
    handle_rate_limits,
    get_match_category,
    _clean_text_for_prompt
)

def test_validate_api_key():
    """Test API key validation"""
    print("Testing API key validation...")
    
    # Test invalid keys
    assert not validate_api_key("")
    assert not validate_api_key(None)
    assert not validate_api_key("invalid-key")
    assert not validate_api_key("short")
    print("✓ Invalid key rejection works")
    
    # Test valid format but mock the API call
    with patch('resume_matcher_ai.utils.requests.post') as mock_post:
        # Mock successful validation
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        assert validate_api_key("pplx-valid-key-for-testing-purposes-12345")
        print("✓ Valid key acceptance works")
        
        # Mock invalid key response
        mock_response.status_code = 401
        assert not validate_api_key("pplx-invalid-key-for-testing-purposes-12345")
        print("✓ API validation works")

def test_load_config():
    """Test configuration loading"""
    print("\nTesting configuration loading...")
    
    # Set test environment variables
    os.environ['PERPLEXITY_API_KEY'] = 'test-key'
    os.environ['MAX_TOKENS'] = '5000'
    
    config = load_config()
    
    assert config['perplexity_api_key'] == 'test-key'
    assert config['max_tokens'] == '5000'
    assert 'api_base_url' in config
    assert 'timeout' in config
    
    print("✓ Configuration loading works")
    
    # Clean up
    del os.environ['PERPLEXITY_API_KEY']
    del os.environ['MAX_TOKENS']

def test_format_prompt():
    """Test prompt formatting"""
    print("\nTesting prompt formatting...")
    
    resume_text = "John Doe, Software Engineer"
    jd_text = "Looking for experienced developer"
    
    prompt = format_prompt(resume_text, jd_text)
    
    assert "RESUME:" in prompt
    assert "JOB DESCRIPTION:" in prompt
    assert resume_text in prompt
    assert jd_text in prompt
    assert "JSON format" in prompt
    assert "compatibility_score" in prompt
    
    print("✓ Prompt formatting works")
    
    # Test with very long text (should be truncated)
    long_resume = "A" * 10000
    long_jd = "B" * 5000
    
    long_prompt = format_prompt(long_resume, long_jd)
    assert len(long_prompt) < 15000  # Should be truncated
    assert "..." in long_prompt  # Should have truncation indicator
    
    print("✓ Text truncation works")

def test_handle_rate_limits():
    """Test rate limit handling"""
    print("\nTesting rate limit handling...")
    
    # Test rate limit response
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.headers = {'Retry-After': '30'}
    
    try:
        handle_rate_limits(mock_response)
        assert False, "Should have raised an exception"
    except Exception as e:
        assert "Rate limit exceeded" in str(e)
        assert "30 seconds" in str(e)
    
    print("✓ Rate limit handling works")
    
    # Test unauthorized response
    mock_response.status_code = 401
    try:
        handle_rate_limits(mock_response)
        assert False, "Should have raised an exception"
    except Exception as e:
        assert "Invalid API key" in str(e)
    
    print("✓ Unauthorized handling works")
    
    # Test server error
    mock_response.status_code = 500
    try:
        handle_rate_limits(mock_response)
        assert False, "Should have raised an exception"
    except Exception as e:
        assert "server error" in str(e)
    
    print("✓ Server error handling works")
    
    # Test success (should not raise)
    mock_response.status_code = 200
    handle_rate_limits(mock_response)  # Should not raise
    print("✓ Success response handling works")

def test_get_match_category():
    """Test match category determination"""
    print("\nTesting match category determination...")
    
    assert get_match_category(25) == "Poor Match"
    assert get_match_category(50) == "Moderate Match"
    assert get_match_category(75) == "Strong Match"
    assert get_match_category(0) == "Poor Match"
    assert get_match_category(100) == "Strong Match"
    
    print("✓ Match category determination works")

def test_clean_text_for_prompt():
    """Test text cleaning for prompts"""
    print("\nTesting text cleaning...")
    
    dirty_text = "  This   has    excessive   whitespace  \n\n\n  and weird chars @@@ !!! "
    clean_text = _clean_text_for_prompt(dirty_text)
    
    assert "   " not in clean_text  # No excessive whitespace
    assert clean_text.strip() == clean_text  # No leading/trailing whitespace
    assert len(clean_text) < len(dirty_text)  # Should be shorter
    
    print("✓ Text cleaning works")
    
    # Test empty text
    assert _clean_text_for_prompt("") == ""
    assert _clean_text_for_prompt(None) == ""
    
    print("✓ Empty text handling works")

def main():
    """Run all utility tests"""
    print("Running utility function tests...\n")
    
    try:
        test_validate_api_key()
        test_load_config()
        test_format_prompt()
        test_handle_rate_limits()
        test_get_match_category()
        test_clean_text_for_prompt()
        
        print("\n✅ All utility tests passed!")
        
    except Exception as e:
        print(f"\n❌ Utility test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()