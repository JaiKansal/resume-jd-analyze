#!/usr/bin/env python3
"""
Quick analysis script - just edit the variables below
"""
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
from resume_matcher_ai.jd_parser import parse_jd_text

# ============================================================================
# EDIT THESE VARIABLES:
# ============================================================================

# Path to your resume PDF
RESUME_PATH = "path/to/your/resume.pdf"  # Change this!

# Your job description (paste between the triple quotes)
JOB_DESCRIPTION = """
Occasionally contribute to backend APIs and microservices
Help with algorithmically driven features

[PASTE YOUR FULL JOB DESCRIPTION HERE]

Requirements:
- Experience with backend development
- Knowledge of microservices architecture
- Algorithm development experience
- etc...
"""

# ============================================================================
# NO NEED TO EDIT BELOW THIS LINE
# ============================================================================

def main():
    try:
        print("🔄 Analyzing resume compatibility...")
        
        # Process the analysis
        resume_text = extract_text_from_pdf(RESUME_PATH)
        cleaned_resume = clean_resume_text(resume_text)
        jd_data = parse_jd_text(JOB_DESCRIPTION)
        result = analyze_match(cleaned_resume, jd_data.__dict__)
        
        # Display results
        print(f"\n🎯 COMPATIBILITY SCORE: {result.score}%")
        print(f"📊 CATEGORY: {result.match_category}")
        
        print(f"\n✅ MATCHING SKILLS ({len(result.matching_skills)}):")
        for skill in result.matching_skills[:10]:
            print(f"   • {skill}")
        
        total_gaps = sum(len(skills) for skills in result.skill_gaps.values())
        if total_gaps > 0:
            print(f"\n❌ MISSING SKILLS:")
            for category in ["Critical", "Important", "Nice-to-have"]:
                skills = result.skill_gaps.get(category, [])
                if skills:
                    print(f"   {category}: {', '.join(skills)}")
        
        print(f"\n💡 TOP RECOMMENDATIONS:")
        for i, suggestion in enumerate(result.suggestions[:3], 1):
            print(f"   {i}. {suggestion}")
        
        print(f"\n⏱️  Completed in {result.processing_time:.2f} seconds")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure to:")
        print("   1. Update RESUME_PATH with your actual PDF path")
        print("   2. Paste your job description in JOB_DESCRIPTION")
        print("   3. Set your PERPLEXITY_API_KEY environment variable")

if __name__ == "__main__":
    main()