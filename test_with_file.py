#!/usr/bin/env python3
"""
Test script using job_description.txt file
"""
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
from resume_matcher_ai.jd_parser import parse_jd_text

def main():
    # Get resume path from user
    resume_path = input("📄 Enter path to your resume PDF: ").strip().strip('"\'')
    
    try:
        print("📋 Reading job description from job_description.txt...")
        
        # Read job description from file
        with open('job_description.txt', 'r', encoding='utf-8') as f:
            job_description = f.read().strip()
        
        if not job_description:
            print("❌ job_description.txt is empty!")
            return
        
        print(f"✅ Job description loaded ({len(job_description)} characters)")
        print("🔄 Analyzing compatibility...")
        
        # Process the analysis
        resume_text = extract_text_from_pdf(resume_path)
        cleaned_resume = clean_resume_text(resume_text)
        jd_data = parse_jd_text(job_description)
        result = analyze_match(cleaned_resume, jd_data.__dict__)
        
        # Display results
        print("\n" + "=" * 60)
        print("🎯 ANALYSIS RESULTS")
        print("=" * 60)
        
        print(f"\n📊 COMPATIBILITY SCORE: {result.score}%")
        print(f"🏷️  MATCH CATEGORY: {result.match_category}")
        
        if result.matching_skills:
            print(f"\n✅ MATCHING SKILLS ({len(result.matching_skills)}):")
            for i, skill in enumerate(result.matching_skills[:8], 1):
                print(f"   {i}. {skill}")
            if len(result.matching_skills) > 8:
                print(f"   ... and {len(result.matching_skills) - 8} more")
        
        # Show skill gaps
        total_gaps = sum(len(skills) for skills in result.skill_gaps.values())
        if total_gaps > 0:
            print(f"\n❌ SKILL GAPS TO ADDRESS:")
            for category, icon in [("Critical", "🔴"), ("Important", "🟡"), ("Nice-to-have", "🟢")]:
                skills = result.skill_gaps.get(category, [])
                if skills:
                    print(f"   {icon} {category}: {', '.join(skills[:3])}")
                    if len(skills) > 3:
                        print(f"      ... and {len(skills) - 3} more")
        else:
            print(f"\n🎉 EXCELLENT! All key skills are present in your resume!")
        
        # Show top suggestions
        if result.suggestions:
            print(f"\n💡 TOP RECOMMENDATIONS:")
            for i, suggestion in enumerate(result.suggestions[:3], 1):
                # Truncate long suggestions for readability
                short_suggestion = suggestion[:100] + "..." if len(suggestion) > 100 else suggestion
                print(f"   {i}. {short_suggestion}")
        
        print(f"\n⏱️  Analysis completed in {result.processing_time:.2f} seconds")
        print("=" * 60)
        
        # Show next steps based on score
        if result.score >= 70:
            print("\n🚀 NEXT STEPS: You're ready to apply! Focus on interview prep.")
        elif result.score >= 50:
            print("\n🎯 NEXT STEPS: Good foundation. Implement top 2-3 recommendations.")
        else:
            print("\n🔧 NEXT STEPS: Significant improvements needed. Focus on critical gaps first.")
        
    except FileNotFoundError:
        print("❌ job_description.txt file not found!")
        print("💡 Make sure the file is in the same directory as this script")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   • Check that your resume PDF is readable")
        print("   • Verify your PERPLEXITY_API_KEY is set")
        print("   • Make sure job_description.txt contains valid text")

if __name__ == "__main__":
    main()