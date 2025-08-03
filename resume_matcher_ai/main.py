"""
Main CLI application for Resume + Job Description Matcher
"""
import os
import sys
import time
from typing import Tuple, Optional
from .resume_parser import extract_text_from_pdf, clean_resume_text, validate_resume_content
from .jd_parser import parse_jd_text
from .matcher import analyze_match
from .utils import MatchResult, load_config, validate_api_key, setup_environment, display_setup_instructions, track_api_usage, get_usage_statistics


def main():
    """Primary application loop"""
    print("=" * 60)
    print("Resume + Job Description Matcher")
    print("=" * 60)
    print()
    
    # Check API configuration on startup
    if not _check_api_configuration():
        return
    
    print("Welcome! This tool analyzes the compatibility between resumes and job descriptions.")
    print("You'll receive a compatibility score, matching skills, gaps, and improvement suggestions.")
    print()
    
    while True:
        try:
            # Get user input
            resume_path, jd_text = get_user_input()
            
            if not resume_path or not jd_text:
                print("Exiting...")
                break
            
            # Process the analysis
            print("\nAnalyzing resume and job description...")
            print("This may take up to 30 seconds...")
            
            results = _process_analysis(resume_path, jd_text)
            
            # Display results
            display_results(results)
            
            # Ask if user wants to continue
            if not _ask_continue():
                break
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            handle_errors(e)
            if not _ask_continue():
                break
    
    print("\nThank you for using Resume + Job Description Matcher!")


def get_user_input() -> Tuple[Optional[str], Optional[str]]:
    """
    Collect resume file path and job description text from user
    
    Returns:
        Tuple of (resume_path, jd_text) or (None, None) if user wants to exit
    """
    print("-" * 40)
    print("INPUT COLLECTION")
    print("-" * 40)
    
    # Get resume file path
    resume_path = _get_resume_file_path()
    if not resume_path:
        return None, None
    
    # Get job description text
    jd_text = _get_job_description_text()
    if not jd_text:
        return None, None
    
    return resume_path, jd_text


def _get_resume_file_path() -> Optional[str]:
    """Get and validate resume file path from user with enhanced error handling"""
    max_attempts = 5
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n1. Resume File (attempt {attempt}/{max_attempts}):")
        
        try:
            resume_path = input("Enter the path to your resume PDF file (or 'quit' to exit): ").strip()
            
            if resume_path.lower() in ['quit', 'exit', 'q']:
                return None
            
            if not resume_path:
                print("❌ Please enter a file path.")
                if attempt >= max_attempts:
                    print("❌ Maximum attempts reached. Exiting...")
                    return None
                continue
            
            # Validate file path with comprehensive error handling
            validation_result = _validate_resume_file(resume_path)
            if validation_result is True:
                print(f"✅ Resume file validated: {resume_path}")
                return resume_path
            else:
                print(f"❌ {validation_result}")
                
                # Provide helpful suggestions based on the error
                if "not found" in validation_result.lower():
                    print("\n💡 Suggestions:")
                    print("   • Check if the file path is correct")
                    print("   • Use absolute path (e.g., /Users/yourname/Documents/resume.pdf)")
                    print("   • Drag and drop the file into terminal to get the correct path")
                elif "permission" in validation_result.lower():
                    print("\n💡 Suggestions:")
                    print("   • Check file permissions")
                    print("   • Try copying the file to your home directory")
                elif "corrupted" in validation_result.lower() or "invalid" in validation_result.lower():
                    print("\n💡 Suggestions:")
                    print("   • Try re-saving your resume as a new PDF")
                    print("   • Ensure the PDF is not password-protected")
                    print("   • Try a different PDF viewer to verify the file works")
                
                if attempt >= max_attempts:
                    print(f"\n❌ Maximum attempts ({max_attempts}) reached.")
                    print("Please check your file and try running the application again.")
                    return None
                
                print("Please try again with a valid PDF file.")
                
        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user.")
            return None
        except EOFError:
            print("\n\n❌ Input stream ended unexpectedly.")
            return None
        except Exception as e:
            print(f"\n❌ Unexpected error while getting file path: {str(e)}")
            if attempt >= max_attempts:
                print("❌ Maximum attempts reached. Exiting...")
                return None
            print("Please try again.")
    
    return None


