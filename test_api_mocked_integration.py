#!/usr/bin/env python3
"""
Test the actual integration with detailed error reporting
"""
import os
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
from resume_matcher_ai.jd_parser import parse_jd_text

def test_step_by_step():
    """Test each step of the process with detailed logging"""
    
    print("🔍 STEP-BY-STEP INTEGRATION TEST")
    print("=" * 50)
    
    # Step 1: Check API key
    api_key = os.getenv('PERPLEXITY_API_KEY')
    print(f"1️⃣  API Key: {api_key[:10]}...{api_key[-4:] if api_key else 'NOT SET'}")
    
    if not api_key:
        print("❌ API key not found!")
        return
    
    # Step 2: Test resume processing
    resume_path = input("📄 Enter resume path: ").strip().strip('"\'')
    
    try:
        print("\n2️⃣  Testing resume processing...")
        resume_text = extract_text_from_pdf(resume_path)
        print(f"   ✅ Extracted {len(resume_text)} characters")
        
        cleaned_resume = clean_resume_text(resume_text)
        print(f"   ✅ Cleaned to {len(cleaned_resume)} characters")
        
        # Show a sample of the resume
        print(f"   📝 Sample: {cleaned_resume[:100]}...")
        
    except Exception as e:
        print(f"   ❌ Resume processing failed: {e}")
        return
    
    # Step 3: Test job description processing
    print("\n3️⃣  Testing job description processing...")
    simple_jd = """
Software Engineer Position

We are looking for a Software Engineer to join our team.

Requirements:
- Bachelor's degree in Computer Science
- 3+ years of programming experience
- Experience with Python or Java
- Knowledge of web development
- Strong problem-solving skills

Responsibilities:
- Develop software applications
- Work with development team
- Write clean, maintainable code
"""
    
    try:
        jd_data = parse_jd_text(simple_jd)
        print(f"   ✅ Parsed job: {jd_data.title}")
        print(f"   📊 Found {len(jd_data.requirements)} requirements")
        print(f"   🔧 Found {len(jd_data.technical_skills)} technical skills")
        
    except Exception as e:
        print(f"   ❌ JD processing failed: {e}")
        return
    
    # Step 4: Test API call directly
    print("\n4️⃣  Testing API call...")
    try:
        from resume_matcher_ai.matcher import call_perplexity_api
        from resume_matcher_ai.utils import format_prompt
        
        # Create a very simple prompt
        simple_prompt = f"""
Analyze this resume against this job and respond with JSON:

RESUME: {cleaned_resume[:500]}...

JOB: {simple_jd[:300]}...

Respond with:
{{"compatibility_score": 75, "matching_skills": ["Python"], "missing_skills": ["Java"], "suggestions": ["Add more experience"]}}
"""
        
        print(f"   📝 Prompt length: {len(simple_prompt)} characters")
        print("   🔄 Calling API...")
        
        api_response = call_perplexity_api(simple_prompt)
        print(f"   ✅ API responded with {len(api_response)} characters")
        print(f"   📝 Response preview: {api_response[:200]}...")
        
        # Step 5: Test full analysis
        print("\n5️⃣  Testing full analysis...")
        result = analyze_match(cleaned_resume, jd_data.__dict__)
        
        print(f"   📊 Score: {result.score}%")
        print(f"   🏷️  Category: {result.match_category}")
        print(f"   ✅ Matching skills: {len(result.matching_skills)}")
        print(f"   ❌ Missing skills: {len(result.missing_skills)}")
        print(f"   💡 Suggestions: {len(result.suggestions)}")
        
        if result.score > 0:
            print("\n🎉 SUCCESS! The integration is working!")
        else:
            print("\n❌ Still getting 0% score - there's an issue with the analysis logic")
            
    except Exception as e:
        print(f"   ❌ API call failed: {e}")
        
        # More detailed error analysis
        error_str = str(e).lower()
        if "400" in error_str:
            print("   💡 400 error suggests malformed request")
            print("   🔍 Possible causes:")
            print("      • Prompt too long")
            print("      • Invalid characters in text")
            print("      • Wrong model name")
        elif "401" in error_str:
            print("   💡 401 error suggests invalid API key")
        elif "429" in error_str:
            print("   💡 429 error suggests rate limiting")
        elif "timeout" in error_str:
            print("   💡 Timeout error suggests slow response")

if __name__ == "__main__":
    test_step_by_step()