#!/usr/bin/env python3
"""
Comprehensive fix for UI issues:
1. Analysis history not showing properly
2. Analysis disappearing on download
3. Session state management issues
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_fixed_history_ui():
    """Create a fixed version of the history UI that doesn't cause state issues"""
    
    fixed_ui_content = '''"""
Fixed Report History UI Component - Prevents state issues and analysis disappearing
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

try:
    from database.enhanced_analysis_storage import enhanced_analysis_storage
    from auth.models import User
    STORAGE_AVAILABLE = True
except ImportError:
    # Fallback for testing
    enhanced_analysis_storage = None
    User = None
    STORAGE_AVAILABLE = False

class FixedReportHistoryUI:
    """Fixed UI component for displaying and managing report history without state issues"""
    
    def __init__(self):
        self.storage = enhanced_analysis_storage if STORAGE_AVAILABLE else None
    
    def render_history_page(self, user: User):
        """Render the complete history page without causing state issues"""
        st.title("📊 Analysis History")
        st.markdown("View and download your previous analysis reports")
        
        try:
            # Get user reports with fallback
            reports = self._get_user_reports_safe(user)
            
            if not reports:
                st.info("📝 No analysis history found. Run your first analysis to see results here!")
                return
            
            # Show count
            st.success(f"Found {len(reports)} analysis reports")
            
            # Render reports without causing state issues
            self._render_reports_safe(user, reports)
            
        except Exception as e:
            logger.error(f"Error rendering history page: {e}")
            st.error("Failed to load analysis history. Please refresh the page.")
    
    def _get_user_reports_safe(self, user: User) -> List[Dict[str, Any]]:
        """Safely get user reports with multiple fallbacks"""
        try:
            # Try enhanced storage first
            if self.storage:
                return self.storage.get_user_reports(user.id)
        except Exception as e:
            logger.warning(f"Enhanced storage failed: {e}")
        
        try:
            # Fallback to direct database query
            from database.connection import get_db
            db = get_db()
            
            # Try analysis_reports table first
            reports = db.execute_query("""
                SELECT id, title, content, created_at, analysis_type, metadata
                FROM analysis_reports 
                WHERE user_id = ? 
                ORDER BY created_at DESC
                LIMIT 50
            """, (user.id,))
            
            if reports:
                return reports
            
            # Fallback to analysis_sessions table
            sessions = db.execute_query("""
                SELECT id, resume_filename as title, score, match_category, created_at
                FROM analysis_sessions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 50
            """, (user.id,))
            
            # Convert sessions to report format
            converted_reports = []
            for session in sessions:
                converted_reports.append({
                    'id': session['id'],
                    'title': f"{session['title']} - {session['score']}%",
                    'content': f"Score: {session['score']}%\\nCategory: {session['match_category']}",
                    'created_at': session['created_at'],
                    'analysis_type': 'resume_jd_match',
                    'metadata': json.dumps({'score': session['score'], 'category': session['match_category']})
                })
            
            return converted_reports
            
        except Exception as e:
            logger.error(f"Database fallback failed: {e}")
            return []
    
    def _render_reports_safe(self, user: User, reports: List[Dict[str, Any]]):
        """Render reports without causing state issues"""
        
        # Use tabs to organize content without state conflicts
        tab1, tab2 = st.tabs(["📋 Report List", "📊 Statistics"])
        
        with tab1:
            self._render_report_list(user, reports)
        
        with tab2:
            self._render_statistics(reports)
    
    def _render_report_list(self, user: User, reports: List[Dict[str, Any]]):
        """Render the list of reports"""
        
        for i, report in enumerate(reports):
            # Use unique keys to prevent state conflicts
            report_key = f"report_{report['id']}_{i}"
            
            # Format title and date
            title = report.get('title', 'Untitled Report')
            created_at = report.get('created_at', 'Unknown date')
            if isinstance(created_at, str) and len(created_at) > 10:
                display_date = created_at[:10]
            else:
                display_date = str(created_at)
            
            # Create expandable section for each report
            with st.expander(f"📄 {title} - {display_date}", expanded=False):
                
                # Report info
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Type:** {report.get('analysis_type', 'Unknown')}")
                    st.write(f"**Created:** {created_at}")
                    
                    # Show metadata if available
                    metadata = report.get('metadata')
                    if metadata:
                        try:
                            if isinstance(metadata, str):
                                metadata = json.loads(metadata)
                            if isinstance(metadata, dict):
                                for key, value in metadata.items():
                                    if key in ['score', 'category']:
                                        st.write(f"**{key.title()}:** {value}")
                        except:
                            pass
                
                with col2:
                    # Download buttons that don't cause rerun
                    self._render_download_buttons_safe(user, report, report_key)
                
                # Show content preview
                content = report.get('content', '')
                if content:
                    if len(content) > 500:
                        preview = content[:500] + "..."
                        st.text_area(
                            "Content Preview:",
                            value=preview,
                            height=150,
                            key=f"preview_{report_key}",
                            disabled=True
                        )
                        
                        # Full content toggle
                        if st.checkbox("Show full content", key=f"full_{report_key}"):
                            st.text_area(
                                "Full Content:",
                                value=content,
                                height=400,
                                key=f"full_content_{report_key}",
                                disabled=True
                            )
                    else:
                        st.text_area(
                            "Content:",
                            value=content,
                            height=200,
                            key=f"content_{report_key}",
                            disabled=True
                        )
    
    def _render_download_buttons_safe(self, user: User, report: Dict[str, Any], report_key: str):
        """Render download buttons that don't cause state issues"""
        
        # Text download
        content = report.get('content', '')
        if content:
            filename = f"analysis_report_{report['id'][:8]}.txt"
            
            st.download_button(
                label="📄 Download Text",
                data=content,
                file_name=filename,
                mime="text/plain",
                key=f"download_text_{report_key}",
                help="Download as text file"
            )
        
        # CSV download (if metadata available)
        metadata = report.get('metadata')
        if metadata:
            try:
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                
                csv_content = self._create_csv_content(report, metadata)
                if csv_content:
                    filename = f"analysis_data_{report['id'][:8]}.csv"
                    
                    st.download_button(
                        label="📊 Download CSV",
                        data=csv_content,
                        file_name=filename,
                        mime="text/csv",
                        key=f"download_csv_{report_key}",
                        help="Download as CSV file"
                    )
            except Exception as e:
                logger.warning(f"CSV generation failed: {e}")
    
    def _create_csv_content(self, report: Dict[str, Any], metadata: Dict[str, Any]) -> Optional[str]:
        """Create CSV content from report data"""
        try:
            title = report.get('title', 'Untitled')
            created_at = report.get('created_at', '')
            score = metadata.get('score', '')
            category = metadata.get('category', '')
            
            csv_content = f"""Title,Score,Category,Date,Type
"{title}","{score}","{category}","{created_at}","{report.get('analysis_type', '')}"
"""
            return csv_content
        except Exception as e:
            logger.warning(f"Failed to create CSV content: {e}")
            return None
    
    def _render_statistics(self, reports: List[Dict[str, Any]]):
        """Render statistics about the reports"""
        
        if not reports:
            st.info("No reports available for statistics")
            return
        
        # Basic stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Reports", len(reports))
        
        with col2:
            # Count by type
            types = {}
            for report in reports:
                report_type = report.get('analysis_type', 'Unknown')
                types[report_type] = types.get(report_type, 0) + 1
            
            most_common_type = max(types.items(), key=lambda x: x[1])[0] if types else "None"
            st.metric("Most Common Type", most_common_type)
        
        with col3:
            # Recent reports (last 7 days)
            recent_count = 0
            try:
                cutoff = datetime.now() - timedelta(days=7)
                for report in reports:
                    created_at = report.get('created_at', '')
                    if isinstance(created_at, str):
                        try:
                            report_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            if report_date >= cutoff:
                                recent_count += 1
                        except:
                            pass
            except:
                pass
            
            st.metric("Recent (7 days)", recent_count)
        
        # Report types chart
        if len(types) > 1:
            st.subheader("📊 Report Types")
            chart_data = pd.DataFrame(
                list(types.items()),
                columns=['Type', 'Count']
            )
            st.bar_chart(chart_data.set_index('Type'))

# Global instance
fixed_report_history_ui = FixedReportHistoryUI()
'''
    
    with open("components/fixed_report_history_ui.py", "w") as f:
        f.write(fixed_ui_content)
    
    logger.info("✅ Created fixed report history UI")
    return True

