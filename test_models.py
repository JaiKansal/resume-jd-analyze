#!/usr/bin/env python3
"""
Test different model names
"""
import os
import requests
import json

def test_models():
    """Test different model names to see which works"""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        print("❌ API key not set")
        return
    
    # Different model names to try
    models_to_test = [
        'llama-3.1-sonar-small-128k-online',
        'llama-3.1-sonar-large-128k-online',
        'llama-3-sonar-small-32k-online',
        'llama-3-sonar-large-32k-online',
        'mixtral-8x7b-instruct',
        'llama-3.1-8b-instruct',
        'llama-3.1-70b-instruct'
    ]
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'User-Agent': 'Resume-Matcher-AI/1.0'
    }
    
    test_message = "Hello, respond with just 'OK'"
    
    for model in models_to_test:
        print(f"🧪 Testing model: {model}")
        
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': test_message}],
            'max_tokens': 10,
            'temperature': 0.1
        }
        
        try:
            response = requests.post(
                'https://api.perplexity.ai/chat/completions',
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"   ✅ {model} works!")
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"   📝 Response: {content}")
                return model  # Return the working model
            else:
                print(f"   ❌ {model} failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {model} error: {e}")
    
    print("❌ No working models found!")
    return None

if __name__ == "__main__":
    working_model = test_models()
    if working_model:
        print(f"\n🎉 Use this model: {working_model}")
    else:
        print("\n❌ No models work - check your API key and account status")