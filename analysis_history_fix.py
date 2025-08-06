
# Analysis History Display Fix
# Add this to app.py to fix history display issues

def display_analysis_history_fixed():
    """Fixed version of analysis history display"""
    if not st.session_state.get('user_authenticated', False):
        st.info("Please log in to view your analysis history.")
        return
    
    user = st.session_state.get('current_user')
    if not user:
        st.error("User session not found. Please log in again.")
        return
    
    try:
        # Get analysis reports with proper error handling
        if ANALYSIS_STORAGE_AVAILABLE and enhanced_analysis_storage:
            reports = enhanced_analysis_storage.get_user_reports(user.id)
        else:
            # Fallback to direct database query
            from database.connection import get_db
            db = get_db()
            reports = db.execute_query("""
                SELECT id, title, created_at, analysis_type, metadata
                FROM analysis_reports 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            """, (user.id,))
        
        if not reports:
            st.info("📝 No analysis history found. Run your first analysis to see results here!")
            return
        
        st.subheader(f"📊 Analysis History ({len(reports)} reports)")
        
        # Display reports without causing state issues
        for i, report in enumerate(reports):
            with st.expander(f"📄 {report.get('title', 'Untitled Report')} - {report.get('created_at', 'Unknown date')[:10]}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Type:** {report.get('analysis_type', 'Unknown')}")
                    st.write(f"**Created:** {report.get('created_at', 'Unknown')}")
                
                with col2:
                    # View button that doesn't cause rerun
                    if st.button(f"👁️ View", key=f"view_{report['id']}_{i}"):
                        st.session_state[f"show_report_{report['id']}"] = True
                
                with col3:
                    # Download button that doesn't cause rerun
                    if st.button(f"📥 Download", key=f"download_{report['id']}_{i}"):
                        try:
                            # Get full report content
                            if ANALYSIS_STORAGE_AVAILABLE and enhanced_analysis_storage:
                                full_report = enhanced_analysis_storage.get_report(report['id'])
                            else:
                                db = get_db()
                                full_report = db.get_single_result(
                                    "SELECT * FROM analysis_reports WHERE id = ?", 
                                    (report['id'],)
                                )
                            
                            if full_report:
                                # Create download without causing rerun
                                st.download_button(
                                    label="📄 Download Text Report",
                                    data=full_report.get('content', ''),
                                    file_name=f"analysis_report_{report['id'][:8]}.txt",
                                    mime="text/plain",
                                    key=f"download_text_{report['id']}_{i}"
                                )
                            else:
                                st.error("Report content not found")
                        except Exception as e:
                            st.error(f"Download failed: {e}")
                
                # Show report content if requested
                if st.session_state.get(f"show_report_{report['id']}", False):
                    try:
                        if ANALYSIS_STORAGE_AVAILABLE and enhanced_analysis_storage:
                            full_report = enhanced_analysis_storage.get_report(report['id'])
                        else:
                            db = get_db()
                            full_report = db.get_single_result(
                                "SELECT * FROM analysis_reports WHERE id = ?", 
                                (report['id'],)
                            )
                        
                        if full_report:
                            st.text_area(
                                "Report Content:",
                                value=full_report.get('content', ''),
                                height=300,
                                key=f"content_{report['id']}_{i}"
                            )
                        else:
                            st.error("Report content not found")
                    except Exception as e:
                        st.error(f"Failed to load report: {e}")
    
    except Exception as e:
        logger.error(f"Failed to display analysis history: {e}")
        st.error("Failed to load analysis history. Please try again.")
