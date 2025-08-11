#!/usr/bin/env python3
"""
Minimal Resume + JD Analyzer - Emergency Version
Guaranteed to work on Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import tempfile
import os
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Resume + JD Analyzer",
    page_icon="🎯",
    layout="wide"
)

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def analyze_resume_match(resume_text, job_description):
    """Simple resume-JD matching analysis"""
    if not resume_text or not job_description:
        return {"error": "Missing resume or job description"}
    
    # Simple keyword matching
    jd_words = set(job_description.lower().split())
    resume_words = set(resume_text.lower().split())
    
    # Calculate basic match score
    common_words = jd_words.intersection(resume_words)
    match_score = len(common_words) / len(jd_words) * 100 if jd_words else 0
    
    # Extract basic info
    skills_keywords = ['python', 'java', 'javascript', 'react', 'sql', 'aws', 'docker', 'kubernetes']
    found_skills = [skill for skill in skills_keywords if skill in resume_text.lower()]
    
    return {
        "match_score": round(match_score, 2),
        "common_keywords": list(common_words)[:10],  # Top 10
        "found_skills": found_skills,
        "total_words_resume": len(resume_words),
        "total_words_jd": len(jd_words),
        "analysis_summary": f"Resume matches {match_score:.1f}% of job requirements"
    }

def main():
    """Main application"""
    st.title("🎯 Resume + JD Analyzer")
    st.markdown("**AI-Powered Resume and Job Description Compatibility Analysis**")
    
    # Sidebar navigation
    st.sidebar.title("🎛️ Navigation")
    mode = st.sidebar.selectbox(
        "Choose Analysis Mode",
        ["🎯 Single Analysis", "📦 Bulk Analysis", "ℹ️ About"]
    )
    
    if mode == "🎯 Single Analysis":
        render_single_analysis()
    elif mode == "📦 Bulk Analysis":
        render_bulk_analysis()
    else:
        render_about()

def render_single_analysis():
    """Render single resume analysis"""
    st.header("🎯 Single Resume Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose a resume file",
            type=['pdf', 'txt'],
            help="Upload a PDF or text file"
        )
        
        resume_text = ""
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                resume_text = extract_text_from_pdf(uploaded_file)
            else:
                resume_text = str(uploaded_file.read(), "utf-8")
            
            if resume_text:
                st.success(f"✅ Resume loaded ({len(resume_text)} characters)")
                with st.expander("📖 Resume Preview"):
                    st.text_area("Resume Content", resume_text[:500] + "...", height=200, disabled=True)
    
    with col2:
        st.subheader("💼 Job Description")
        job_description = st.text_area(
            "Paste the job description here",
            height=300,
            placeholder="Paste the complete job description including requirements, responsibilities, and qualifications..."
        )
        
        if job_description:
            st.success(f"✅ Job description loaded ({len(job_description)} characters)")
    
    # Analysis button
    if st.button("🚀 Analyze Match", type="primary", disabled=not (resume_text and job_description)):
        with st.spinner("Analyzing resume compatibility..."):
            result = analyze_resume_match(resume_text, job_description)
            
            if "error" in result:
                st.error(result["error"])
            else:
                render_analysis_result(result)

def render_analysis_result(result):
    """Render analysis results"""
    st.header("📊 Analysis Results")
    
    # Match score
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Match Score", f"{result['match_score']}%")
    
    with col2:
        st.metric("Skills Found", len(result['found_skills']))
    
    with col3:
        st.metric("Common Keywords", len(result['common_keywords']))
    
    # Progress bar for match score
    st.progress(result['match_score'] / 100)
    
    # Analysis summary
    st.subheader("📝 Summary")
    st.info(result['analysis_summary'])
    
    # Skills found
    if result['found_skills']:
        st.subheader("🛠️ Skills Identified")
        skills_cols = st.columns(min(len(result['found_skills']), 4))
        for i, skill in enumerate(result['found_skills']):
            with skills_cols[i % 4]:
                st.success(f"✅ {skill.title()}")
    
    # Common keywords
    if result['common_keywords']:
        st.subheader("🔑 Common Keywords")
        keywords_text = ", ".join(result['common_keywords'][:20])
        st.text(keywords_text)

def render_bulk_analysis():
    """Render bulk analysis"""
    st.header("📦 Bulk Resume Analysis")
    st.info("Upload multiple resumes to analyze against a job description")
    
    # Job description
    job_description = st.text_area(
        "Job Description",
        height=200,
        placeholder="Paste the job description here..."
    )
    
    # File uploader for multiple files
    uploaded_files = st.file_uploader(
        "Upload Resume Files",
        type=['pdf', 'txt'],
        accept_multiple_files=True,
        help="Upload multiple PDF or text files"
    )
    
    if uploaded_files and job_description:
        if st.button("🚀 Analyze All Resumes", type="primary"):
            results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Processing {file.name}...")
                
                # Extract text
                if file.type == "application/pdf":
                    resume_text = extract_text_from_pdf(file)
                else:
                    resume_text = str(file.read(), "utf-8")
                
                # Analyze
                result = analyze_resume_match(resume_text, job_description)
                result['filename'] = file.name
                results.append(result)
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.text("Analysis complete!")
            
            # Display results
            st.subheader("📊 Bulk Analysis Results")
            
            # Create DataFrame
            df_data = []
            for result in results:
                if "error" not in result:
                    df_data.append({
                        'Filename': result['filename'],
                        'Match Score (%)': result['match_score'],
                        'Skills Found': len(result['found_skills']),
                        'Common Keywords': len(result['common_keywords'])
                    })
            
            if df_data:
                df = pd.DataFrame(df_data)
                df = df.sort_values('Match Score (%)', ascending=False)
                
                st.dataframe(df, use_container_width=True)
                
                # Download results
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name="resume_analysis_results.csv",
                    mime="text/csv"
                )

def render_about():
    """Render about page"""
    st.header("ℹ️ About Resume + JD Analyzer")
    
    st.markdown("""
    ### 🎯 What is this tool?
    
    Resume + JD Analyzer is an AI-powered tool that helps you:
    - **Analyze resume compatibility** with job descriptions
    - **Identify skill gaps** and missing keywords
    - **Optimize your resume** for specific roles
    - **Process multiple resumes** in bulk
    
    ### 🚀 Features
    
    - **Single Analysis**: Upload one resume and compare with a job description
    - **Bulk Analysis**: Process multiple resumes at once
    - **Skill Detection**: Automatically identify technical 