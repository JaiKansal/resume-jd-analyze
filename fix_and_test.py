#!/usr/bin/env python3
"""
Fix and test script
"""
import os
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
from resume_matcher_ai.jd_parser import parse_jd_text

def check_api_key():
    """Check if API key is properly configured"""
    api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        print("❌ PERPLEXITY_API_KEY environment variable is not set!")
        print("\n💡 Fix this by running:")
        print("export PERPLEXITY_API_KEY='pplx-your-actual-key-here'")
        return False
    
    if not api_key.startswith('pplx-'):
        print(f"❌ API key format looks wrong: {api_key[:10]}...")
        print("💡 Perplexity API keys should start with 'pplx-'")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    return True

def clean_job_description_file():
    """Clean the job description file"""
    file_path = "/Users/jai/Desktop/Resume + JD/job_description.txt"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove the placeholder text
        lines = content.split('\n')
        cleaned_lines = []
        skip_until_job_title = True
        
        for line in lines:
            if skip_until_job_title:
                if line.strip().startswith('Job Title:') or line.strip().startswith('Junior Full Stack Developer'):
                    skip_until_job_title = False
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
        
        cleaned_content = '\n'.join(cleaned_lines).strip()
        
        # Save cleaned version
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"✅ Cleaned job description file")
        print(f"📊 New size: {len(cleaned_content)} characters")
        print(f"📝 Starts with: {cleaned_content[:100]}...")
        
        return cleaned_content
        
    except Exception as e:
        print(f"❌ Error cleaning file: {e}")
        return None

def test_analysis():
    """Test the analysis with cleaned data"""
    resume_path = "'/Users/jai/Downloads/Jai resume updated 8 May 2025.pdf'"
    resume_path = resume_path.strip("'\"")  # Remove quotes
    
    try:
        # Read cleaned job description
        with open("/Users/jai/Desktop/Resume + JD/job_description.txt", 'r', encoding='utf-8') as f:
            job_description = f.read().strip()
        
        if not job_description:
            print("❌ Job description is empty after cleaning!")
            return
        
        print("🔄 Testing analysis with cleaned data...")
        
        # Process the analysis
        resume_text = extract_text_from_pdf(resume_path)
        cleaned_resume = clean_resume_text(resume_text)
        jd_data = parse_jd_text(job_description)
        result = analyze_match(cleaned_resume, jd_data.__dict__)
        
        # Display results
        print(f"\n🎯 RESULTS:")
        print(f"📊 Score: {result.score}%")
        print(f"🏷️  Category: {result.match_category}")
        
        if result.score > 0:
            print("🎉 SUCCESS! Analysis is working!")
            
            if result.matching_skills:
                print(f"\n✅ Found {len(result.matching_skills)} matching skills:")
                for skill in result.matching_skills[:5]:
                    print(f"   • {skill}")
            
            if result.suggestions:
                print(f"\n💡 Top suggestion:")
                print(f"   {result.suggestions[0]}")
        else:
            print("❌ Still getting 0% - there may be other issues")
            
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        
        if "api key" in str(e).lower():
            print("💡 This is an API key issue")
        elif "400" in str(e):
            print("💡 This is a bad request - likely data formatting issue")
        elif "rate limit" in str(e).lower():
            print("💡 Rate limit hit - wait a minute and try again")

def main():
    print("🔧 FIXING AND TESTING RESUME ANALYZER")
    print("=" * 50)
    
    # Step 1: Check API key
    print("\n1️⃣  Checking API configuration...")
    if not check_api_key():
        return
    
    # Step 2: Clean job description
    print("\n2️⃣  Cleaning job description file...")
    if not clean_job_description_file():
        return
    
    # Step 3: Test analysis
    print("\n3️⃣  Testing analysis...")
    test_analysis()

if __name__ == "__main__":
    main()