def _get_job_description_text() -> Optional[str]:
    """Get job description text from user with enhanced validation and error handling"""
    max_attempts = 3
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n2. Job Description (attempt {attempt}/{max_attempts}):")
        print("Please paste the job description text below.")
        print("You can paste multiple lines. When finished, press Enter on an empty line.")
        print("(or type 'quit' to exit)")
        print()
        
        lines = []
        try:
            while True:
                try:
                    line = input()
                    if line.strip().lower() in ['quit', 'exit', 'q']:
                        return None
                    if not line.strip() and lines:  # Empty line after some content
                        break
                    lines.append(line)
                except EOFError:
                    break
            
            jd_text = '\n'.join(lines).strip()
            
            # Comprehensive validation using the jd_parser validation
            try:
                from .jd_parser import _validate_job_description_input
                _validate_job_description_input(jd_text)
                
                # If validation passes, return the text
                print(f"✅ Job description received and validated ({len(jd_text)} characters)")
                return jd_text
                
            except (ValueError, TypeError) as e:
                print(f"❌ {str(e)}")
                
                # Provide helpful suggestions based on the error
                error_msg = str(e).lower()
                if "empty" in error_msg or "short" in error_msg:
                    print("\n💡 Suggestions:")
                    print("   • Copy the complete job posting from the company website")
                    print("   • Include job title, responsibilities, requirements, and qualifications")
                    print("   • Ensure you paste the full text, not just a summary")
                elif "invalid content" in error_msg or "doesn't appear to be" in error_msg:
                    print("\n💡 Suggestions:")
                    print("   • Make sure you're pasting a real job description")
                    print("   • Avoid pasting URLs, email addresses, or partial content")
                    print("   • Include sections like requirements, responsibilities, qualifications")
                elif "too long" in error_msg:
                    print("\n💡 Suggestions:")
                    print("   • Try pasting just the core job description without company info")
                    print("   • Focus on the role requirements and responsibilities")
                
                if attempt >= max_attempts:
                    print(f"\n❌ Maximum attempts ({max_attempts}) reached.")
                    print("Please check your job description and try running the application again.")
                    return None
                
                print("\nPlease try again with a valid job description.")
                
        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user.")
            return None
        except Exception as e:
            print(f"\n❌ Unexpected error while getting job description: {str(e)}")
            if attempt >= max_attempts:
                print("❌ Maximum attempts reached. Exiting...")
                return None
            print("Please try again.")
    
    return None


def _validate_resume_file(file_path: str) -> str | bool:
    """
    Enhanced validation of resume file path and content with improved error messages
    
    Returns:
        True if valid, error message string if invalid
    """
    # Enhanced path validation
    if not file_path or not file_path.strip():
        return "File path cannot be empty"
    
    file_path = file_path.strip()
    
    # Check for common path issues
    if file_path.startswith('"') and file_path.endswith('"'):
        file_path = file_path[1:-1]  # Remove quotes
    
    if file_path.startswith("'") and file_path.endswith("'"):
        file_path = file_path[1:-1]  # Remove quotes
    
    # Check if file exists with enhanced error messages
    if not os.path.exists(file_path):
        # Provide more helpful error messages based on common issues
        if '~' in file_path and not file_path.startswith(os.path.expanduser('~')):
            expanded_path = os.path.expanduser(file_path)
            if os.path.exists(expanded_path):
                return f"File found at expanded path. Try: {expanded_path}"
            else:
                return f"File not found: {file_path} (expanded: {expanded_path})"
        
        # Check if it's a relative path issue
        abs_path = os.path.abspath(file_path)
        if os.path.exists(abs_path):
            return f"File found using absolute path. Try: {abs_path}"
        
        # Check if file exists in current directory
        basename = os.path.basename(file_path)
        if os.path.exists(basename):
            return f"File found in current directory. Try: {basename}"
        
        return f"File not found: {file_path}"
    
    # Enhanced file type validation
    if not file_path.lower().endswith('.pdf'):
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in ['.doc', '.docx']:
            return "Word documents are not supported. Please convert to PDF first."
        elif file_ext in ['.txt', '.rtf']:
            return "Text files are not supported. Please convert to PDF first."
        elif not file_ext:
            return "File has no extension. Please ensure it's a PDF file with .pdf extension."
        else:
            return f"Unsupported file type '{file_ext}'. Only PDF files (.pdf) are supported."
    
    # Enhanced permission checking
    if not os.access(file_path, os.R_OK):
        if os.path.exists(file_path):
            return "File exists but is not readable. Please check file permissions or try copying the file to a different location."
        else:
            return "File is not accessible. Please check the file path and permissions."
    
    # Enhanced file size validation
    try:
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return "File is empty (0 bytes). Please ensure the PDF contains content."
        
        # More granular size limits with helpful messages
        if file_size < 1024:  # Less than 1KB
            return f"File is very small ({file_size} bytes). This may not be a valid PDF resume."
        
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            size_mb = file_size / (1024 * 1024)
            return f"File is too large ({size_mb:.1f}MB, maximum 50MB). Please compress the PDF or use a smaller file."
        
        if file_size > 10 * 1024 * 1024:  # Warn for files over 10MB
            size_mb = file_size / (1024 * 1024)
            print(f"⚠️  Large file detected ({size_mb:.1f}MB). Processing may take longer.")
            
    except OSError as e:
        return f"Cannot access file information: {str(e)}"
    
    # Enhanced content validation with better error reporting
    try:
        print("📄 Extracting text from PDF...")
        text = extract_text_from_pdf(file_path)
        
        if not text or not text.strip():
            return "PDF appears to be empty or contains no extractable text. This could be due to:\n" \
                   "   • Scanned PDF without OCR\n" \
                   "   • Password-protected PDF\n" \
                   "   • Corrupted PDF file\n" \
                   "   • PDF with only images"
        
        print("🧹 Cleaning extracted text...")
        cleaned_text = clean_resume_text(text)
        
        if not cleaned_text or len(cleaned_text.strip()) < 50:
            return f"PDF contains insufficient text content ({len(cleaned_text)} characters). " \
                   f"Please ensure the PDF contains a readable resume with text content."
        
        print("✅ Validating resume content...")
        if not validate_resume_content(cleaned_text):
            return "PDF does not appear to contain valid resume content. Please ensure the file contains:\n" \
                   "   • Personal/contact information\n" \
                   "   • Work experience or education\n" \
                   "   • Skills or qualifications\n" \
                   "   • Readable text (not just images)"
        
        # Additional content quality checks
        word_count = len(cleaned_text.split())
        if word_count < 50:
            return f"Resume content is too brief ({word_count} words). Please ensure the PDF contains a complete resume."
        
        if word_count > 5000:
            print(f"⚠️  Very detailed resume detected ({word_count} words). Consider using a more concise version for better analysis.")
        
        return True
        
    except Exception as e:
        error_msg = str(e).lower()
        
        # Provide specific guidance based on error type
        if "password" in error_msg or "encrypted" in error_msg:
            return "PDF is password-protected or encrypted. Please provide an unprotected PDF file."
        elif "corrupted" in error_msg or "damaged" in error_msg:
            return "PDF file appears to be corrupted or damaged. Please try re-saving or re-creating the PDF."
        elif "permission" in error_msg:
            return "Permission denied while reading PDF. Please check file permissions or try copying to a different location."
        elif "memory" in error_msg:
            return "PDF is too complex to process. Please try compressing the PDF or using a simpler version."
        else:
            return f"Error reading PDF: {str(e)}\n" \
                   f"This could be due to:\n" \
                   f"   • Unsupported PDF format\n" \
                   f"   • Corrupted file\n" \
                   f"   • Complex PDF structure\n" \
                   f"   • Missing PDF processing dependencies"


