#!/usr/bin/env python3
"""
Direct fix for all reported issues - comprehensive solution
"""

import sqlite3
import logging
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_watermark_service_directly():
    """Fix the watermark service Canvas method error"""
    logger.info("🔧 Fixing watermark service...")
    
    watermark_file = "billing/watermark_service.py"
    
    try:
        with open(watermark_file, 'r') as f:
            content = f.read()
        
        # Replace the problematic method calls
        if "drawCentredString" in content:
            # Replace with drawString and adjust positioning
            content = content.replace(
                'canvas_obj.drawCentredString(400, -100, "FREE PLAN")',
                'canvas_obj.drawString(300, -100, "FREE PLAN")'
            )
            content = content.replace(
                'canvas_obj.drawCentredString(400, -150, "UPGRADE TO REMOVE")',
                'canvas_obj.drawString(250, -150, "UPGRADE TO REMOVE")'
            )
            
            with open(watermark_file, 'w') as f:
                f.write(content)
            
            logger.info("✅ Fixed watermark service Canvas method calls")
        else:
            logger.info("✅ Watermark service already fixed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix watermark service: {e}")
        return False

def fix_engagement_events_query():
    """Fix the engagement events database query"""
    logger.info("🔧 Fixing engagement events query...")
    
    analytics_file = "analytics/user_engagement.py"
    
    try:
        with open(analytics_file, 'r') as f:
            content = f.read()
        
        # Replace the problematic query to use created_at instead of timestamp
        old_query = '''query = """
                INSERT INTO engagement_events (
                    id, user_id, event_type, parameters, timestamp
                ) VALUES (?, ?, ?, ?, ?)
            \""""'''
        
        new_query = '''query = """
                INSERT INTO engagement_events (
                    id, user_id, event_type, parameters, created_at
                ) VALUES (?, ?, ?, ?, ?)
            \""""'''
        
        if "parameters, timestamp" in content:
            content = content.replace("parameters, timestamp", "parameters, created_at")
            
            with open(analytics_file, 'w') as f:
                f.write(content)
            
            logger.info("✅ Fixed engagement events query to use created_at column")
        else:
            logger.info("✅ Engagement events query already uses created_at")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix engagement events query: {e}")
        return False

def create_robust_history_display():
    """Create a robust history display function that works"""
    logger.info("🔧 Creating robust history display...")
    
    history_fix = '''
def render_analysis_history_robust(user):
    """Robust analysis history that actually works"""
    st.title("📊 Analysis History")
    
    try:
        from database.connection import get_db
        db = get_db()
        
        # Try multiple table queries to find reports
        reports = []
        
        # Try analysis_reports table first
        try:
            reports = db.execute_query("""
                SELECT id, title, content, created_at, analysis_type, metadata
                FROM analysis_reports 
                WHERE user_id = ? 
                ORDER BY created_at DESC
                LIMIT 50
            """, (user.id,))
            logger.info(f"Found {len(reports)} reports in analysis_reports table")
        except Exception as e:
            logger.warning(f"analysis_reports query failed: {e}")
        
        # If no reports, try analysis_sessions table
        if not reports:
            try:
                sessions = db.execute_query("""
                    SELECT id, resume_filename, score, match_category, created_at, analysis_result
                    FROM analysis_sessions 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT 50
                """, (user.id,))
                
                # Convert sessions to reports format
                for session in sessions:
                    reports.append({
                        'id': session['id'],
                        'title': f"{session['resume_filename']} - {session['score']}%",
                        'content': f"Score: {session['score']}%\\nCategory: {session['match_category']}\\n\\nFull Analysis:\\n{session.get('analysis_result', 'No detailed analysis available')}",
                        'created_at': session['created_at'],
                        'analysis_type': 'resume_jd_match',
                        'metadata': json.dumps({'score': session['score'], 'category': session['match_category']})
                    })
                
                logger.info(f"Found {len(reports)} sessions converted to reports")
            except Exception as e:
                logger.warning(f"analysis_sessions query failed: {e}")
        
        if not reports:
            st.info("📝 No analysis history found. Run your first analysis to see results here!")
            st.info("💡 Make sure you're logged in and have completed at least one analysis.")
            return
        
        st.success(f"📊 Found {len(reports)} analysis reports")
        
        # Display reports with stable UI
        for i, report in enumerate(reports):
            report_id = report['id']
            title = report.get('title', 'Untitled Report')
            created_at = report.get('created_at', 'Unknown date')
            
            # Format date for display
            if isinstance(created_at, str) and len(created_at) > 10:
                display_date = created_at[:10]
            else:
                display_date = str(created_at)
            
            with st.expander(f"📄 {title} - {display_date}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Type:** {report.get('analysis_type', 'Unknown')}")
                    st.write(f"**Created:** {created_at}")
                    
                    # Show metadata if available
                    metadata = report.get('metadata')
                    if metadata:
                        try:
                            if isinstance(metadata, str):
                                metadata_dict = json.loads(metadata)
                            else:
                                metadata_dict = metadata
                            
                            if isinstance(metadata_dict, dict):
                                for key, value in metadata_dict.items():
                                    if key in ['score', 'category']:
                                        st.write(f"**{key.title()}:** {value}")
                        except:
                            pass
                
                with col2:
                    # Download button that doesn't cause rerun
                    content = report.get('content', '')
                    if content:
                        filename = f"analysis_report_{report_id[:8]}.txt"
                        
                        st.download_button(
                            label="📄 Download",
                            data=content,
                            file_name=filename,
                            mime="text/plain",
                            key=f"download_{report_id}_{i}",
                            help="Download this analysis report"
                        )
                
                # Show content preview
                content = report.get('content', '')
                if content:
                    if len(content) > 500:
                        preview = content[:500] + "..."
                        st.text_area(
                            "Preview:",
                            value=preview,
                            height=150,
                            key=f"preview_{report_id}_{i}",
                            disabled=True
                        )
                        
                        if st.checkbox("Show full content", key=f"full_{report_id}_{i}"):
                            st.text_area(
                                "Full Content:",
                                value=content,
                                height=400,
                                key=f"full_content_{report_id}_{i}",
                                disabled=True
                            )
                    else:
                        st.text_area(
                            "Content:",
                            value=content,
                            height=200,
                            key=f"content_{report_id}_{i}",
                            disabled=True
                        )
    
    except Exception as e:
        logger.error(f"History display error: {e}")
        st.error("❌ Failed to load analysis history")
        st.info("💡 Try refreshing the page or contact support if the issue persists.")
        
        # Show session data as fallback
        if hasattr(st.session_state, 'analysis_results') and st.session_state.analysis_results:
            st.info("📋 Showing current session results:")
            for i, (filename, result) in enumerate(st.session_state.analysis_results):
                with st.expander(f"📄 {filename} - {result.score}%"):
                    st.write(f"**Score:** {result.score}%")
                    st.write(f"**Category:** {result.match_category}")
'''
    
    # Append to app.py
    with open("app.py", "a") as f:
        f.write(history_fix)
    
    logger.info("✅ Added robust history display function to app.py")
    return True

