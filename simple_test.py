#!/usr/bin/env python3
"""
Simple test with minimal job description
"""
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
from resume_matcher_ai.jd_parser import parse_jd_text

def test_with_simple_jd():
    # Simple, clean job description for testing
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
- Participate in code reviews
"""
    
    resume_path = input("📄 Enter path to your resume PDF: ").strip().strip('"\'')
    
    try:
        print("🔄 Testing with simple job description...")
        
        # Process the analysis
        resume_text = extract_text_from_pdf(resume_path)
        print(f"✅ Resume extracted: {len(resume_text)} characters")
        
        cleaned_resume = clean_resume_text(resume_text)
        print(f"✅ Resume cleaned: {len(cleaned_resume)} characters")
        
        jd_data = parse_jd_text(simple_jd)
        print(f"✅ Job description parsed: {jd_data.title}")
        
        result = analyze_match(cleaned_resume, jd_data.__dict__)
        print(f"✅ Analysis completed!")
        
        # Display results
        print(f"\n📊 SCORE: {result.score}%")
        print(f"🏷️  CATEGORY: {result.match_category}")
        
        if result.score > 0:
            print("🎉 SUCCESS! The system is working correctly.")
            print("The issue is likely with your job description file.")
        else:
            print("❌ Still getting 0% - there might be an API configuration issue.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # More specific error diagnosis
        if "api key" in str(e).lower():
            print("\n💡 API Key Issue:")
            print("   export PERPLEXITY_API_KEY='pplx-your-actual-key-here'")
        elif "400" in str(e):
            print("\n💡 Bad Request - likely due to:")
            print("   • Resume content too long or malformed")
            print("   • Invalid characters in text")
            print("   • API key format issues")
        elif "pdf" in str(e).lower():
            print("\n💡 PDF Issue:")
            print("   • Make sure PDF contains selectable text")
            print("   • Try a different PDF file")

if __name__ == "__main__":
    test_with_simple_jd()