def display_results(results: MatchResult) -> None:
    """
    Format and display analysis results with enhanced presentation
    Implements Requirements 6.3, 3.3, 4.4, 5.3
    
    Args:
        results: MatchResult object containing analysis data
    """
    # Enhanced header with visual separation
    print("\n" + "=" * 70)
    print("🎯 RESUME + JOB DESCRIPTION ANALYSIS RESULTS")
    print("=" * 70)
    
    # Display compatibility score and category with enhanced formatting
    _display_enhanced_score_section(results)
    
    # Display matching skills with improved categorization
    _display_enhanced_matching_skills_section(results)
    
    # Display skill gaps with better visual hierarchy
    _display_enhanced_skill_gaps_section(results)
    
    # Display suggestions with actionable formatting
    _display_enhanced_suggestions_section(results)
    
    # Display processing info with detailed indicators
    _display_enhanced_processing_info(results)
    
    # Add summary footer
    _display_results_summary(results)


def _display_enhanced_score_section(results: MatchResult) -> None:
    """Display compatibility score and match category with enhanced formatting"""
    print(f"\n┌─ 📊 COMPATIBILITY ANALYSIS")
    print(f"│")
    
    # Enhanced score display with visual indicators
    if results.score >= 70:
        score_indicator = "🟢"
        score_bar = "█" * 7 + "░" * 3  # 70% filled bar
        score_color = "STRONG"
    elif results.score >= 30:
        score_indicator = "🟡" 
        score_bar = "█" * 4 + "░" * 6  # 40% filled bar
        score_color = "MODERATE"
    else:
        score_indicator = "🔴"
        score_bar = "█" * 2 + "░" * 8  # 20% filled bar
        score_color = "NEEDS WORK"
    
    print(f"│ {score_indicator} MATCH SCORE: {results.score}% [{score_bar}] {score_color}")
    print(f"│ 🏷️  CATEGORY: {results.match_category}")
    print(f"│")
    
    # Enhanced interpretation with actionable context
    if results.score >= 70:
        print(f"│ ✨ EXCELLENT! Your resume demonstrates strong alignment with this role.")
        print(f"│    You meet most key requirements and show relevant experience.")
    elif results.score >= 50:
        print(f"│ 👍 GOOD POTENTIAL! You have solid foundation with room for optimization.")
        print(f"│    Focus on highlighting missing skills and strengthening key areas.")
    elif results.score >= 30:
        print(f"│ ⚠️  MODERATE FIT. Several important elements need attention.")
        print(f"│    Consider significant updates to better match job requirements.")
    else:
        print(f"│ 🔧 SIGNIFICANT GAPS identified. Major resume restructuring recommended.")
        print(f"│    Focus on skill development and strategic resume improvements.")
    
    print(f"└─────────────────────────────────────────────────────────────────")


