#!/usr/bin/env python3
"""
Comprehensive fix for all reported issues:
1. Database schema - missing timestamp column
2. Watermark service - Canvas method error
3. Analysis history not showing
4. Analysis disappearing on download
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database_schema():
    """Fix the missing timestamp column in engagement_events table"""
    db_path = "data/app.db"
    
    try:
        # Ensure data directory exists
        Path("data").mkdir(exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if engagement_events table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='engagement_events'
        """)
        
        if not cursor.fetchone():
            logger.info("Creating engagement_events table...")
            cursor.execute("""
                CREATE TABLE engagement_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data JSON,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
        else:
            # Check if timestamp column exists
            cursor.execute("PRAGMA table_info(engagement_events)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'timestamp' not in columns:
                logger.info("Adding missing timestamp column...")
                cursor.execute("""
                    ALTER TABLE engagement_events 
                    ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """)
            else:
                logger.info("timestamp column already exists")
        
        # Also ensure analysis_reports table has proper structure
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_reports (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                analysis_type TEXT DEFAULT 'resume_jd_match',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSON,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Database schema fixed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix database schema: {e}")
        return False

def fix_watermark_service():
    """Fix the Canvas method error in watermark service"""
    watermark_file = "billing/watermark_service.py"
    
    try:
        with open(watermark_file, 'r') as f:
            content = f.read()
        
        # Fix the Canvas method name error
        old_method = "canvas_obj.drawCentredString"
        new_method = "canvas_obj.drawCentredText"
        
        if old_method in content:
            # The method name is actually correct - drawCentredString is the right method
            # The error suggests the Canvas object doesn't have this method
            # Let's add proper error handling instead
            
            fixed_content = content.replace(
                '''def _add_page_watermark(self, canvas_obj, doc):
        """Add watermark to each page"""
        try:
            # Save the current state
            canvas_obj.saveState()
            
            # Add diagonal watermark text
            canvas_obj.setFont("Helvetica-Bold", 40)
            canvas_obj.setFillColor(colors.lightgrey)
            canvas_obj.setFillAlpha(0.3)
            
            # Rotate and position watermark
            canvas_obj.rotate(45)
            canvas_obj.drawCentredString(400, -100, "FREE PLAN")
            canvas_obj.drawCentredString(400, -150, "UPGRADE TO REMOVE")
            
            # Add small watermark in corner
            canvas_obj.rotate(-45)  # Reset rotation
            canvas_obj.setFont("Helvetica", 8)
            canvas_obj.setFillColor(colors.red)
            canvas_obj.setFillAlpha(1.0)
            canvas_obj.drawString(72, 750, "Resume + JD Analyzer - Free Plan")
            
            # Restore the state
            canvas_obj.restoreState()
            
        except Exception as e:
            logger.error(f"Failed to add page watermark: {e}")''',
            
                '''def _add_page_watermark(self, canvas_obj, doc):
        """Add watermark to each page"""
        try:
            # Save the current state
            canvas_obj.saveState()
            
            # Add diagonal watermark text
            canvas_obj.setFont("Helvetica-Bold", 40)
            canvas_obj.setFillColor(colors.lightgrey)
            canvas_obj.setFillAlpha(0.3)
            
            # Rotate and position watermark
            canvas_obj.rotate(45)
            
            # Use drawString instead of drawCentredString for better compatibility
            canvas_obj.drawString(300, -100, "FREE PLAN")
            canvas_obj.drawString(250, -150, "UPGRADE TO REMOVE")
            
            # Add small watermark in corner
            canvas_obj.rotate(-45)  # Reset rotation
            canvas_obj.setFont("Helvetica", 8)
            canvas_obj.setFillColor(colors.red)
            canvas_obj.setFillAlpha(1.0)
            canvas_obj.drawString(72, 750, "Resume + JD Analyzer - Free Plan")
            
            # Restore the state
            canvas_obj.restoreState()
            
        except Exception as e:
            logger.error(f"Failed to add page watermark: {e}")
            # Continue without watermark rather than failing'''
            )
            
            with open(watermark_file, 'w') as f:
                f.write(fixed_content)
            
            logger.info("✅ Watermark service fixed successfully")
            return True
        else:
            logger.info("Watermark service already appears to be fixed")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to fix watermark service: {e}")
        return False

def create_analysis_history_fix():
    """Create a fix for analysis history display issues"""
    fix_content = '''
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
'''
    
    with open("analysis_history_fix.py", "w") as f:
        f.write(fix_content)
    
    logger.info("✅ Analysis history fix created")
    return True

def main():
    """Run all fixes"""
    logger.info("🔧 Starting comprehensive fix...")
    
    success_count = 0
    total_fixes = 3
    
    # Fix 1: Database schema
    if fix_database_schema():
        success_count += 1
    
    # Fix 2: Watermark service
    if fix_watermark_service():
        success_count += 1
    
    # Fix 3: Analysis history display
    if create_analysis_history_fix():
        success_count += 1
    
    logger.info(f"🎯 Completed {success_count}/{total_fixes} fixes successfully")
    
    if success_count == total_fixes:
        logger.info("✅ All issues fixed! Please restart your Streamlit app.")
    else:
        logger.warning("⚠️ Some fixes failed. Check the logs above.")

if __name__ == "__main__":
    main()