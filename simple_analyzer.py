#!/usr/bin/env python3
"""
Simple Resume Analyzer - Handles large job description input better
"""
import os
import sys
from resume_matcher_ai.matcher import analyze_match
from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
from resume_matcher_ai.jd_parser import parse_jd_text

def get_resume_path():
    """Get resume file path with validation"""
    while True:
        resume_path = input("\n📄 Enter path to your resume PDF: ").strip().strip('"\'')
        
        if not resume_path:
            print("❌ Please enter a file path")
            continue
            
        if not os.path.exists(resume_path):
            print(f"❌ File not found: {resume_path}")
            continue
            
        if not resume_path.lower().endswith('.pdf'):
            print("❌ Please provide a PDF file")
            continue
            
        return resume_path

def get_job_description():
    """Get job description with better handling for large text"""
    print("\n📋 Job Description Input Options:")
    print("1. Type/paste directly (for short descriptions)")
    print("2. Read from file (recommended for long descriptions)")
    
    choice = input("\nChoose option (1 or 2): ").strip()
    
    if choice == "2":
        # Read from file
        file_path = input("Enter path to job description text file: ").strip().strip('"\'')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return get_job_description()  # Try again
    
    else:
        # Direct input with better handling
        print("\n📝 Paste your job description below.")
        print("💡 Tip: If you have issues, save to a file and use option 2")
        print("Press Ctrl+D (Mac/Linux) or Ctrl+Z (Windows) when done:")
        print("-" * 50)
        
        lines = []
        try:
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print("\n❌ Input cancelled")
                    return get_job_description()  # Try again
        except Exception as e:
            print(f"❌ Input error: {e}")
            return get_job_description()  # Try again
        
        return '\n'.join(lines).strip()

def display_results(result):
    """Display analysis results in a clean format"""
    print("\n" + "=" * 70)
    print("🎯 ANALYSIS RESULTS")
    print("=" * 70)
    
    # Score and category
    print(f"\n📊 COMPATIBILITY SCORE: {result.score}%")
    print(f"🏷️  MATCH CATEGORY: {result.match_category}")
    
    # Matching skills
    if result.matching_skills:
        print(f"\n✅ MATCHING SKILLS ({len(result.matching_skills)}):")
        for i, skill in enumerate(result.matching_skills[:10], 1):  # Show top 10
            print(f"   {i}. {skill}")
        if len(result.matching_skills) > 10:
            print(f"   ... and {len(result.matching_skills) - 10} more")
    
    # Skill gaps
    total_gaps = sum(len(skills) for skills in result.skill_gaps.values())
    if total_gaps > 0:
        print(f"\n❌ SKILL GAPS ({total_gaps} total):")
        
        for category, icon in [("Critical", "🔴"), ("Important", "🟡"), ("Nice-to-have", "🟢")]:
            skills = result.skill_gaps.get(category, [])
            if skills:
                print(f"   {icon} {category}: {', '.join(skills[:5])}")
                if len(skills) > 5:
                    print(f"      ... and {len(skills) - 5} more")
    else:
        print(f"\n🎉 NO SKILL GAPS! All key skills are present.")
    
    # Top suggestions
    if result.suggestions:
        print(f"\n💡 TOP RECOMMENDATIONS:")
        for i, suggestion in enumerate(result.suggestions[:3], 1):  # Show top 3
            print(f"   {i}. {suggestion}")
    
    print(f"\n⏱️  Processing time: {result.processing_time:.2f} seconds")
    print("=" * 70)

def main():
    """Main application"""
    print("🚀 Resume + Job Description Analyzer")
    print("=" * 50)
    
    try:
        # Get inputs
        resume_path = get_resume_path()
        job_description = get_job_description()
        
        if not job_description.strip():
            print("❌ Job description cannot be empty")
            return
        
        print(f"\n🔄 Analyzing compatibility...")
        print("⏳ This may take up to 30 seconds...")
        
        # Process analysis
        resume_text = extract_text_from_pdf(resume_path)
        cleaned_resume = clean_resume_text(resume_text)
        jd_data = parse_jd_text(job_description)
        result = analyze_match(cleaned_resume, jd_data.__dict__)
        
        # Display results
        display_results(result)
        
        # Ask if user wants to analyze another
        while True:
            again = input("\n🔄 Analyze another resume/job? (y/n): ").strip().lower()
            if again in ['y', 'yes']:
                print("\n" + "="*50)
                main()  # Restart
                break
            elif again in ['n', 'no']:
                print("\n👋 Thank you for using Resume Analyzer!")
                break
            else:
                print("Please enter 'y' or 'n'")
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Tips:")
        print("   • Make sure your PDF is readable (not scanned)")
        print("   • Check that your API key is set correctly")
        print("   • Try with a shorter job description")

if __name__ == "__main__":
    main()