def _display_enhanced_matching_skills_section(results: MatchResult) -> None:
    """Display skills that match between resume and job description with improved categorization"""
    print(f"\n┌─ ✅ MATCHING SKILLS ANALYSIS")
    print(f"│")
    
    if results.matching_skills:
        skill_count = len(results.matching_skills)
        print(f"│ 📈 FOUND {skill_count} MATCHING SKILL{'S' if skill_count != 1 else ''}")
        print(f"│")
        
        # Categorize skills for better presentation
        if skill_count <= 5:
            # Show all skills for smaller lists
            print(f"│ 🎯 Your Matching Skills:")
            for i, skill in enumerate(results.matching_skills, 1):
                print(f"│   {i}. {skill}")
        elif skill_count <= 10:
            # Show all with better formatting for medium lists
            print(f"│ 🎯 Your Matching Skills:")
            for i, skill in enumerate(results.matching_skills, 1):
                print(f"│   {i:2d}. {skill}")
        else:
            # Show top skills + summary for large lists
            print(f"│ 🎯 Top Matching Skills:")
            for i, skill in enumerate(results.matching_skills[:8], 1):
                print(f"│   {i}. {skill}")
            remaining = skill_count - 8
            print(f"│   ... plus {remaining} additional matching skills")
        
        print(f"│")
        
        # Enhanced summary with strength indicators
        if skill_count >= 8:
            print(f"│ 💪 EXCELLENT skill alignment! You demonstrate {skill_count} relevant competencies.")
            print(f"│    This strong foundation positions you well for this role.")
        elif skill_count >= 5:
            print(f"│ 👍 SOLID skill match! {skill_count} aligned competencies show good fit.")
            print(f"│    You meet many of the core requirements.")
        elif skill_count >= 3:
            print(f"│ ✓ MODERATE alignment with {skill_count} matching skills.")
            print(f"│    Focus on highlighting these strengths in your application.")
        else:
            print(f"│ ⚠️  LIMITED alignment with only {skill_count} matching skill{'s' if skill_count != 1 else ''}.")
            print(f"│    Consider emphasizing transferable skills and relevant experience.")
    else:
        # Requirement 3.3: Enhanced message when no matching skills found
        print(f"│ ❌ NO DIRECT SKILL MATCHES FOUND")
        print(f"│")
        print(f"│ 🔍 This suggests one of the following:")
        print(f"│   • Your resume may not use the same terminology as the job posting")
        print(f"│   • Relevant skills might be embedded in experience descriptions")
        print(f"│   • You may need to develop skills specific to this role")
        print(f"│")
        print(f"│ 💡 RECOMMENDATIONS:")
        print(f"│   • Review the job description for key terms and incorporate them")
        print(f"│   • Add a 'Core Competencies' or 'Technical Skills' section")
        print(f"│   • Highlight transferable skills from your experience")
    
    print(f"└─────────────────────────────────────────────────────────────────")


def _display_enhanced_skill_gaps_section(results: MatchResult) -> None:
    """Display missing skills categorized by priority with better visual hierarchy"""
    print(f"\n┌─ ❌ SKILL GAPS & OPPORTUNITIES")
    print(f"│")
    
    total_gaps = sum(len(skills) for skills in results.skill_gaps.values())
    
    if total_gaps == 0:
        # Requirement 4.4: Enhanced message when no missing skills identified
        print(f"│ 🎉 OUTSTANDING! All key skills are present in your resume!")
        print(f"│")
        print(f"│ ✨ Your resume demonstrates comprehensive coverage of job requirements.")
        print(f"│    You appear to meet or exceed the skill expectations for this role.")
        print(f"│")
        print(f"│ 🚀 NEXT STEPS:")
        print(f"│   • Focus on quantifying your achievements with these skills")
        print(f"│   • Ensure your experience examples showcase these competencies")
        print(f"│   • Consider adding specific project outcomes and metrics")
    else:
        print(f"│ 📊 IDENTIFIED {total_gaps} SKILL GAP{'S' if total_gaps != 1 else ''} TO ADDRESS")
        print(f"│")
        
        # Enhanced category display with priority indicators
        gap_categories = [
            ("Critical", "🔴", "MUST-HAVE skills essential for role success", results.skill_gaps.get('Critical', [])),
            ("Important", "🟡", "VALUABLE skills that strengthen your candidacy", results.skill_gaps.get('Important', [])),
            ("Nice-to-have", "🟢", "BONUS skills that would be advantageous", results.skill_gaps.get('Nice-to-have', []))
        ]
        
        for category, indicator, description, skills in gap_categories:
            if skills:
                print(f"│ {indicator} {category.upper()} GAPS ({len(skills)} skill{'s' if len(skills) != 1 else ''}):")
                print(f"│   {description}")
                print(f"│")
                for skill in skills:
                    print(f"│   • {skill}")
                print(f"│")
        
        # Enhanced actionable summary with priority guidance
        critical_count = len(results.skill_gaps.get('Critical', []))
        important_count = len(results.skill_gaps.get('Important', []))
        
        print(f"│ 🎯 PRIORITY ACTION PLAN:")
        if critical_count > 0:
            print(f"│   1. IMMEDIATE: Address {critical_count} critical skill{'s' if critical_count != 1 else ''} first")
            if important_count > 0:
                print(f"│   2. NEXT: Work on {important_count} important skill{'s' if important_count != 1 else ''}")
            print(f"│   3. STRATEGY: Add these to resume or develop through training/projects")
        elif important_count > 0:
            print(f"│   1. FOCUS: Highlight or develop {important_count} important skill{'s' if important_count != 1 else ''}")
            print(f"│   2. STRATEGY: Emphasize related experience or seek skill development")
        else:
            print(f"│   • Consider adding nice-to-have skills to stand out from other candidates")
    
    print(f"└─────────────────────────────────────────────────────────────────")


