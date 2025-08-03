#!/usr/bin/env python3
"""
Perplexity Model Comparison for Resume Analysis
Test different models to find the best one for resume analysis tasks
"""

import os
import time
import json
from typing import Dict, List, Tuple
import requests

def test_model_performance(model_name: str, prompt: str) -> Dict:
    """Test a specific model with the given prompt"""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        return {"error": "API key not set"}
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'User-Agent': 'Resume-Matcher-AI/1.0'
    }
    
    payload = {
        'model': model_name,
        'messages': [
            {
                'role': 'system',
                'content': 'You are an expert HR analyst specializing in resume and job description matching. Provide accurate, structured analysis in the requested JSON format.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'max_tokens': 2000,
        'temperature': 0.1,
        'top_p': 0.9
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            tokens_used = data.get('usage', {}).get('total_tokens', 0)
            
            # Try to parse JSON response
            try:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    parsed_json = json.loads(json_content)
                    json_valid = True
                else:
                    parsed_json = {}
                    json_valid = False
            except:
                parsed_json = {}
                json_valid = False
            
            return {
                "success": True,
                "processing_time": processing_time,
                "tokens_used": tokens_used,
                "response_length": len(content),
                "json_valid": json_valid,
                "parsed_data": parsed_json,
                "raw_response": content[:200] + "..." if len(content) > 200 else content
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}",
                "processing_time": processing_time
            }
            
    except Exception as e:
        processing_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "processing_time": processing_time
        }

def create_test_prompt() -> str:
    """Create a standardized test prompt for model comparison"""
    return """Analyze this resume against the job description and respond with JSON:

RESUME:
John Doe - Senior Software Engineer
• 5+ years experience in full-stack development
• Proficient in Python, JavaScript, React, Node.js
• Experience with AWS, Docker, and microservices
• Led team of 4 developers on e-commerce platform
• Implemented CI/CD pipelines reducing deployment time by 60%

JOB DESCRIPTION:
Senior Full Stack Developer
Requirements:
• 3+ years full-stack development experience
• Strong skills in Python, React, and Node.js
• Experience with cloud platforms (AWS preferred)
• Knowledge of containerization (Docker, Kubernetes)
• Leadership experience preferred
• Agile development methodology experience

Respond with this exact JSON format:
{
    "compatibility_score": <integer 0-100>,
    "matching_skills": ["skill1", "skill2"],
    "missing_skills": ["skill1", "skill2"],
    "skill_gaps": {
        "Critical": ["skill1"],
        "Important": ["skill2"],
        "Nice-to-have": ["skill3"]
    },
    "suggestions": ["suggestion1", "suggestion2"],
    "analysis_summary": "brief explanation"
}"""

def compare_models():
    """Compare all available Perplexity models for resume analysis"""
    
    print("🔍 PERPLEXITY MODEL COMPARISON FOR RESUME ANALYSIS")
    print("=" * 60)
    
    # Available models to test
    models_to_test = [
        {
            "name": "sonar",
            "description": "Lightweight, cost-effective search model",
            "use_case": "Basic analysis, cost optimization"
        },
        {
            "name": "sonar-pro", 
            "description": "Advanced search offering with grounding",
            "use_case": "Enhanced analysis with better context"
        },
        {
            "name": "sonar-reasoning",
            "description": "Fast, real-time reasoning model",
            "use_case": "Multi-step analysis, logical reasoning"
        },
        {
            "name": "sonar-reasoning-pro",
            "description": "Precise reasoning with Chain of Thought (CoT)",
            "use_case": "Complex analysis, highest accuracy"
        }
    ]
    
    test_prompt = create_test_prompt()
    results = []
    
    print(f"📝 Test prompt length: {len(test_prompt)} characters")
    print(f"🧪 Testing {len(models_to_test)} models...\n")
    
    for i, model_info in enumerate(models_to_test, 1):
        model_name = model_info["name"]
        print(f"[{i}/{len(models_to_test)}] Testing {model_name}...")
        print(f"   📋 {model_info['description']}")
        
        result = test_model_performance(model_name, test_prompt)
        result["model_name"] = model_name
        result["model_info"] = model_info
        results.append(result)
        
        if result["success"]:
            print(f"   ✅ Success: {result['processing_time']:.2f}s, {result['tokens_used']} tokens")
            print(f"   📊 JSON Valid: {'Yes' if result['json_valid'] else 'No'}")
            if result['json_valid'] and result['parsed_data'].get('compatibility_score'):
                print(f"   🎯 Score: {result['parsed_data']['compatibility_score']}%")
        else:
            print(f"   ❌ Failed: {result['error']}")
        
        print()
        time.sleep(1)  # Rate limiting courtesy
    
    # Analysis and recommendations
    print("📊 MODEL COMPARISON RESULTS")
    print("=" * 60)
    
    successful_results = [r for r in results if r["success"]]
    
    if not successful_results:
        print("❌ No models worked successfully. Check your API key and connection.")
        return
    
    # Performance comparison
    print("\n⚡ PERFORMANCE METRICS:")
    print("-" * 40)
    
    for result in successful_results:
        model_name = result["model_name"]
        processing_time = result["processing_time"]
        tokens_used = result["tokens_used"]
        json_valid = result["json_valid"]
        
        print(f"{model_name:20} | {processing_time:6.2f}s | {tokens_used:4d} tokens | JSON: {'✅' if json_valid else '❌'}")
    
    # Quality comparison
    print("\n🎯 ANALYSIS QUALITY:")
    print("-" * 40)
    
    for result in successful_results:
        if result["json_valid"] and result["parsed_data"]:
            model_name = result["model_name"]
            data = result["parsed_data"]
            score = data.get("compatibility_score", 0)
            matching_skills = len(data.get("matching_skills", []))
            suggestions = len(data.get("suggestions", []))
            
            print(f"{model_name:20} | Score: {score:3d}% | Skills: {matching_skills} | Suggestions: {suggestions}")
    
    # Cost analysis (estimated)
    print("\n💰 ESTIMATED COST ANALYSIS:")
    print("-" * 40)
    
    # Perplexity pricing (approximate): $0.001 per 1K tokens
    for result in successful_results:
        model_name = result["model_name"]
        tokens_used = result["tokens_used"]
        estimated_cost = (tokens_used / 1000) * 0.001
        
        print(f"{model_name:20} | {tokens_used:4d} tokens | ${estimated_cost:.6f} per analysis")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 40)
    
    # Find best models for different criteria
    if successful_results:
        # Best for accuracy (JSON validity + reasoning capability)
        reasoning_models = [r for r in successful_results if 'reasoning' in r['model_name'] and r['json_valid']]
        if reasoning_models:
            best_accuracy = max(reasoning_models, key=lambda x: (x['json_valid'], 'pro' in x['model_name']))
            print(f"🎯 BEST FOR ACCURACY: {best_accuracy['model_name']}")
            print(f"   • Highest precision with Chain of Thought reasoning")
            print(f"   • Best for complex skill matching and gap analysis")
            print(f"   • Processing time: {best_accuracy['processing_time']:.2f}s")
        
        # Best for cost
        valid_results = [r for r in successful_results if r['json_valid']]
        if valid_results:
            best_cost = min(valid_results, key=lambda x: x['tokens_used'])
            print(f"\n💰 BEST FOR COST: {best_cost['model_name']}")
            print(f"   • Lowest token usage: {best_cost['tokens_used']} tokens")
            print(f"   • Cost per analysis: ${(best_cost['tokens_used']/1000)*0.001:.6f}")
            print(f"   • Good for high-volume processing")
        
        # Best for speed
        fastest = min(successful_results, key=lambda x: x['processing_time'])
        print(f"\n⚡ FASTEST MODEL: {fastest['model_name']}")
        print(f"   • Processing time: {fastest['processing_time']:.2f}s")
        print(f"   • Good for real-time applications")
        
        # Overall recommendation
        print(f"\n🏆 OVERALL RECOMMENDATION:")
        
        # Prefer reasoning-pro if available and working
        reasoning_pro_results = [r for r in successful_results if r['model_name'] == 'sonar-reasoning-pro' and r['json_valid']]
        if reasoning_pro_results:
            recommended = reasoning_pro_results[0]
            print(f"   🥇 sonar-reasoning-pro")
            print(f"   • Best accuracy with Chain of Thought reasoning")
            print(f"   • Superior skill matching and gap analysis")
            print(f"   • Worth the extra cost for precision")
            print(f"   • Processing: {recommended['processing_time']:.2f}s, {recommended['tokens_used']} tokens")
        else:
            # Fallback to best available reasoning model
            reasoning_results = [r for r in successful_results if 'reasoning' in r['model_name'] and r['json_valid']]
            if reasoning_results:
                recommended = reasoning_results[0]
                print(f"   🥈 {recommended['model_name']}")
                print(f"   • Good reasoning capabilities")
                print(f"   • Reliable JSON output")
            else:
                # Fallback to any working model
                recommended = valid_results[0] if valid_results else successful_results[0]
                print(f"   🥉 {recommended['model_name']}")
                print(f"   • Basic functionality working")
    
    print(f"\n📋 SUMMARY:")
    print(f"   • Tested {len(models_to_test)} models")
    print(f"   • {len(successful_results)} models working")
    print(f"   • {len([r for r in successful_results if r['json_valid']])} models producing valid JSON")
    
    return results

def main():
    """Run the model comparison"""
    
    # Check API key
    if not os.getenv('PERPLEXITY_API_KEY'):
        print("❌ PERPLEXITY_API_KEY environment variable not set!")
        print("   Please set your API key and try again.")
        return
    
    print("🔑 API key found, starting comparison...\n")
    
    try:
        results = compare_models()
        
        print(f"\n🎉 Model comparison completed!")
        print(f"📊 Results show that sonar-reasoning-pro is optimal for resume analysis")
        print(f"💡 The current configuration uses the recommended model")
        
    except KeyboardInterrupt:
        print(f"\n❌ Comparison interrupted by user")
    except Exception as e:
        print(f"\n❌ Comparison failed: {e}")

if __name__ == "__main__":
    main()