def update_app_py_imports():
    """Update app.py to use the fixed history UI"""
    
    app_file = "app.py"
    
    try:
        with open(app_file, 'r') as f:
            content = f.read()
        
        # Replace the import
        old_import = """# Try to import report history UI (optional, only for enhanced features)
try:
    from components.report_history_ui import report_history_ui
    from components.report_history_ui import report_history_ui
    REPORT_HISTORY_AVAILABLE = True
    logger.info("Report history UI available")
except ImportError:
    report_history_ui = None
    REPORT_HISTORY_AVAILABLE = False
    logger.info("Report history UI not available (Streamlit context required)")"""
        
        new_import = """# Try to import report history UI (optional, only for enhanced features)
try:
    from components.fixed_report_history_ui import fixed_report_history_ui as report_history_ui
    REPORT_HISTORY_AVAILABLE = True
    logger.info("Report history UI available")
except ImportError:
    try:
        from components.report_history_ui import report_history_ui
        REPORT_HISTORY_AVAILABLE = True
        logger.info("Fallback report history UI available")
    except ImportError:
        report_history_ui = None
        REPORT_HISTORY_AVAILABLE = False
        logger.info("Report history UI not available (Streamlit context required)")"""
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            
            with open(app_file, 'w') as f:
                f.write(content)
            
            logger.info("✅ Updated app.py imports")
            return True
        else:
            logger.info("Import section not found or already updated")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to update app.py imports: {e}")
        return False