def _display_enhanced_suggestions_section(results: MatchResult) -> None:
    """Display improvement suggestions with actionable formatting (Requirement 5.3)"""
    print(f"\n┌─ 💡 ACTIONABLE IMPROVEMENT RECOMMENDATIONS")
    print(f"│")
    
    if results.suggestions:
        suggestion_count = len(results.suggestions)
        print(f"│ 📝 {suggestion_count} STRATEGIC RECOMMENDATION{'S' if suggestion_count != 1 else ''}:")
        print(f"│")
        
        # Enhanced suggestion display with priority indicators
        for i, suggestion in enumerate(results.suggestions, 1):
            # Add priority indicators for first few suggestions
            if i == 1:
                priority_icon = "🔥"
                priority_text = "HIGH IMPACT"
            elif i == 2:
                priority_icon = "⭐"
                priority_text = "IMPORTANT"
            elif i == 3:
                priority_icon = "💫"
                priority_text = "VALUABLE"
            else:
                priority_icon = "✓"
                priority_text = "HELPFUL"
            
            print(f"│ {priority_icon} RECOMMENDATION {i} ({priority_text}):")
            
            # Format suggestion with better line wrapping
            suggestion_lines = suggestion.split('. ')
            for j, line in enumerate(suggestion_lines):
                if j == 0:
                    print(f"│   {line}{'.' if not line.endswith('.') else ''}")
                else:
                    print(f"│   {line}{'.' if not line.endswith('.') and line else ''}")
            print(f"│")
        
        # Enhanced implementation guidance
        print(f"│ 🚀 IMPLEMENTATION STRATEGY:")
        print(f"│   • Start with HIGH IMPACT recommendation for maximum benefit")
        print(f"│   • Implement 1-2 changes at a time for manageable progress")
        print(f"│   • Focus on specific, measurable improvements")
        print(f"│   • Review and update your resume after each change")
        print(f"│")
        print(f"│ ⏱️  TIMELINE: Aim to implement top 3 recommendations within 1-2 weeks")
    else:
        print(f"│ ✨ EXCELLENT! Your resume appears well-optimized for this position.")
        print(f"│")
        print(f"│ 🎯 FINE-TUNING OPPORTUNITIES:")
        print(f"│   • Add quantifiable achievements and specific metrics")
        print(f"│   • Include relevant project outcomes and business impact")
        print(f"│   • Ensure consistent terminology with the job description")
        print(f"│   • Consider adding a compelling professional summary")
    
    print(f"└─────────────────────────────────────────────────────────────────")


def _display_enhanced_processing_info(results: MatchResult) -> None:
    """Display processing time and additional info with detailed indicators"""
    print(f"\n┌─ ⏱️  ANALYSIS PERFORMANCE METRICS")
    print(f"│")
    
    # Enhanced processing time display with context
    processing_time = results.processing_time
    if processing_time < 5:
        time_indicator = "🚀"
        time_comment = "LIGHTNING FAST"
        performance_note = "Optimal API response time"
    elif processing_time < 15:
        time_indicator = "⚡"
        time_comment = "QUICK ANALYSIS"
        performance_note = "Excellent processing speed"
    elif processing_time < 25:
        time_indicator = "⏱️"
        time_comment = "STANDARD PROCESSING"
        performance_note = "Normal analysis duration"
    else:
        time_indicator = "🐌"
        time_comment = "THOROUGH ANALYSIS"
        performance_note = "Comprehensive deep analysis"
    
    print(f"│ {time_indicator} PROCESSING TIME: {processing_time:.1f} seconds ({time_comment})")
    print(f"│ 📊 PERFORMANCE: {performance_note}")
    print(f"│")
    
    # Enhanced match category display with detailed context
    category_details = {
        "Strong Match": {
            "icon": "🎯",
            "message": "EXCELLENT COMPATIBILITY DETECTED",
            "detail": "Your profile aligns strongly with role requirements",
            "confidence": "High confidence in role suitability"
        },
        "Moderate Match": {
            "icon": "📊", 
            "message": "GOOD POTENTIAL WITH OPTIMIZATION OPPORTUNITIES",
            "detail": "Solid foundation with targeted improvements needed",
            "confidence": "Moderate confidence with strategic enhancements"
        },
        "Poor Match": {
            "icon": "🔧",
            "message": "SIGNIFICANT DEVELOPMENT OPPORTUNITIES IDENTIFIED", 
            "detail": "Major gaps require strategic skill building",
            "confidence": "Requires substantial profile strengthening"
        }
    }
    
    category_info = category_details.get(results.match_category, {
        "icon": "📋",
        "message": "ANALYSIS COMPLETED",
        "detail": "Review recommendations for next steps",
        "confidence": "Assessment complete"
    })
    
    print(f"│ {category_info['icon']} RESULT: {category_info['message']}")
    print(f"│ 💭 INSIGHT: {category_info['detail']}")
    print(f"│ 🎲 ASSESSMENT: {category_info['confidence']}")
    
    print(f"└─────────────────────────────────────────────────────────────────")


