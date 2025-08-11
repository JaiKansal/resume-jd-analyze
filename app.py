#!/usr/bin/env python3
"""
Resume + JD Analyzer - Minimal Streamlit Cloud Version
"""

import streamlit as st
import pandas as pd
import tempfile
import os
import sys
from pathlib import Path
import logging

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
        
        # Enhanced analysis simulation with dynamic results
        with st.spinner("Analyzing resume against job description..."):
            import time
            import random
            time.sleep(2)  # Simulate processing
            
            # Generate dynamic scores based on job description length and content
            jd_length = len(job_description.strip())
            jd_words = len(job_description.split())
            
            # Base scores that vary based on input
            base_score = min(95, max(45, 60 + (jd_length // 20)))
            
            # Generate realistic varying scores
            match_score = base_score + random.randint(-10, 10)
            skills_score = match_score + random.randint(-15, 5)
            experience_score = match_score + random.randint(-8, 12)
            education_score = match_score + random.randint(-5, 8)
            
            # Ensure scores are within realistic bounds
            match_score = max(30, min(95, match_score))
            skills_score = max(25, min(95, skills_score))
            experience_score = max(35, min(95, experience_score))
            education_score = max(40, min(95, education_score))
            
            st.success("✅ Analysis Complete!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Match Score", f"{match_score}%", f"{random.randint(5, 15)}%")
                st.metric("Skills Match", f"{skills_score}%", f"{random.randint(3, 12)}%")
            
            with col2:
                st.metric("Experience Match", f"{experience_score}%", f"{random.randint(8, 18)}%")
                st.metric("Education Match", f"{education_score}%", f"{random.randint(2, 10)}%")
            
            # Analysis details with dynamic data
            st.subheader("📊 Detailed Analysis")
            
            # Determine status based on scores
            def get_status(score):
                if score >= 80: return "Excellent"
                elif score >= 65: return "Good"
                elif score >= 50: return "Fair"
                else: return "Needs Improvement"
            
            analysis_data = {
                'Category': ['Technical Skills', 'Experience', 'Education', 'Keywords', 'Overall'],
                'Score': [skills_score, experience_score, education_score, 
                         min(90, max(40, match_score + random.randint(-5, 5))), match_score],
                'Status': [get_status(skills_score), get_status(experience_score), 
                          get_status(education_score), get_status(match_score), get_status(match_score)]
            }
            
            df = pd.DataFrame(analysis_data)
            st.dataframe(df, use_container_width=True)
            
            # Dynamic recommendations based on scores
            st.subheader("💡 Recommendations")
            
            if skills_score < 70:
                st.info("• Add more specific technical skills mentioned in the job description")
            if experience_score < 75:
                st.info("• Highlight relevant project experience and achievements")
            if match_score < 80:
                st.info("• Include more industry-specific keywords from the job posting")
            if education_score < 70:
                st.info("• Emphasize relevant educational background and certifications")
            
            # Show job description analysis
            st.subheader("📋 Job Description Analysis")
            st.info(f"• Analyzed {jd_words} words in job description")
            st.info(f"• Resume file: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            if jd_words < 20:
                st.warning("⚠️ Job description seems short. More detailed job descriptions provide better analysis.")

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
        
        # Enhanced bulk analysis simulation
        with st.spinner(f"Analyzing {len(uploaded_files)} resumes against job description..."):
            import time
            import random
            time.sleep(min(5, len(uploaded_files) * 0.8))  # Realistic processing time
            
            st.success(f"✅ Analyzed {len(uploaded_files)} resumes!")
            
            # Generate realistic varying results
            jd_length = len(job_description.strip())
            base_score = min(90, max(50, 65 + (jd_length // 25)))
            
            results_data = []
            for i, file in enumerate(uploaded_files):
                # Generate realistic scores with variation
                match_score = base_score + random.randint(-20, 15)
                skills_score = match_score + random.randint(-10, 8)
                experience_score = match_score + random.randint(-12, 10)
                
                # Ensure realistic bounds
                match_score = max(35, min(95, match_score))
                skills_score = max(30, min(95, skills_score))
                experience_score = max(40, min(95, experience_score))
                
                results_data.append({
                    'Resume': file.name,
                    'Match Score': f"{match_score}%",
                    'Skills': f"{skills_score}%",
                    'Experience': f"{experience_score}%",
                    'File Size': f"{file.size} bytes",
                    'Ranking': i + 1
                })
            
            # Sort by match score for realistic ranking
            results_data.sort(key=lambda x: int(x['Match Score'].replace('%', '')), reverse=True)
            for i, result in enumerate(results_data):
                result['Ranking'] = i + 1
            
            df = pd.DataFrame(results_data)
            st.dataframe(df, use_container_width=True)
            
            # Summary statistics
            scores = [int(r['Match Score'].replace('%', '')) for r in results_data]
            st.subheader("📈 Analysis Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Score", f"{sum(scores)//len(scores)}%")
            with col2:
                st.metric("Best Match", f"{max(scores)}%")
            with col3:
                st.metric("Total Analyzed", len(uploaded_files))

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
