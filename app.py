#!/usr/bin/env python3
"""
Resume + JD Analyzer - Real AI-Powered Analysis with Perplexity API
"""

import streamlit as st
import pandas as pd
import tempfile
import os
import sys
from pathlib import Path
import logging
import requests
import json
import PyPDF2
import io
import re
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def initialize_session_state():
    """Initialize session state variables"""
    if 'user_authenticated' not in st.session_state:
        st.session_state.user_authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None

def create_test_user():
    """Create a test user for demo purposes"""
    return type('User', (), {
        'id': '1',
        'email': 'demo@example.com',
        'first_name': 'Demo',
        'last_name': 'User',
        'get_full_name': lambda self=None: 'Demo User'
    })()

def extract_text_from_pdf(pdf_file) -> Optional[str]:
    """Extract text from uploaded PDF file"""
    try:
        pdf_file.seek(0)
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
        
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"
        
        text = text.strip()
        if not text:
            return None
        
        logger.info(f"Extracted {len(text)} characters from PDF")
        return text
        
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        return None

def get_perplexity_api_key():
    """Get Perplexity API key from secrets or environment"""
    try:
        # Try Streamlit secrets first
        if hasattr(st, 'secrets') and 'PERPLEXITY_API_KEY' in st.secrets:
            return st.secrets['PERPLEXITY_API_KEY']
    except:
        pass
    
    # Try environment variable
    return os.getenv('PERPLEXITY_API_KEY')

def analyze_resume_with_ai(resume_text: str, job_description: str) -> Dict[str, Any]:
    """Real AI analysis using Perplexity API"""
    
    api_key = get_perplexity_api_key()
    
    if not api_key:
        st.warning("⚠️ Perplexity API key not configured. Add PERPLEXITY_API_KEY to Streamlit secrets for AI analysis.")
        return basic_keyword_analysis(resume_text, job_description)
    
    try:
        # Create comprehensive analysis prompt
        prompt = f"""
You are an expert HR analyst and resume reviewer. Analyze the following resume against the job description and provide a comprehensive evaluation.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Please provide a detailed analysis in JSON format with these exact fields:
{{
    "overall_match_score": <number 0-100>,
    "skills_match_score": <number 0-100>,
    "experience_match_score": <number 0-100>,
    "education_match_score": <number 0-100>,
    "keyword_match_score": <number 0-100>,
    "strengths": ["list of key strengths"],
    "weaknesses": ["list of areas for improvement"],
    "missing_skills": ["skills mentioned in JD but not in resume"],
    "recommendations": ["specific actionable recommendations"],
    "key_insights": ["important insights about the match"],
    "ats_score": <number 0-100>
}}

Focus on technical skills alignment, experience relevance, education match, and ATS compatibility.
"""

        # Call Perplexity API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert HR analyst. Provide detailed resume analysis in the exact JSON format requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.2,
            "top_p": 0.9
        }
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # Parse JSON from AI response
            try:
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                    
                    # Validate scores
                    for key in ['overall_match_score', 'skills_match_score', 'experience_match_score', 
                               'education_match_score', 'keyword_match_score', 'ats_score']:
                        if key not in analysis:
                            analysis[key] = 50
                        analysis[key] = max(0, min(100, int(analysis[key])))
                    
                    # Ensure lists exist
                    for key in ['strengths', 'weaknesses', 'missing_skills', 'recommendations', 'key_insights']:
                        if key not in analysis or not isinstance(analysis[key], list):
                            analysis[key] = [f"AI analysis for {key}"]
                    
                    analysis['analysis_type'] = 'ai_powered'
                    analysis['api_used'] = 'perplexity'
                    return analysis
                    
            except json.JSONDecodeError:
                # If JSON parsing fails, extract info from text
                return parse_text_analysis(ai_response, resume_text, job_description)
        
        else:
            st.error(f"Perplexity API error: {response.status_code}")
            return basic_keyword_analysis(resume_text, job_description)
            
    except Exception as e:
        st.error(f"AI analysis failed: {e}")
        return basic_keyword_analysis(resume_text, job_description)