def _display_results_summary(results: MatchResult) -> None:
    """Add summary footer with key takeaways and next steps"""
    print(f"\n┌─ 📋 EXECUTIVE SUMMARY & NEXT STEPS")
    print(f"│")
    
    # Generate summary based on results
    score = results.score
    matching_skills_count = len(results.matching_skills)
    total_gaps = sum(len(skills) for skills in results.skill_gaps.values())
    critical_gaps = len(results.skill_gaps.get('Critical', []))
    
    # Overall assessment
    if score >= 70:
        assessment = "STRONG CANDIDATE PROFILE"
        recommendation = "Focus on application strategy and interview preparation"
    elif score >= 50:
        assessment = "COMPETITIVE CANDIDATE WITH OPTIMIZATION POTENTIAL"
        recommendation = "Implement key recommendations to strengthen your profile"
    elif score >= 30:
        assessment = "DEVELOPING CANDIDATE REQUIRING STRATEGIC IMPROVEMENTS"
        recommendation = "Address critical gaps before applying to similar roles"
    else:
        assessment = "SIGNIFICANT PROFILE DEVELOPMENT NEEDED"
        recommendation = "Consider skill development or targeting different role types"
    
    print(f"│ 🎯 OVERALL ASSESSMENT: {assessment}")
    print(f"│ 🚀 PRIMARY RECOMMENDATION: {recommendation}")
    print(f"│")
    
    # Key metrics summary
    print(f"│ 📊 KEY METRICS:")
    print(f"│   • Compatibility Score: {score}% ({results.match_category})")
    print(f"│   • Matching Skills: {matching_skills_count} identified")
    print(f"│   • Skill Gaps: {total_gaps} total ({critical_gaps} critical)")
    print(f"│   • Recommendations: {len(results.suggestions)} actionable items")
    print(f"│")
    
    # Next steps based on score
    print(f"│ 📝 IMMEDIATE NEXT STEPS:")
    if score >= 70:
        print(f"│   1. ✅ Apply with confidence - your profile is well-aligned")
        print(f"│   2. 🎯 Prepare for interviews focusing on your matching skills")
        print(f"│   3. 📈 Consider minor optimizations from recommendations")
    elif score >= 50:
        print(f"│   1. 🔧 Implement top 2-3 recommendations before applying")
        print(f"│   2. 💪 Emphasize your {matching_skills_count} matching skills in applications")
        print(f"│   3. 📚 Address critical skill gaps through training or projects")
    elif score >= 30:
        print(f"│   1. 🎯 Focus on addressing {critical_gaps} critical skill gaps first")
        print(f"│   2. 📝 Significantly revise resume using provided recommendations")
        print(f"│   3. 🔍 Consider additional skill development before applying")
    else:
        print(f"│   1. 📚 Invest in skill development for this role type")
        print(f"│   2. 🔄 Consider targeting roles better aligned with current skills")
        print(f"│   3. 💼 Explore transitional roles to build required experience")
    
    print(f"│")
    print(f"│ 🌟 Remember: This analysis provides guidance for optimization.")
    print(f"│    Your unique experience and potential extend beyond any single metric!")
    print(f"└─────────────────────────────────────────────────────────────────")
    print("=" * 70)





