#!/usr/bin/env python3
"""
Analysis History UI
User interface for viewing and managing saved analyses
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Optional
import json

from analysis.enhanced_analysis_service import enhanced_analysis_service, AnalysisResult

def render_analysis_history(user_id: str):
    """Render the analysis history page"""
    st.header("📊 Your Analysis History")
    
    # Get user analyses
    analyses = enhanced_analysis_service.get_user_analyses(user_id, limit=100)
    
    if not analyses:
        st.info("🔍 No analyses found. Start by uploading a resume and job description!")
        return
    
    # Display stats
    stats = enhanced_analysis_service.get_user_analysis_stats(user_id)
    render_analysis_stats(stats)
    
    # Display analyses
    render_analyses_table(analyses, user_id)

def render_analysis_stats(stats: dict):
    """Render analysis statistics"""
    if not stats:
        return
    
    st.subheader("📈 Your Analysis Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analyses", stats.get('total_analyses', 0))
    
    with col2:
        avg_score = stats.get('avg_match_score', 0)
        st.metric("Average Match Score", f"{avg_score:.1f}%")
    
    with col3:
        best_score = stats.get('best_match_score', 0)
        st.metric("Best Match Score", f"{best_score:.1f}%")
    
    with col4:
        completed = stats.get('completed_analyses', 0)
        total = stats.get('total_analyses', 0)
        success_rate = (completed / total * 100) if total > 0 else 0
        st.metric("Success Rate", f"{success_rate:.1f}%")

def render_analyses_table(analyses: List[AnalysisResult], user_id: str):
    """Render the analyses table with actions"""
    st.subheader("📋 Analysis History")
    
    # Create DataFrame for display
    data = []
    for analysis in analyses:
        data.append({
            'Date': analysis.created_at.strftime('%Y-%m-%d %H:%M') if analysis.created_at else 'Unknown',
            'Resume': analysis.resume_filename or 'Unknown',
            'Match Score': f"{analysis.match_score:.1f}%" if analysis.match_score else 'N/A',
            'Status': analysis.status.title(),
            'Analysis ID': analysis.id
        })
    
    df = pd.DataFrame(data)
    
    # Display table
    st.dataframe(
        df[['Date', 'Resume', 'Match Score', 'Status']], 
        use_container_width=True,
        hide_index=True
    )
    
    # Analysis selection and actions
    st.subheader("🔍 View Analysis Details")
    
    # Create selectbox with analysis options
    analysis_options = {
        f"{analysis.resume_filename} - {analysis.created_at.strftime('%Y-%m-%d %H:%M') if analysis.created_at else 'Unknown'} ({analysis.match_score:.1f}%)": analysis.id
        for analysis in analyses
    }
    
    selected_analysis_key = st.selectbox(
        "Select an analysis to view details:",
        options=list(analysis_options.keys()),
        index=0 if analysis_options else None
    )
    
    if selected_analysis_key and analysis_options:
        selected_analysis_id = analysis_options[selected_analysis_key]
        render_analysis_details(selected_analysis_id, user_id)

def render_analysis_details(analysis_id: str, user_id: str):
    """Render detailed view of a specific analysis"""
    analysis = enhanced_analysis_service.get_analysis_by_id(analysis_id)
    
    if not analysis:
        st.error("❌ Analysis not found!")
        return
    
    # Verify user ownership
    if analysis.user_id != user_id:
        st.error("❌ Unauthorized access!")
        return
    
    st.subheader(f"📄 Analysis Details: {analysis.resume_filename}")
    
    # Basic info
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Date:** {analysis.created_at.strftime('%Y-%m-%d %H:%M:%S') if analysis.created_at else 'Unknown'}")
        st.write(f"**Match Score:** {analysis.match_score:.1f}%")
        st.write(f"**Status:** {analysis.status.title()}")
    
    with col2:
        st.write(f"**Analysis Type:** {analysis.analysis_type}")
        if analysis.processing_time_seconds:
            st.write(f"**Processing Time:** {analysis.processing_time_seconds:.2f}s")
        if analysis.tokens_used:
            st.write(f"**Tokens Used:** {analysis.tokens_used:,}")
    
    # Detailed analysis results
    tabs = st.tabs(["📊 Summary", "💪 Strengths", "⚠️ Weaknesses", "💡 Recommendations", "🔑 Keywords", "📄 Content"])
    
    with tabs[0]:  # Summary
        render_analysis_summary(analysis)
    
    with tabs[1]:  # Strengths
        render_analysis_strengths(analysis)
    
    with tabs[2]:  # Weaknesses
        render_analysis_weaknesses(analysis)
    
    with tabs[3]:  # Recommendations
        render_analysis_recommendations(analysis)
    
    with tabs[4]:  # Keywords
        render_analysis_keywords(analysis)
    
    with tabs[5]:  # Content
        render_analysis_content(analysis)
    
    # Action buttons
    st.subheader("🔧 Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Download PDF Report", key=f"download_{analysis_id}"):
            handle_pdf_download(analysis)
    
    with col2:
        if st.button("🔄 Re-run Analysis", key=f"rerun_{analysis_id}"):
            handle_analysis_rerun(analysis)
    
    with col3:
        if st.button("🗑️ Delete Analysis", key=f"delete_{analysis_id}", type="secondary"):
            handle_analysis_deletion(analysis_id, user_id)

def render_analysis_summary(analysis: AnalysisResult):
    """Render analysis summary"""
    st.write("### 📊 Analysis Summary")
    
    # Match score visualization
    score = analysis.match_score
    if score >= 80:
        color = "green"
        emoji = "🎯"
    elif score >= 60:
        color = "orange"
        emoji = "⚡"
    else:
        color = "red"
        emoji = "🔧"
    
    st.markdown(f"""
    <div style="padding: 20px; border-radius: 10px; background-color: {color}20; border-left: 5px solid {color};">
        <h3>{emoji} Match Score: {score:.1f}%</h3>
        <p>Your resume shows a <strong>{score:.1f}%</strong> match with the job requirements.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Strengths Found", len(analysis.strengths))
    
    with col2:
        st.metric("Areas to Improve", len(analysis.weaknesses))
    
    with col3:
        st.metric("Recommendations", len(analysis.recommendations))