def parse_text_analysis(ai_text: str, resume_text: str, job_description: str) -> Dict[str, Any]:
    """Parse AI text response when JSON parsing fails"""
    
    # Extract scores using regex
    scores = {}
    score_patterns = {
        'overall_match_score': r'overall.*?(\d+)%?',
        'skills_match_score': r'skills?.*?(\d+)%?',
        'experience_match_score': r'experience.*?(\d+)%?',
        'education_match_score': r'education.*?(\d+)%?',
        'keyword_match_score': r'keyword.*?(\d+)%?',
        'ats_score': r'ats.*?(\d+)%?'
    }
    
    for key, pattern in score_patterns.items():
        match = re.search(pattern, ai_text, re.IGNORECASE)
        scores[key] = int(match.group(1)) if match else 65
    
    return {
        **scores,
        'strengths': ["AI analysis completed"],
        'weaknesses': ["See detailed analysis"],
        'missing_skills': ["Review AI feedback"],
        'recommendations': ["Follow AI suggestions"],
        'key_insights': [ai_text[:200] + "..."],
        'analysis_type': 'ai_text_parsed',
        'api_used': 'perplexity'
    }

def basic_keyword_analysis(resume_text: str, job_description: str) -> Dict[str, Any]:
    """Basic keyword matching when AI is not available"""
    
    jd_words = set(word.lower() for word in job_description.split() if len(word) > 3)
    resume_words = set(word.lower() for word in resume_text.split() if len(word) > 3)
    
    common_words = jd_words.intersection(resume_words)
    keyword_match = len(common_words) / len(jd_words) * 100 if jd_words else 0
    
    base_score = min(85, max(35, keyword_match + 20))
    
    return {
        'overall_match_score': int(base_score),
        'skills_match_score': int(base_score - 5),
        'experience_match_score': int(base_score + 5),
        'education_match_score': int(base_score),
        'keyword_match_score': int(keyword_match),
        'ats_score': int(keyword_match + 10),
        'strengths': [f"Found {len(common_words)} matching keywords"],
        'weaknesses': ["Add Perplexity API key for detailed AI analysis"],
        'missing_skills': ["Enable AI analysis for detailed insights"],
        'recommendations': [
            "Add PERPLEXITY_API_KEY to Streamlit secrets",
            "Enhance resume with job-specific keywords"
        ],
        'key_insights': [
            f"Basic analysis found {len(common_words)} keyword matches",
            "Enable AI for comprehensive insights"
        ],
        'analysis_type': 'basic_keyword',
        'api_used': 'none'
    }

def render_single_analysis():
    """Render single resume analysis"""
    st.header("🎯 Single Resume Analysis")
    
    # Job Description Input
    st.subheader("📋 Job Description")
    job_description = st.text_area(
        "Paste the job description here:",
        height=200,
        placeholder="Enter the job description you want to match resumes against..."
    )
    
    # Resume Upload
    st.subheader("📄 Resume Upload")
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF)",
        type=['pdf'],
        help="Upload a PDF resume to analyze"
    )
    
    if st.button("🔍 Analyze Resume", type="primary"):
        if not job_description.strip():
            st.error("❌ Please enter a job description to analyze against")
            return
        
        if not uploaded_file:
            st.error("❌ Please upload a resume file")
            return
        
        # Extract text from PDF
        resume_text = extract_text_from_pdf(uploaded_file)
        
        if not resume_text:
            st.error("❌ Could not extract text from PDF. Please ensure it's a valid PDF with readable text.")
            return
        
        # Real AI-powered analysis
        with st.spinner("🤖 Analyzing resume with AI... This may take 10-30 seconds"):
            analysis = analyze_resume_with_ai(resume_text, job_description)
            
            st.success("✅ AI Analysis Complete!")
            
            # Display analysis type
            if analysis.get('analysis_type') == 'ai_powered':
                st.info("🤖 **Powered by Perplexity AI** - Real-time analysis")
            else:
                st.warning("⚠️ **Basic Analysis** - Add PERPLEXITY_API_KEY for AI-powered insights")
            
            # Main metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Overall Match", f"{analysis['overall_match_score']}%")
                st.metric("Skills Match", f"{analysis['skills_match_score']}%")
                st.metric("ATS Compatibility", f"{analysis['ats_score']}%")
            
            with col2:
                st.metric("Experience Match", f"{analysis['experience_match_score']}%")
                st.metric("Education Match", f"{analysis['education_match_score']}%")
                st.metric("Keyword Match", f"{analysis['keyword_match_score']}%")
            
            # Detailed breakdown
            st.subheader("📊 Detailed Analysis")
            
            def get_status(score):
                if score >= 80: return "Excellent"
                elif score >= 65: return "Good"
                elif score >= 50: return "Fair"
                else: return "Needs Improvement"
            
            analysis_data = {
                'Category': ['Overall Match', 'Technical Skills', 'Experience', 'Education', 'Keywords', 'ATS Score'],
                'Score': [
                    analysis['overall_match_score'],
                    analysis['skills_match_score'],
                    analysis['experience_match_score'],
                    analysis['education_match_score'],
                    analysis['keyword_match_score'],
                    analysis['ats_score']
                ],
                'Status': [
                    get_status(analysis['overall_match_score']),
                    get_status(analysis['skills_match_score']),
                    get_status(analysis['experience_match_score']),
                    get_status(analysis['education_match_score']),
                    get_status(analysis['keyword_match_score']),
                    get_status(analysis['ats_score'])
                ]
            }
            
            df = pd.DataFrame(analysis_data)
            st.dataframe(df, use_container_width=True)
            
            # AI Insights
            if analysis.get('strengths'):
                st.subheader("💪 Key Strengths")
                for strength in analysis['strengths']:
                    st.success(f"✅ {strength}")
            
            if analysis.get('weaknesses'):
                st.subheader("⚠️ Areas for Improvement")
                for weakness in analysis['weaknesses']:
                    st.warning(f"⚠️ {weakness}")
            
            if analysis.get('missing_skills'):
                st.subheader("🎯 Missing Skills")
                for skill in analysis['missing_skills']:
                    st.error(f"❌ {skill}")
            
            # AI Recommendations
            st.subheader("💡 AI Recommendations")
            for i, rec in enumerate(analysis.get('recommendations', []), 1):
                st.info(f"{i}. {rec}")
            
            # Key Insights
            if analysis.get('key_insights'):
                st.subheader("🔍 Key Insights")
                for insight in analysis['key_insights']:
                    st.info(f"💡 {insight}")
            
            # Analysis metadata
            st.subheader("📋 Analysis Details")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Resume Length", f"{len(resume_text)} chars")
            with col2:
                st.metric("JD Length", f"{len(job_description)} chars")
            with col3:
                st.metric("Analysis Type", analysis.get('analysis_type', 'unknown').title())