def handle_errors(error: Exception) -> None:
    """
    Enhanced centralized error handling with comprehensive guidance and recovery options
    
    Args:
        error: Exception that occurred
    """
    print(f"\n❌ ERROR: {str(error)}")
    
    # Provide specific guidance based on error type with enhanced recovery options
    error_str = str(error).lower()
    
    if "api key" in error_str:
        print("\n💡 API KEY ISSUE - To fix this:")
        print("   1. Get a Perplexity API key from https://www.perplexity.ai/")
        print("   2. Set the environment variable:")
        print("      • macOS/Linux: export PERPLEXITY_API_KEY='your-key-here'")
        print("      • Windows: set PERPLEXITY_API_KEY=your-key-here")
        print("   3. Or create a .env file with: PERPLEXITY_API_KEY=your-key-here")
        print("   4. Restart the application")
        print("\n🔍 Troubleshooting:")
        print("   • Ensure your API key starts with 'pplx-'")
        print("   • Check that your account has sufficient credits")
        print("   • Verify the key hasn't expired")
    
    elif "rate limit" in error_str:
        # Extract wait time if available
        import re
        wait_match = re.search(r'(\d+)\s*seconds?', error_str)
        wait_time = wait_match.group(1) if wait_match else "60"
        
        print(f"\n💡 RATE LIMIT EXCEEDED - To fix this:")
        print(f"   1. Wait {wait_time} seconds before retrying")
        print("   2. Consider upgrading your Perplexity API plan for higher limits")
        print("   3. Try using shorter resume or job description text")
        print("\n📊 Usage Tips:")
        print("   • Space out your requests to avoid hitting limits")
        print("   • Consider processing during off-peak hours")
        print("   • Monitor your API usage at https://www.perplexity.ai/settings/api")
    
    elif "network" in error_str or "connection" in error_str:
        print("\n💡 NETWORK ISSUE - To fix this:")
        print("   1. Check your internet connection")
        print("   2. Try again in a few moments")
        print("   3. Verify that api.perplexity.ai is accessible")
        print("   4. Check if you're behind a corporate firewall")
        print("\n🔍 Advanced Troubleshooting:")
        print("   • Try accessing https://api.perplexity.ai in your browser")
        print("   • Check DNS resolution: nslookup api.perplexity.ai")
        print("   • Verify proxy settings if applicable")
        print("   • Consider using a different network connection")
    
    elif "pdf" in error_str or "file" in error_str:
        print("\n💡 FILE ISSUE - To fix this:")
        print("   1. Ensure the file is a valid PDF")
        print("   2. Try a different resume file")
        print("   3. Check that the file is not corrupted or password-protected")
        print("   4. Verify the file path is correct")
        print("\n🔧 File Troubleshooting:")
        print("   • Try opening the PDF in a different viewer")
        print("   • Re-save the PDF from the original document")
        print("   • Ensure the PDF contains selectable text (not just images)")
        print("   • Check file permissions and accessibility")
    
    elif "timeout" in error_str:
        print("\n💡 TIMEOUT ISSUE - To fix this:")
        print("   1. Try again with a shorter resume or job description")
        print("   2. Check your internet connection speed")
        print("   3. Wait a few minutes and retry")
        print("\n⚡ Performance Tips:")
        print("   • Use concise, well-formatted documents")
        print("   • Avoid extremely long job descriptions")
        print("   • Consider processing during off-peak hours")
    
    elif "json" in error_str or "parse" in error_str:
        print("\n💡 PARSING ISSUE - To fix this:")
        print("   1. This is usually a temporary API issue - try again")
        print("   2. Try with a different resume or job description")
        print("   3. Check that your inputs contain valid text")
        print("\n🔍 If the issue persists:")
        print("   • The API service may be experiencing issues")
        print("   • Try again in a few minutes")
        print("   • Contact support if the problem continues")
    
    elif "memory" in error_str or "resource" in error_str:
        print("\n💡 RESOURCE ISSUE - To fix this:")
        print("   1. Try with a smaller PDF file")
        print("   2. Use a more concise job description")
        print("   3. Restart the application")
        print("\n💾 Memory Optimization:")
        print("   • Close other applications to free up memory")
        print("   • Use compressed PDF files when possible")
        print("   • Consider processing one document at a time")
    
    elif "permission" in error_str or "access" in error_str:
        print("\n💡 PERMISSION ISSUE - To fix this:")
        print("   1. Check file and directory permissions")
        print("   2. Try copying files to your home directory")
        print("   3. Run the application with appropriate permissions")
        print("\n🔐 Permission Troubleshooting:")
        print("   • Ensure you have read access to the PDF file")
        print("   • Check that the file isn't locked by another application")
        print("   • Verify directory permissions for temporary files")
    
    else:
        print("\n💡 GENERAL TROUBLESHOOTING:")
        print("   1. Try restarting the application")
        print("   2. Check your inputs and configuration")
        print("   3. Ensure all dependencies are properly installed")
        print("\n🆘 If the problem persists:")
        print("   • Check the application logs for more details")
        print("   • Try with different input files")
        print("   • Consider updating the application")
        print("   • Contact support with the error details above")
    
    # Add recovery suggestions based on error context
    print(f"\n🔄 RECOVERY OPTIONS:")
    print(f"   • Type 'y' to try again with the same inputs")
    print(f"   • Type 'n' to start over with new inputs")
    print(f"   • Type 'q' to quit the application")