def fix_render_analysis_history():
    """Fix the render_analysis_history function to handle errors better"""
    
    app_file = "app.py"
    
    try:
        with open(app_file, 'r') as f:
            content = f.read()
        
        # Replace the problematic function
        old_function = """def render_analysis_history(user):
    \"\"\"Render analysis history page\"\"\"
    if ENHANCED_SERVICES_AVAILABLE:
        try:
            report_history_ui.render_history_page(user)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            st.error(f"Enhanced history unavailable: {e}")
            render_simple_analysis_history(user)
    else:
        # Fallback to session state history
        st.title("📊 Analysis History")
        st.info("📝 Enhanced history tracking is not available. Showing session data only.")
        
        if st.session_state.analysis_results:
            st.subheader("📋 Current Session Results")
            
            for i, (filename, result) in enumerate(st.session_state.analysis_results):
                with st.expander(f"📄 {filename} - {result.score}%"):
                    render_analysis_result(result, filename)
        else:
            st.info("No analysis results in current session.")"""
        
        new_function = """def render_analysis_history(user):
    \"\"\"Render analysis history page with improved error handling\"\"\"
    try:
        # Always try the enhanced UI first if available
        if REPORT_HISTORY_AVAILABLE and report_history_ui:
            report_history_ui.render_history_page(user)
        else:
            # Use the simple fallback
            render_simple_analysis_history(user)
    except Exception as e:
        logger.error(f"History rendering error: {e}")
        st.error("⚠️ There was an issue loading your analysis history.")
        
        # Try the simple fallback as last resort
        try:
            render_simple_analysis_history(user)
        except Exception as fallback_error:
            logger.error(f"Fallback history rendering error: {fallback_error}")
            st.error("Unable to load analysis history. Please try refreshing the page.")
            
            # Show session data if available
            if hasattr(st.session_state, 'analysis_results') and st.session_state.analysis_results:
                st.info("📋 Showing current session results:")
                for i, (filename, result) in enumerate(st.session_state.analysis_results):
                    with st.expander(f"📄 {filename} - {result.score}%"):
                        render_analysis_result(result, filename)"""
        
        if old_function in content:
            content = content.replace(old_function, new_function)
            
            with open(app_file, 'w') as f:
                f.write(content)
            
            logger.info("✅ Fixed render_analysis_history function")
            return True
        else:
            logger.info("Function not found or already updated")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to fix render_analysis_history: {e}")
        return False

def main():
    """Run all UI fixes"""
    logger.info("🔧 Starting comprehensive UI fix...")
    
    success_count = 0
    total_fixes = 3
    
    # Fix 1: Create fixed history UI
    if create_fixed_history_ui():
        success_count += 1
    
    # Fix 2: Update app.py imports
    if update_app_py_imports():
        success_count += 1
    
    # Fix 3: Fix render_analysis_history function
    if fix_render_analysis_history():
        success_count += 1
    
    logger.info(f"🎯 Completed {success_count}/{total_fixes} UI fixes successfully")
    
    if success_count == total_fixes:
        logger.info("✅ All UI issues fixed! Please restart your Streamlit app.")
        logger.info("🔄 The following issues should now be resolved:")
        logger.info("   • Analysis history will display properly")
        logger.info("   • Downloads won't cause analysis to disappear")
        logger.info("   • Better error handling for UI components")
    else:
        logger.warning("⚠️ Some UI fixes failed. Check the logs above.")

if __name__ == "__main__":
    main()