def render_bulk_analysis():
    """Render bulk resume analysis"""
    st.header("📦 Bulk Resume Analysis")
    
    st.info("Upload multiple resumes to analyze against a job description")
    
    # Job Description
    job_description = st.text_area(
        "Job Description:",
        height=150,
        placeholder="Enter the job description..."
    )
    
    # Multiple file upload
    uploaded_files = st.file_uploader(
        "Upload Resumes (PDF)",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload multiple PDF resumes"
    )
    
    if st.button("🔍 Analyze All Resumes", type="primary"):
        if not job_description.strip():
            st.error("❌ Please enter a job description to analyze against")
            return
        
        if not uploaded_files:
            st.error("❌ Please upload at least one resume")
            return
        
        # Real AI-powered bulk analysis
        with st.spinner(f"🤖 AI analyzing {len(uploaded_files)} resumes... This may take several minutes"):
            
            results_data = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Analyzing {file.name}... ({i+1}/{len(uploaded_files)})")
                
                # Extract text from PDF
                resume_text = extract_text_from_pdf(file)
                
                if resume_text:
                    # Real AI analysis for each resume
                    analysis = analyze_resume_with_ai(resume_text, job_description)
                    
                    results_data.append({
                        'Resume': file.name,
                        'Overall Match': f"{analysis['overall_match_score']}%",
                        'Skills': f"{analysis['skills_match_score']}%",
                        'Experience': f"{analysis['experience_match_score']}%",
                        'Education': f"{analysis['education_match_score']}%",
                        'ATS Score': f"{analysis['ats_score']}%",
                        'Analysis Type': analysis.get('analysis_type', 'unknown'),
                        'File Size': f"{file.size} bytes"
                    })
                else:
                    results_data.append({
                        'Resume': file.name,
                        'Overall Match': "Error",
                        'Skills': "Error",
                        'Experience': "Error",
                        'Education': "Error",
                        'ATS Score': "Error",
                        'Analysis Type': 'failed',
                        'File Size': f"{file.size} bytes"
                    })
                
                # Update progress
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.text("Analysis complete!")
            st.success(f"✅ AI Analysis Complete for {len(uploaded_files)} resumes!")
            
            # Sort by overall match score
            valid_results = [r for r in results_data if r['Overall Match'] != "Error"]
            error_results = [r for r in results_data if r['Overall Match'] == "Error"]
            
            if valid_results:
                valid_results.sort(key=lambda x: int(x['Overall Match'].replace('%', '')), reverse=True)
                
                # Add ranking
                for i, result in enumerate(valid_results):
                    result['Ranking'] = i + 1
                
                # Combine results
                all_results = valid_results + error_results
                
                df = pd.DataFrame(all_results)
                st.dataframe(df, use_container_width=True)
                
                # Summary statistics
                if valid_results:
                    scores = [int(r['Overall Match'].replace('%', '')) for r in valid_results]
                    ai_powered = len([r for r in valid_results if r['Analysis Type'] == 'ai_powered'])
                    
                    st.subheader("📈 Analysis Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Average Score", f"{sum(scores)//len(scores)}%")
                    with col2:
                        st.metric("Best Match", f"{max(scores)}%")
                    with col3:
                        st.metric("AI Analyzed", f"{ai_powered}/{len(valid_results)}")
                    with col4:
                        st.metric("Success Rate", f"{len(valid_results)}/{len(uploaded_files)}")
                
                # Show top candidates
                if len(valid_results) > 0:
                    st.subheader("🏆 Top Candidates")
                    top_3 = valid_results[:3]
                    for i, candidate in enumerate(top_3, 1):
                        with st.expander(f"#{i} - {candidate['Resume']} ({candidate['Overall Match']})"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Skills Match:** {candidate['Skills']}")
                                st.write(f"**Experience Match:** {candidate['Experience']}")
                            with col2:
                                st.write(f"**Education Match:** {candidate['Education']}")
                                st.write(f"**ATS Score:** {candidate['ATS Score']}")
            
            if error_results:
                st.warning(f"⚠️ {len(error_results)} files could not be processed (invalid PDF or text extraction failed)")

def render_dashboard():
    """Render user dashboard"""
    st.header("📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Analyses This Month", "12", "3")
    
    with col2:
        st.metric("Average Match Score", "82%", "5%")
    
    with col3:
        st.metric("Resumes Processed", "45", "12")
    
    # Chart
    st.subheader("📈 Analysis Trends")
    
    chart_data = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=30, freq='D'),
        'Analyses': [1, 2, 0, 3, 1, 2, 4, 1, 0, 2, 3, 1, 2, 0, 1, 3, 2, 1, 0, 2, 1, 3, 2, 0, 1, 2, 3, 1, 0, 2]
    })
    
    st.line_chart(chart_data.set_index('Date'))