def _process_analysis(resume_path: str, jd_text: str) -> MatchResult:
    """
    Process the resume and job description analysis with comprehensive error handling and retry logic
    
    Args:
        resume_path: Path to resume PDF file
        jd_text: Job description text
        
    Returns:
        MatchResult object with analysis results
        
    Raises:
        Exception: If analysis fails after all retry attempts
    """
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"🔄 Retrying analysis (attempt {attempt + 1}/{max_retries})...")
            
            # Step 1: Extract and clean resume text
            try:
                print("📄 Extracting text from resume PDF...")
                resume_text = extract_text_from_pdf(resume_path)
                cleaned_resume_text = clean_resume_text(resume_text)
                print("✅ Resume text extracted successfully")
            except Exception as e:
                error_msg = f"Failed to process resume PDF: {str(e)}"
                if attempt == max_retries - 1:
                    raise Exception(error_msg)
                print(f"⚠️  {error_msg}")
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            
            # Step 2: Parse job description
            try:
                print("📋 Parsing job description...")
                jd_data = parse_jd_text(jd_text)
                print("✅ Job description parsed successfully")
            except Exception as e:
                error_msg = f"Failed to parse job description: {str(e)}"
                if attempt == max_retries - 1:
                    raise Exception(error_msg)
                print(f"⚠️  {error_msg}")
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            
            # Step 3: Perform matching analysis (most likely to fail due to API issues)
            try:
                print("🤖 Performing AI-powered matching analysis...")
                results = analyze_match(cleaned_resume_text, jd_data.__dict__)
                print("✅ Analysis completed successfully")
                return results
            except Exception as e:
                error_msg = str(e)
                
                # Check if this is a retryable error
                if _is_retryable_error(error_msg):
                    if attempt == max_retries - 1:
                        raise Exception(f"Analysis failed after {max_retries} attempts: {error_msg}")
                    
                    print(f"⚠️  Analysis failed: {error_msg}")
                    
                    # Extract wait time from rate limit errors
                    wait_time = _extract_wait_time_from_error(error_msg)
                    if wait_time > 0:
                        print(f"⏳ Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                    else:
                        print(f"⏳ Waiting {retry_delay} seconds before retry...")
                        time.sleep(retry_delay)
                    continue
                else:
                    # Non-retryable error, raise immediately
                    raise Exception(f"Analysis failed: {error_msg}")
                    
        except KeyboardInterrupt:
            print("\n\n❌ Analysis cancelled by user.")
            raise Exception("Analysis cancelled by user")
        except Exception as e:
            # If this is the last attempt or a non-retryable error, re-raise
            if attempt == max_retries - 1 or not _is_retryable_error(str(e)):
                raise
            
            # Otherwise, continue to next retry
            continue
    
    # This should never be reached, but just in case
    raise Exception(f"Analysis failed after {max_retries} attempts with unknown error")


def _is_retryable_error(error_msg: str) -> bool:
    """
    Determine if an error is retryable based on the error message
    
    Args:
        error_msg: The error message to analyze
        
    Returns:
        True if the error is retryable, False otherwise
    """
    error_lower = error_msg.lower()
    
    # Retryable errors (usually temporary issues)
    retryable_indicators = [
        'timeout', 'timed out', 'connection', 'network', 'temporary',
        'rate limit', 'server error', 'service unavailable', 'bad gateway',
        'gateway timeout', 'internal server error', '500', '502', '503', '504',
        'failed to connect', 'connection refused', 'connection reset',
        'read timeout', 'ssl', 'certificate'
    ]
    
    # Non-retryable errors (usually configuration or input issues)
    non_retryable_indicators = [
        'api key', 'unauthorized', '401', 'forbidden', '403',
        'invalid', 'corrupted', 'not found', 'permission',
        'file not found', 'directory', 'empty', 'too short',
        'doesn\'t appear to be', 'malformed', 'bad request', '400'
    ]
    
    # Check for non-retryable errors first (these take precedence)
    for indicator in non_retryable_indicators:
        if indicator in error_lower:
            return False
    
    # Check for retryable errors
    for indicator in retryable_indicators:
        if indicator in error_lower:
            return True
    
    # Default to retryable for unknown errors (conservative approach)
    return True


def _extract_wait_time_from_error(error_msg: str) -> int:
    """
    Extract wait time from rate limit error messages
    
    Args:
        error_msg: The error message that may contain wait time
        
    Returns:
        Wait time in seconds, or 0 if no wait time found
    """
    import re
    
    # Look for patterns like "wait 60 seconds" or "retry after 30"
    patterns = [
        r'wait (\d+) seconds?',
        r'retry after (\d+)',
        r'(\d+) seconds? before',
        r'wait (\d+)s',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, error_msg.lower())
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                continue
    
    return 0


def _ask_continue() -> bool:
    """Ask user if they want to process another resume-JD combination"""
    print("\n" + "-" * 40)
    while True:
        response = input("Would you like to analyze another resume and job description? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            print()  # Add spacing
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")


def _check_api_configuration() -> bool:
    """
    Enhanced API configuration check on startup with comprehensive setup validation
    Implements Requirements 7.5, 7.4
    
    Returns:
        True if configuration is valid, False otherwise
    """
    print("🔧 Setting up Resume Matcher AI...")
    print()
    
    # Use enhanced setup environment function
    setup_result = setup_environment()
    
    if setup_result['success']:
        # Display successful setup steps
        for step in setup_result['setup_steps']:
            print(step)
        
        # Display any warnings
        if setup_result['warnings']:
            print()
            for warning in setup_result['warnings']:
                print(f"⚠️  WARNING: {warning}")
        
        # Display usage statistics if available
        try:
            stats = get_usage_statistics(days=7)
            if stats['total_calls'] > 0:
                print()
                print("📊 RECENT USAGE (Last 7 days):")
                print(f"   • API Calls: {stats['total_calls']} ({stats['successful_calls']} successful)")
                print(f"   • Estimated Cost: ${stats['total_cost']:.3f}")
                print(f"   • Avg Processing Time: {stats['average_processing_time']:.1f}s")
        except Exception:
            # Silently fail if usage stats can't be displayed
            pass
        
        print()
        return True
    
    else:
        # Display setup errors
        print("❌ CONFIGURATION SETUP FAILED")
        print()
        
        for error in setup_result['errors']:
            print(f"❌ {error}")
        
        print()
        
        # Display comprehensive setup instructions
        display_setup_instructions()
        
        return False


if __name__ == "__main__":
    main()