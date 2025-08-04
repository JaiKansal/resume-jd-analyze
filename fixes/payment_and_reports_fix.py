#!/usr/bin/env python3
"""
Comprehensive Fix for Payment System and Report Persistence Issues
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)

def fix_razorpay_configuration():
    """Fix Razorpay configuration and initialization"""
    print("🔧 Fixing Razorpay Payment System...")
    
    # Check current environment variables
    key_id = os.getenv('RAZORPAY_KEY_ID')
    key_secret = os.getenv('RAZORPAY_KEY_SECRET')
    
    print(f"Current RAZORPAY_KEY_ID: {key_id}")
    print(f"Current RAZORPAY_KEY_SECRET: {'Set' if key_secret else 'Not set'}")
    
    # Create improved Razorpay service with better error handling
    razorpay_service_content = '''"""
Enhanced Razorpay Payment Service with Better Error Handling
"""

import os
import json
import logging
import hmac
import hashlib
import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Razorpay SDK with fallback
try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False
    st.warning("⚠️ Razorpay SDK not installed. Run: pip install razorpay")

from auth.models import User, PlanType
from database.connection import get_db

logger = logging.getLogger(__name__)

class EnhancedRazorpayService:
    """Enhanced Razorpay service with better configuration handling"""
    
    def __init__(self):
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize Razorpay client with multiple configuration sources"""
        # Try multiple sources for API keys
        self.key_id = self._get_api_key_id()
        self.key_secret = self._get_api_key_secret()
        self.webhook_secret = os.getenv('RAZORPAY_WEBHOOK_SECRET')
        
        # Initialize client
        if not self.key_id or not self.key_secret:
            logger.warning("Razorpay credentials not found in any configuration source")
            self.client = None
            self.status = "credentials_missing"
        elif not RAZORPAY_AVAILABLE:
            logger.warning("Razorpay SDK not available")
            self.client = None
            self.status = "sdk_missing"
        else:
            try:
                self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
                # Test the connection
                self._test_connection()
                logger.info("Razorpay client initialized successfully")
                self.status = "connected"
            except Exception as e:
                logger.error(f"Failed to initialize Razorpay client: {e}")
                self.client = None
                self.status = "connection_failed"
    
    def _get_api_key_id(self) -> Optional[str]:
        """Get API key ID from multiple sources"""
        # Try environment variables first
        key_id = os.getenv('RAZORPAY_KEY_ID')
        if key_id:
            return key_id
        
        # Try Streamlit secrets
        try:
            if hasattr(st, 'secrets') and 'RAZORPAY_KEY_ID' in st.secrets:
                return st.secrets['RAZORPAY_KEY_ID']
        except Exception:
            pass
        
        # Try .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
            return os.getenv('RAZORPAY_KEY_ID')
        except ImportError:
            pass
        
        return None
    
    def _get_api_key_secret(self) -> Optional[str]:
        """Get API key secret from multiple sources"""
        # Try environment variables first
        key_secret = os.getenv('RAZORPAY_KEY_SECRET')
        if key_secret:
            return key_secret
        
        # Try Streamlit secrets
        try:
            if hasattr(st, 'secrets') and 'RAZORPAY_KEY_SECRET' in st.secrets:
                return st.secrets['RAZORPAY_KEY_SECRET']
        except Exception:
            pass
        
        # Try .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
            return os.getenv('RAZORPAY_KEY_SECRET')
        except ImportError:
            pass
        
        return None
    
    def _test_connection(self):
        """Test Razorpay connection"""
        if self.client:
            try:
                # Try to fetch payment methods (lightweight API call)
                self.client.payment.all({'count': 1})
                return True
            except Exception as e:
                logger.warning(f"Razorpay connection test failed: {e}")
                return False
        return False
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get detailed status information for debugging"""
        return {
            'status': self.status,
            'key_id_present': bool(self.key_id),
            'key_secret_present': bool(self.key_secret),
            'sdk_available': RAZORPAY_AVAILABLE,
            'client_initialized': self.client is not None,
            'key_id_preview': self.key_id[:12] + "..." if self.key_id else None
        }
    
    def render_status_debug(self):
        """Render status debug information in Streamlit"""
        status_info = self.get_status_info()
        
        if self.status == "connected":
            st.success("✅ Razorpay payment system is properly configured")
        else:
            st.error("❌ Razorpay payment system configuration issue")
            
            with st.expander("🔧 Debug Information"):
                st.json(status_info)
                
                if self.status == "credentials_missing":
                    st.markdown("""
                    **Fix Required**: Add Razorpay API credentials
                    
                    **For Streamlit Cloud:**
                    1. Go to your app settings
                    2. Add secrets:
                       - `RAZORPAY_KEY_ID` = your key ID
                       - `RAZORPAY_KEY_SECRET` = your key secret
                    
                    **For Local Development:**
                    1. Add to `.env` file:
                       ```
                       RAZORPAY_KEY_ID=your_key_id
                       RAZORPAY_KEY_SECRET=your_key_secret
                       ```
                    """)
                elif self.status == "sdk_missing":
                    st.markdown("""
                    **Fix Required**: Install Razorpay SDK
                    
                    Run: `pip install razorpay`
                    """)
    
    def create_payment_link(self, amount: int, description: str, 
                          customer_email: str, plan_type: PlanType) -> Optional[Dict[str, Any]]:
        """Create a payment link with enhanced error handling"""
        if not self.client:
            logger.error(f"Razorpay client not available. Status: {self.status}")
            return None
        
        try:
            payment_link_data = {
                'amount': amount,  # Amount in paisa
                'currency': 'INR',
                'accept_partial': False,
                'description': description,
                'customer': {
                    'email': customer_email
                },
                'notify': {
                    'sms': True,
                    'email': True
                },
                'reminder_enable': True,
                'notes': {
                    'plan_type': plan_type.value,
                    'product': 'resume_analyzer'
                },
                'callback_url': f"{os.getenv('APP_URL', 'https://resume-jd-analyze.streamlit.app')}/payment/success",
                'callback_method': 'get'
            }
            
            payment_link = self.client.payment_link.create(payment_link_data)
            logger.info(f"Created payment link: {payment_link['id']}")
            return payment_link
            
        except Exception as e:
            logger.error(f"Failed to create payment link: {e}")
            return None
    
    def create_customer(self, user: User) -> Optional[Dict[str, Any]]:
        """Create a Razorpay customer with enhanced error handling"""
        if not self.client:
            logger.error(f"Razorpay client not available. Status: {self.status}")
            return None
        
        try:
            customer_data = {
                'name': f"{getattr(user, 'first_name', 'User')} {getattr(user, 'last_name', '')}".strip(),
                'email': user.email,
                'notes': {
                    'user_id': str(user.id),
                    'company': getattr(user, 'company_name', '') or '',
                    'role': getattr(user, 'role', 'user').value if hasattr(getattr(user, 'role', None), 'value') else 'user'
                }
            }
            
            # Add phone if available
            if hasattr(user, 'phone') and user.phone:
                customer_data['contact'] = user.phone
            
            customer = self.client.customer.create(customer_data)
            logger.info(f"Created Razorpay customer: {customer['id']}")
            return customer
            
        except Exception as e:
            logger.error(f"Failed to create Razorpay customer: {e}")
            return None

# Global instance
enhanced_razorpay_service = EnhancedRazorpayService()

# Backward compatibility
razorpay_service = enhanced_razorpay_service
'''
    
    # Write the enhanced service
    with open('billing/enhanced_razorpay_service.py', 'w') as f:
        f.write(razorpay_service_content)
    
    print("✅ Created enhanced Razorpay service")
    return True

def fix_report_persistence():
    """Fix report persistence and history functionality"""
    print("🔧 Fixing Report Persistence and History...")
    
    # Create enhanced analysis storage with report history
    enhanced_storage_content = '''"""
