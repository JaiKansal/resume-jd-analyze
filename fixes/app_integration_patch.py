"""
App Integration Patch for Payment and Report Fixes
Add this to your app.py imports and initialization
"""

# Add these imports at the top of app.py
from billing.enhanced_razorpay_service import enhanced_razorpay_service
from database.enhanced_analysis_storage import enhanced_analysis_storage
from components.report_history_ui import report_history_ui

# Add this function to check payment system status
def check_payment_system_status():
    """Check and display payment system status"""
    status_info = enhanced_razorpay_service.get_status_info()
    
    if status_info['status'] != 'connected':
        st.sidebar.warning("⚠️ Payment system needs configuration")
        
        with st.sidebar.expander("🔧 Payment System Status"):
            enhanced_razorpay_service.render_status_debug()

# Add this to your main navigation function
def render_navigation_with_history(user):
    """Enhanced navigation with history page"""
    
    # Check payment system
    check_payment_system_status()
    
    # Navigation
    page = st.sidebar.selectbox(
        "Navigate",
        ["🏠 Home", "📊 Single Analysis", "📁 Bulk Analysis", 
         "📋 Analysis History", "👤 Dashboard", "⚙️ Settings"]
    )
    
    if page == "📋 Analysis History":
        report_history_ui.render_history_page(user)
        return "history"
    
    return page

# Add this function to save analysis with enhanced storage
def save_analysis_with_history(user_id: str, resume_filename: str, resume_content: str,
                              job_description: str, analysis_result: dict, 
                              processing_time: float = 0):
    """Save analysis with enhanced storage and history tracking"""
    
    analysis_id = enhanced_analysis_storage.save_analysis(
        user_id=user_id,
        resume_filename=resume_filename,
        resume_content=resume_content,
        job_description=job_description,
        analysis_result=analysis_result,
        processing_time=processing_time
    )
    
    if analysis_id:
        st.success("✅ Analysis saved to your history!")
        
        # Show quick stats
        with st.expander("📊 Your Analysis Stats"):
            stats = enhanced_analysis_storage.get_user_statistics(user_id)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Analyses", stats.get('total_analyses', 0))
            with col2:
                st.metric("Average Score", f"{stats.get('avg_score', 0):.1f}%")
            with col3:
                st.metric("Best Score", f"{stats.get('best_score', 0)}%")
    
    return analysis_id

# Add this to your download button handlers
def enhanced_download_with_tracking(user_id: str, analysis_id: str, report_type: str, 
                                  report_format: str, report_data: str, filename: str):
    """Enhanced download with tracking"""
    
    # Record the download
    enhanced_analysis_storage.record_download(analysis_id, user_id, report_type, report_format)
    
    # Provide download button
    st.download_button(
        label=f"📥 Download {report_format.upper()}",
        data=report_data,
        file_name=filename,
        mime=f"text/{report_format}" if report_format in ['csv', 'plain'] else f"application/{report_format}"
    )
    
    st.success(f"✅ {report_format.upper()} report ready for download!")
    st.info("💡 This report is saved in your Analysis History for future access.")

# Usage example in your analysis function:
def process_analysis_with_history(user, resume_file, job_description):
    """Process analysis with history tracking"""
    
    # Your existing analysis code here...
    # result = analyze_resume(resume_content, job_description)
    
    # Save to history
    analysis_id = save_analysis_with_history(
        user_id=user.id,
        resume_filename=resume_file.name,
        resume_content=resume_content,
        job_description=job_description,
        analysis_result=result,
        processing_time=processing_time
    )
    
    # Enhanced download options
    if analysis_id:
        enhanced_download_with_tracking(
            user_id=user.id,
            analysis_id=analysis_id,
            report_type='individual',
            report_format='csv',
            report_data=create_csv_report(result),
            filename=f"analysis_{analysis_id[:8]}.csv"
        )