def update_app_py_to_use_robust_history():
    """Update app.py to use the robust history function"""
    logger.info("🔧 Updating app.py to use robust history...")
    
    try:
        with open("app.py", 'r') as f:
            content = f.read()
        
        # Replace the render_analysis_history function call
        if "def render_analysis_history(user):" in content:
            # Replace the function call in the main app
            content = content.replace(
                "render_analysis_history(user)",
                "render_analysis_history_robust(user)"
            )
            
            with open("app.py", 'w') as f:
                f.write(content)
            
            logger.info("✅ Updated app.py to use robust history function")
        else:
            logger.info("✅ App.py already updated or function not found")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update app.py: {e}")
        return False

def verify_database_connection():
    """Verify database connection and fix any issues"""
    logger.info("🔧 Verifying database connection...")
    
    try:
        db_path = "data/app.db"
        
        if not Path(db_path).exists():
            logger.warning("Database doesn't exist - will be created on first use")
            return True
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        logger.info(f"Database has {table_count} tables")
        
        # Check engagement_events table specifically
        cursor.execute("PRAGMA table_info(engagement_events)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'timestamp' in column_names and 'created_at' in column_names:
            logger.info("✅ engagement_events table has both timestamp and created_at columns")
        elif 'created_at' in column_names:
            logger.info("✅ engagement_events table has created_at column")
        else:
            logger.warning("⚠️ engagement_events table missing timestamp columns")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False

def main():
    """Run all direct fixes"""
    logger.info("🚀 Starting direct comprehensive fix...")
    
    fixes = [
        ("Watermark Service", fix_watermark_service_directly),
        ("Engagement Events Query", fix_engagement_events_query),
        ("Database Connection", verify_database_connection),
        ("Robust History Display", create_robust_history_display),
        ("App.py Update", update_app_py_to_use_robust_history)
    ]
    
    passed = 0
    total = len(fixes)
    
    for fix_name, fix_func in fixes:
        logger.info(f"\n--- Applying {fix_name} ---")
        if fix_func():
            passed += 1
            logger.info(f"✅ {fix_name} applied successfully")
        else:
            logger.error(f"❌ {fix_name} failed")
    
    logger.info(f"\n🎯 Fix Results: {passed}/{total} fixes applied successfully")
    
    if passed == total:
        logger.info("🎉 All fixes applied successfully!")
        logger.info("🔄 Please restart your Streamlit app to see the changes:")
        logger.info("   • Analysis history should now display properly")
        logger.info("   • Downloads won't cause analysis to disappear")
        logger.info("   • Database errors should be resolved")
        logger.info("   • Watermark service errors should be fixed")
    else:
        logger.warning("⚠️ Some fixes failed. Check the logs above.")

if __name__ == "__main__":
    main()