def render_analysis_strengths(analysis: AnalysisResult):
    """Render analysis strengths"""
    st.write("### 💪 Your Strengths")
    
    if analysis.strengths:
        for i, strength in enumerate(analysis.strengths, 1):
            st.write(f"**{i}.** {strength}")
    else:
        st.info("No specific strengths identified in this analysis.")

def render_analysis_weaknesses(analysis: AnalysisResult):
    """Render analysis weaknesses"""
    st.write("### ⚠️ Areas for Improvement")
    
    if analysis.weaknesses:
        for i, weakness in enumerate(analysis.weaknesses, 1):
            st.write(f"**{i}.** {weakness}")
    else:
        st.success("No significant weaknesses identified!")

def render_analysis_recommendations(analysis: AnalysisResult):
    """Render analysis recommendations"""
    st.write("### 💡 Recommendations")
    
    if analysis.recommendations:
        for i, recommendation in enumerate(analysis.recommendations, 1):
            st.write(f"**{i}.** {recommendation}")
    else:
        st.info("No specific recommendations available.")

def render_analysis_keywords(analysis: AnalysisResult):
    """Render keyword analysis"""
    st.write("### 🔑 Keyword Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**✅ Keywords Matched:**")
        if analysis.keywords_matched:
            for keyword in analysis.keywords_matched:
                st.write(f"• {keyword}")
        else:
            st.info("No matched keywords recorded.")
    
    with col2:
        st.write("**❌ Keywords Missing:**")
        if analysis.keywords_missing:
            for keyword in analysis.keywords_missing:
                st.write(f"• {keyword}")
        else:
            st.success("No missing keywords identified!")

def render_analysis_content(analysis: AnalysisResult):
    """Render original content"""
    st.write("### 📄 Original Content")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Resume Content:**")
        if analysis.resume_content:
            with st.expander("View Resume Content"):
                st.text_area("Resume", analysis.resume_content, height=300, disabled=True)
        else:
            st.info("Resume content not saved.")
    
    with col2:
        st.write("**Job Description:**")
        if analysis.job_description:
            with st.expander("View Job Description"):
                st.text_area("Job Description", analysis.job_description, height=300, disabled=True)
        else:
            st.info("Job description not saved.")

def handle_pdf_download(analysis: AnalysisResult):
    """Handle PDF report download"""
    if analysis.pdf_report_path:
        st.success("📥 PDF report download would start here!")
        # TODO: Implement actual PDF download
    else:
        st.warning("⚠️ PDF report not available for this analysis.")

def handle_analysis_rerun(analysis: AnalysisResult):
    """Handle analysis re-run"""
    st.info("🔄 Analysis re-run functionality would be implemented here!")
    # TODO: Implement analysis re-run

def handle_analysis_deletion(analysis_id: str, user_id: str):
    """Handle analysis deletion"""
    if st.button("⚠️ Confirm Deletion", key=f"confirm_delete_{analysis_id}"):
        if enhanced_analysis_service.delete_analysis(analysis_id, user_id):
            st.success("✅ Analysis deleted successfully!")
            st.rerun()
        else:
            st.error("❌ Failed to delete analysis!")

# Export function for use in main app
def show_analysis_history_page(user_id: str):
    """Main function to show analysis history page"""
    render_analysis_history(user_id)