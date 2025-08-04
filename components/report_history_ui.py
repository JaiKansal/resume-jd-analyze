"""
Report History UI Component
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any

try:
    from database.enhanced_analysis_storage import enhanced_analysis_storage
    from auth.models import User
except ImportError:
    # Fallback for testing
    enhanced_analysis_storage = None
    User = None

class ReportHistoryUI:
    """UI component for displaying and managing report history"""
    
    def __init__(self):
        self.storage = enhanced_analysis_storage
    
    def render_history_page(self, user: User):
        """Render the complete history page"""
        st.title("📊 Analysis History")
        st.markdown("View and download your previous analysis reports")
        
        # Get user analyses
        analyses = self.storage.get_user_analyses(user.id, limit=100)
        
        if not analyses:
            st.info("📝 No analysis history found. Run your first analysis to see results here!")
            return
        
        # Statistics overview
        self.render_statistics_overview(user, analyses)
        
        # Filters
        filtered_analyses = self.render_filters(analyses)
        
        # History table
        self.render_history_table(user, filtered_analyses)
    
    def render_statistics_overview(self, user: User, analyses: List[Dict[str, Any]]):
        """Render statistics overview"""
        st.subheader("📈 Your Analysis Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Analyses", len(analyses))
        
        with col2:
            avg_score = sum(a['score'] for a in analyses) / len(analyses) if analyses else 0
            st.metric("Average Score", f"{avg_score:.1f}%")
        
        with col3:
            best_score = max(a['score'] for a in analyses) if analyses else 0
            st.metric("Best Score", f"{best_score}%")
        
        with col4:
            recent_count = len([a for a in analyses if self._is_recent(a['created_at'])])
            st.metric("This Week", recent_count)
    
    def render_filters(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Render filters and return filtered analyses"""
        st.subheader("🔍 Filter Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Score range filter
            min_score = st.slider("Minimum Score", 0, 100, 0)
            max_score = st.slider("Maximum Score", 0, 100, 100)
        
        with col2:
            # Date range filter
            date_range = st.selectbox(
                "Date Range",
                ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"]
            )
        
        with col3:
            # Match category filter
            categories = list(set(a['match_category'] for a in analyses))
            selected_categories = st.multiselect(
                "Match Categories",
                categories,
                default=categories
            )
        
        # Apply filters
        filtered = analyses
        
        # Score filter
        filtered = [a for a in filtered if min_score <= a['score'] <= max_score]
        
        # Date filter
        if date_range != "All Time":
            days = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}[date_range]
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered = [a for a in filtered if self._parse_date(a['created_at']) >= cutoff_date]
        
        # Category filter
        filtered = [a for a in filtered if a['match_category'] in selected_categories]
        
        st.info(f"Showing {len(filtered)} of {len(analyses)} analyses")
        
        return filtered
    
    def render_history_table(self, user: User, analyses: List[Dict[str, Any]]):
        """Render the history table with download options"""
        st.subheader("📋 Analysis History")
        
        if not analyses:
            st.warning("No analyses match your filters.")
            return
        
        # Create DataFrame for display
        df_data = []
        for analysis in analyses:
            df_data.append({
                'Date': self._format_date(analysis['created_at']),
                'Resume': analysis['resume_filename'] or 'Unknown',
                'Score': f"{analysis['score']}%",
                'Category': analysis['match_category'],
                'Downloads': len(analysis.get('download_history', [])),
                'ID': analysis['id']
            })
        
        df = pd.DataFrame(df_data)
        
        # Display table with selection
        selected_indices = st.dataframe(
            df.drop('ID', axis=1),
            use_container_width=True,
            on_select="rerun",
            selection_mode="multi-row"
        )
        
        # Action buttons for selected analyses
        if selected_indices and hasattr(selected_indices, 'selection') and selected_indices.selection.rows:
            selected_ids = [df.iloc[i]['ID'] for i in selected_indices.selection.rows]
            self.render_bulk_actions(user, selected_ids, analyses)
        
        # Individual analysis details
        with st.expander("📊 View Individual Analysis Details"):
            analysis_id = st.selectbox(
                "Select Analysis",
                options=[a['id'] for a in analyses],
                format_func=lambda x: next(
                    f"{a['resume_filename']} - {a['score']}% ({self._format_date(a['created_at'])})"
                    for a in analyses if a['id'] == x
                )
            )
            
            if analysis_id:
                self.render_analysis_details(user, analysis_id)
    
    def render_bulk_actions(self, user: User, selected_ids: List[str], analyses: List[Dict[str, Any]]):
        """Render bulk actions for selected analyses"""
        st.subheader(f"🎯 Actions for {len(selected_ids)} Selected Analyses")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Download CSV Summary", use_container_width=True):
                self.download_bulk_csv(user, selected_ids, analyses)
        
        with col2:
            if st.button("📄 Download Text Reports", use_container_width=True):
                self.download_bulk_text(user, selected_ids, analyses)
        
        with col3:
            if st.button("🗑️ Delete Selected", use_container_width=True, type="secondary"):
                self.delete_bulk_analyses(user, selected_ids)
    
    def render_analysis_details(self, user: User, analysis_id: str):
        """Render detailed view of a single analysis"""
        analysis = self.storage.get_analysis_by_id(analysis_id, user.id)
        
        if not analysis:
            st.error("Analysis not found")
            return
        
        # Basic info
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Score", f"{analysis['score']}%")
            st.metric("Category", analysis['match_category'])
        
        with col2:
            st.metric("Date", self._format_date(analysis['created_at']))
            processing_time = analysis.get('processing_time_seconds', 0)
            st.metric("Processing Time", f"{processing_time:.2f}s")
        
        # Download history
        if analysis.get('download_history'):
            st.subheader("📥 Download History")
            download_df = pd.DataFrame(analysis['download_history'])
            st.dataframe(download_df, use_container_width=True)
        
        # Re-download options
        st.subheader("📥 Download This Report")
        self.render_individual_download_options(user, analysis)
    
    def render_individual_download_options(self, user: User, analysis: Dict[str, Any]):
        """Render download options for individual analysis"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 CSV", key=f"csv_{analysis['id']}", use_container_width=True):
                self.download_individual_csv(user, analysis)
        
        with col2:
            if st.button("📄 Text", key=f"text_{analysis['id']}", use_container_width=True):
                self.download_individual_text(user, analysis)
        
        with col3:
            if st.button("📑 PDF", key=f"pdf_{analysis['id']}", use_container_width=True):
                self.download_individual_pdf(user, analysis)
    
    def download_individual_csv(self, user: User, analysis: Dict[str, Any]):
        """Download individual analysis as CSV"""
        # Record download
        self.storage.record_download(analysis['id'], user.id, 'individual', 'csv')
        
        # Create CSV data
        result = analysis['analysis_result']
        csv_data = f"""Resume,Score,Category,Date
{analysis['resume_filename']},{analysis['score']},{analysis['match_category']},{self._format_date(analysis['created_at'])}"""
        
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name=f"analysis_{analysis['id'][:8]}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    def download_individual_text(self, user: User, analysis: Dict[str, Any]):
        """Download individual analysis as text report"""
        # Record download
        self.storage.record_download(analysis['id'], user.id, 'individual', 'text')
        
        # Create text report
        result = analysis['analysis_result']
        text_report = f"""RESUME ANALYSIS REPORT
{'='*50}

Resume: {analysis['resume_filename']}
Analysis Date: {self._format_date(analysis['created_at'])}
Compatibility Score: {analysis['score']}%
Match Category: {analysis['match_category']}

ANALYSIS DETAILS:
{'-'*20}
{json.dumps(result, indent=2)}

Generated by Resume + JD Analyzer
"""
        
        st.download_button(
            label="📄 Download Text Report",
            data=text_report,
            file_name=f"report_{analysis['id'][:8]}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )
    
    def _is_recent(self, date_str: str, days: int = 7) -> bool:
        """Check if date is within recent days"""
        try:
            date = self._parse_date(date_str)
            return date >= datetime.now() - timedelta(days=days)
        except:
            return False
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime"""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.now()
    
    def _format_date(self, date_str: str) -> str:
        """Format date for display"""
        try:
            date = self._parse_date(date_str)
            return date.strftime('%Y-%m-%d %H:%M')
        except:
            return date_str

# Global instance
report_history_ui = ReportHistoryUI()