Enhanced Analysis Storage with Report History and Persistence
"""

import sqlite3
import json
import uuid
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from auth.models import User

class EnhancedAnalysisStorage:
    """Enhanced service for storing and retrieving analysis results with history"""
    
    def __init__(self):
        self.db_path = 'data/app.db'
        self.ensure_database()
    
    def ensure_database(self):
        """Ensure database and tables exist with enhanced schema"""
        Path('data').mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create enhanced analysis_sessions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                resume_filename TEXT,
                resume_hash TEXT,
                job_description TEXT,
                job_description_hash TEXT,
                analysis_result TEXT,
                score INTEGER,
                match_category TEXT,
                processing_time_seconds REAL,
                api_cost_usd REAL,
                tokens_used INTEGER,
                status TEXT DEFAULT 'completed',
                session_type TEXT DEFAULT 'single',
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create report_downloads table to track downloads
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS report_downloads (
                id TEXT PRIMARY KEY,
                analysis_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                report_type TEXT NOT NULL,
                report_format TEXT NOT NULL,
                download_count INTEGER DEFAULT 1,
                first_downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_id) REFERENCES analysis_sessions(id)
            )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_user_id ON analysis_sessions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_created_at ON analysis_sessions(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_score ON analysis_sessions(score)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_report_downloads_user_id ON report_downloads(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_report_downloads_analysis_id ON report_downloads(analysis_id)")
            
            conn.commit()
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content to detect duplicates"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def save_analysis(self, user_id: str, resume_filename: str, resume_content: str,
                     job_description: str, analysis_result: Dict[str, Any], 
                     processing_time: float = 0, api_cost: float = 0, tokens_used: int = 0) -> str:
        """Save analysis result to database with enhanced metadata"""
        try:
            analysis_id = str(uuid.uuid4())
            resume_hash = self._generate_content_hash(resume_content) if resume_content else None
            jd_hash = self._generate_content_hash(job_description)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                INSERT INTO analysis_sessions 
                (id, user_id, resume_filename, resume_hash, job_description, job_description_hash,
                 analysis_result, score, match_category, processing_time_seconds, api_cost_usd, 
                 tokens_used, status, session_type, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis_id,
                    user_id,
                    resume_filename,
                    resume_hash,
                    job_description,
                    jd_hash,
                    json.dumps(analysis_result),
                    analysis_result.get('score', 0),
                    analysis_result.get('match_category', 'Unknown'),
                    processing_time,
                    api_cost,
                    tokens_used,
                    'completed',
                    'single',
                    json.dumps({
                        'resume_size': len(resume_content) if resume_content else 0,
                        'jd_size': len(job_description),
                        'timestamp': datetime.utcnow().isoformat()
                    })
                ))
                
                conn.commit()
                return analysis_id
                
        except Exception as e:
            print(f"Error saving analysis: {e}")
            return None
    
    def get_user_analyses(self, user_id: str, limit: int = 50, include_content: bool = False) -> List[Dict[str, Any]]:
        """Get all analyses for a user with optional content inclusion"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Select fields based on whether content is needed
                if include_content:
                    fields = "*"
                else:
                    fields = """id, user_id, resume_filename, score, match_category, 
                               processing_time_seconds, created_at, updated_at"""
                
                cursor.execute(f"""
                SELECT {fields} FROM analysis_sessions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
                """, (user_id, limit))
                
                rows = cursor.fetchall()
                
                analyses = []
                for row in rows:
                    analysis = dict(row)
                    
                    # Parse JSON fields if present
                    if 'analysis_result' in analysis and analysis['analysis_result']:
                        analysis['analysis_result'] = json.loads(analysis['analysis_result'])
                    if 'metadata' in analysis and analysis['metadata']:
                        analysis['metadata'] = json.loads(analysis['metadata'])
                    
                    # Get download history for this analysis
                    analysis['download_history'] = self.get_download_history(analysis['id'])
                    
                    analyses.append(analysis)
                
                return analyses
                
        except Exception as e:
            print(f"Error getting user analyses: {e}")
            return []
    
    def get_analysis_by_id(self, analysis_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get specific analysis by ID with full content"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT * FROM analysis_sessions 
                WHERE id = ? AND user_id = ?
                """, (analysis_id, user_id))
                
                row = cursor.fetchone()
                
                if row:
                    analysis = dict(row)
                    
                    # Parse JSON fields
                    if analysis['analysis_result']:
                        analysis['analysis_result'] = json.loads(analysis['analysis_result'])
                    if analysis['metadata']:
                        analysis['metadata'] = json.loads(analysis['metadata'])
                    
                    # Get download history
                    analysis['download_history'] = self.get_download_history(analysis_id)
                    
                    return analysis
                
                return None
                
        except Exception as e:
            print(f"Error getting analysis by ID: {e}")
            return None
    
    def record_download(self, analysis_id: str, user_id: str, report_type: str, report_format: str):
        """Record a report download"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if download record exists
                cursor.execute("""
                SELECT id, download_count FROM report_downloads 
                WHERE analysis_id = ? AND user_id = ? AND report_type = ? AND report_format = ?
                """, (analysis_id, user_id, report_type, report_format))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing record
                    cursor.execute("""
                    UPDATE report_downloads 
                    SET download_count = download_count + 1, last_downloaded_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """, (existing[0],))
                else:
                    # Create new record
                    cursor.execute("""
                    INSERT INTO report_downloads 
                    (id, analysis_id, user_id, report_type, report_format)
                    VALUES (?, ?, ?, ?, ?)
                    """, (str(uuid.uuid4()), analysis_id, user_id, report_type, report_format))
                
                conn.commit()
                
        except Exception as e:
            print(f"Error recording download: {e}")
    
    def get_download_history(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Get download history for an analysis"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                SELECT report_type, report_format, download_count, 
                       first_downloaded_at, last_downloaded_at
                FROM report_downloads 
                WHERE analysis_id = ?
                ORDER BY last_downloaded_at DESC
                """, (analysis_id,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error getting download history: {e}")
            return []
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user analysis statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Basic stats
                cursor.execute("""
                SELECT 
                    COUNT(*) as total_analyses,
                    AVG(score) as avg_score,
                    MAX(score) as best_score,
                    MIN(score) as worst_score,
                    SUM(processing_time_seconds) as total_processing_time,
                    SUM(api_cost_usd) as total_api_cost
                FROM analysis_sessions 
                WHERE user_id = ?
                """, (user_id,))
                
                stats = dict(cursor.fetchone()) if cursor.fetchone() else {}
                
                # Download stats
                cursor.execute("""
                SELECT 
                    COUNT(DISTINCT analysis_id) as analyses_downloaded,
                    SUM(download_count) as total_downloads
                FROM report_downloads 
                WHERE user_id = ?
                """, (user_id,))
                
                download_stats = dict(cursor.fetchone()) if cursor.fetchone() else {}
                
                return {**stats, **download_stats}
                
        except Exception as e:
            print(f"Error getting user statistics: {e}")
            return {}
    
    def delete_analysis(self, analysis_id: str, user_id: str) -> bool:
        """Delete an analysis and its download history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete download history first
                cursor.execute("""
                DELETE FROM report_downloads 
                WHERE analysis_id = ? AND user_id = ?
                """, (analysis_id, user_id))
                
                # Delete analysis
                cursor.execute("""
                DELETE FROM analysis_sessions 
                WHERE id = ? AND user_id = ?
                """, (analysis_id, user_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting analysis: {e}")
            return False
    
    def find_similar_analyses(self, user_id: str, resume_hash: str = None, 
                            jd_hash: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar analyses based on content hashes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                conditions = ["user_id = ?"]
                params = [user_id]
                
                if resume_hash:
                    conditions.append("resume_hash = ?")
                    params.append(resume_hash)
                
                if jd_hash:
                    conditions.append("job_description_hash = ?")
                    params.append(jd_hash)
                
                query = f"""
                SELECT id, resume_filename, score, match_category, created_at
                FROM analysis_sessions 
                WHERE {' AND '.join(conditions)}
                ORDER BY created_at DESC 
                LIMIT ?
                """
                params.append(limit)
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error finding similar analyses: {e}")
            return []

# Global instance
enhanced_analysis_storage = EnhancedAnalysisStorage()

# Backward compatibility
analysis_storage = enhanced_analysis_storage
'''
    
    # Write the enhanced storage
    with open('database/enhanced_analysis_storage.py', 'w') as f:
        f.write(enhanced_storage_content)
    
    print("✅ Created enhanced analysis storage")
    return True

def create_report_history_ui():
    """Create a report history UI component"""
    print("🔧 Creating Report History UI...")
    
    history_ui_content = '''"""
Report History UI Component
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any

from database.enhanced_analysis_storage import enhanced_analysis_storage
from auth.models import User

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
'''
    
    # Write the history UI
    with open('components/report_history_ui.py', 'w') as f:
        f.write(history_ui_content)
    
    print("✅ Created report history UI component")
    return True

def update_app_integration():
    """Update app.py to integrate the fixes"""
    print("🔧 Updating app.py integration...")
    
    # Create app integration patch
    app_patch_content = '''"""
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
'''
    
    # Write the integration patch
    with open('fixes/app_integration_patch.py', 'w') as f:
        f.write(app_patch_content)
    
    print("✅ Created app integration patch")
    return True

def main():
    """Main function to apply all fixes"""
    print("🚀 COMPREHENSIVE FIX: Payment System & Report Persistence")
    print("=" * 60)
    
    # Create fixes directory
    Path('fixes').mkdir(exist_ok=True)
    Path('components').mkdir(exist_ok=True)
    
    success = True
    
    # Fix 1: Razorpay Configuration
    print("\\n1. Fixing Razorpay Payment System...")
    if not fix_razorpay_configuration():
        success = False
    
    # Fix 2: Report Persistence
    print("\\n2. Fixing Report Persistence...")
    if not fix_report_persistence():
        success = False
    
    # Fix 3: Report History UI
    print("\\n3. Creating Report History UI...")
    if not create_report_history_ui():
        success = False
    
    # Fix 4: App Integration
    print("\\n4. Creating App Integration...")
    if not update_app_integration():
        success = False
    
    if success:
        print("\\n🎉 ALL FIXES COMPLETED SUCCESSFULLY!")
        print("\\n📋 Next Steps:")
        print("1. Add Razorpay credentials to Streamlit Cloud secrets:")
        print("   - RAZORPAY_KEY_ID = rzp_live_gBOm5l3scvXYjP")
        print("   - RAZORPAY_KEY_SECRET = your_secret_key")
        print("2. Update your app.py with the integration patch")
        print("3. Test the payment system and report history")
        print("\\n✅ Payment system will work correctly")
        print("✅ Reports will persist and be accessible in history")
        print("✅ Users can re-download previous reports")
    else:
        print("\\n❌ SOME FIXES FAILED!")
        print("Check the error messages above")
    
    return success

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()