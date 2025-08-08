#!/usr/bin/env python3
"""
Sample integration showing how to use the enhanced analysis system
"""

import streamlit as st
from analysis.enhanced_analysis_service import enhanced_analysis_service, create_analysis_result
from analysis.analysis_history_ui import show_analysis_history_page

def example_save_analysis():
    """Example of how to save an analysis"""
    
    # Sample analysis data (replace with real analysis results)
    analysis_data = {
        'analysis_type': 'resume_jd_match',
        'match_score': 85.5,
        'strengths': [
            'Strong technical skills in Python and machine learning',
            'Relevant experience in data analysis',
            'Good educational background'
        ],
        'weaknesses': [
            'Limited experience with cloud platforms',
            'Could improve communication skills section'
        ],
        'recommendations': [
            'Add more details about cloud computing experience',
            'Include specific project outcomes and metrics',
            'Highlight leadership and teamwork experiences'
        ],
        'keywords_matched': ['Python', 'Machine Learning', 'Data Analysis', 'SQL'],
        'keywords_missing': ['AWS', 'Docker', 'Kubernetes'],
        'sections_analysis': {
            'experience': {'score': 90, 'feedback': 'Strong relevant experience'},
            'skills': {'score': 85, 'feedback': 'Good technical skills'},
            'education': {'score': 80, 'feedback': 'Solid educational background'}
        },
        'processing_time_seconds': 2.5,
        'api_cost_usd': 0.05,
        'tokens_used': 1250
    }
    
    # Create and save analysis
    analysis_result = create_analysis_result(
        user_id="sample_user_id",
        resume_filename="john_doe_resume.pdf",
        job_description="Senior Data Scientist position...",
        resume_content="John Doe\nData Scientist\n...",
        analysis_data=analysis_data
    )
    
    success = enhanced_analysis_service.save_analysis(analysis_result)
    
    if success:
        st.success(f"✅ Analysis saved! ID: {analysis_result.id}")
    else:
        st.error("❌ Failed to save analysis")

def example_show_history():
    """Example of how to show analysis history"""
    user_id = "sample_user_id"  # Replace with actual user ID
    show_analysis_history_page(user_id)

# Streamlit app example
if __name__ == "__main__":
    st.title("Enhanced Analysis System Demo")
    
    tab1, tab2 = st.tabs(["Save Analysis", "View History"])
    
    with tab1:
        st.header("Save Sample Analysis")
        if st.button("Save Sample Analysis"):
            example_save_analysis()
    
    with tab2:
        st.header("Analysis History")
        example_show_history()