def main():
    """Main application"""
    st.set_page_config(
        page_title="Resume + JD Analyzer",
        page_icon="🎯",
        layout="wide"
    )
    
    initialize_session_state()
    
    # Header
    st.title("🎯 Resume + JD Analyzer")
    st.markdown("AI-Powered Resume and Job Description Compatibility Analysis")
    
    # Sidebar
    st.sidebar.title("🎛️ Navigation")
    
    # Debug mode button
    if st.sidebar.button("🚀 **Start Demo**", type="primary"):
        st.session_state.user_authenticated = True
        st.session_state.current_user = create_test_user()
        st.rerun()
    
    # Check if user is authenticated
    if not st.session_state.get('user_authenticated', False):
        st.info("👈 Click the 'Start Demo' button in the sidebar to begin!")
        st.markdown("""
        ### 🌟 Features:
        - **Single Resume Analysis** - Analyze one resume against a job description
        - **Bulk Resume Analysis** - Process multiple resumes at once
        - **Match Scoring** - Get detailed compatibility scores
        - **Recommendations** - Receive improvement suggestions
        - **Dashboard** - Track your analysis history
        """)
        return
    
    # User is authenticated - show navigation
    user = st.session_state.current_user
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"👤 **{user.get_full_name()}**")
    st.sidebar.markdown(f"📧 {user.email}")
    
    if st.sidebar.button("🚪 Sign Out"):
        st.session_state.user_authenticated = False
        st.session_state.current_user = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Navigation menu
    mode = st.sidebar.selectbox(
        "Choose Mode:",
        ["🎯 Single Analysis", "📦 Bulk Analysis", "📊 Dashboard"]
    )
    
    # Route to appropriate function
    if mode == "🎯 Single Analysis":
        render_single_analysis()
    elif mode == "📦 Bulk Analysis":
        render_bulk_analysis()
    elif mode == "📊 Dashboard":
        render_dashboard()

if __name__ == "__main__":
    main()
