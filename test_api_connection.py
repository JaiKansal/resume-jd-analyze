#!/usr/bin/env python3
"""
Test API connection directly
"""
import os
import requests
import json

def test_api_key():
    """Test the API key with a minimal request"""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        print("❌ PERPLEXITY_API_KEY not set")
        return False
    
    print(f"🔑 Testing API key: {api_key[:10]}...{api_key[-4:]}")
    
    # Test with minimal request
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'User-Agent': 'Resume-Matcher-AI/1.0'
    }
    
    # Minimal test payload
    test_payload = {
        'model': 'sonar-reasoning-pro',
        'messages': [
            {
                'role': 'user',
                'content': 'Hello, this is a test message.'
            }
        ],
        'max_tokens': 10,
        'temperature': 0.1
    }
    
    try:
        print("🔄 Making test API request...")
        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers=headers,
            json=test_payload,
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API key is working!")
            try:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"📝 Response: {content}")
                return True
            except Exception as e:
                print(f"⚠️  Got 200 but couldn't parse response: {e}")
                return False
                
        elif response.status_code == 401:
            print("❌ API key is invalid (401 Unauthorized)")
            print("💡 Check your API key at https://www.perplexity.ai/settings/api")
            return False
            
        elif response.status_code == 403:
            print("❌ API key lacks permissions (403 Forbidden)")
            print("💡 Check your account status and billing")
            return False
            
        elif response.status_code == 429:
            print("❌ Rate limit exceeded (429)")
            print("💡 Wait a minute and try again")
            return False
            
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check your internet")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_with_resume_content():
    """Test with actual resume content to see what's causing the 400 error"""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        print("❌ API key not set")
        return
    
    # Get resume content
    resume_path = input("📄 Enter path to your resume PDF: ").strip().strip('"\'')
    
    try:
        from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
        from resume_matcher_ai.utils import estimate_token_usage
        
        print("📄 Extracting resume text...")
        resume_text = extract_text_from_pdf(resume_path)
        cleaned_resume = clean_resume_text(resume_text)
        
        print(f"📊 Resume stats:")
        print(f"   Raw length: {len(resume_text)} chars")
        print(f"   Cleaned length: {len(cleaned_resume)} chars")
        print(f"   Estimated tokens: {estimate_token_usage(cleaned_resume)}")
        
        # Test with very simple prompt
        simple_prompt = f"""Analyze this resume and give a score from 0-100:

{cleaned_resume[:1000]}...

Respond with just a number."""
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Resume-Matcher-AI/1.0'
        }
        
        payload = {
            'model': 'sonar',
            'messages': [
                {
                    'role': 'user',
                    'content': simple_prompt
                }
            ],
            'max_tokens': 50,
            'temperature': 0.1
        }
        
        print("🔄 Testing with resume content...")
        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Resume content works with API!")
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"📝 Response: {content}")
        else:
            print(f"❌ Failed with resume content")
            print(f"📝 Response: {response.text}")
            
            # Check if it's a content issue
            if response.status_code == 400:
                print("\n💡 This suggests the resume content has problematic characters")
                print("   Let's check for issues...")
                
                # Check for problematic characters
                problematic = []
                if '\x00' in cleaned_resume:
                    problematic.append("null bytes")
                if len([c for c in cleaned_resume if ord(c) > 127]) > len(cleaned_resume) * 0.1:
                    problematic.append("many non-ASCII characters")
                if len(cleaned_resume) > 20000:
                    problematic.append("very long text")
                
                if problematic:
                    print(f"   Found: {', '.join(problematic)}")
                else:
                    print("   No obvious content issues found")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🔍 API CONNECTION DIAGNOSTICS")
    print("=" * 40)
    
    # Test 1: Basic API key test
    print("\n1️⃣  Testing API key with minimal request...")
    if not test_api_key():
        print("\n❌ API key test failed. Fix your API key first.")
        return
    
    # Test 2: Test with resume content
    print("\n2️⃣  Testing with resume content...")
    test_with_resume_content()

if __name__ == "__main__":
    main()