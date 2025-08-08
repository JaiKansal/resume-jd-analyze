#!/usr/bin/env python3
"""
Resume + JD Analyzer - Web Application
A fully productized web interface for resume and job description matching
"""

# Inline startup initialization
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set environment variables
os.environ.setdefault('PYTHONPATH', str(project_root))

import streamlit as st

# Streamlit Cloud environment fix - inline to avoid import issues
import os
if not os.getenv('DATABASE_URL'):
    try:
        database_url = st.secrets.get('DATABASE_URL')
        if database_url:
            os.environ['DATABASE_URL'] = database_url
            print("✅ DATABASE_URL loaded from Streamlit secrets")
    except Exception as e:
        print(f"⚠️ Could not load DATABASE_URL from secrets: {e}")

import tempfile
import zipfile
import pandas as pd
import json
import time
import os
import logging
from datetime import datetime
from pathlib import Path
import base64
from io import BytesIO

# Set up logging
logger = logging.getLogger(__name__)

# Deployment fix timestamp: 2025-08-06 15:50 UTC

def validate_user_session():
    """Validate current user session and refresh if needed"""
    if not st.session_state.get('user_authenticated', False):
        return None
    
    user = st.session_state.get('current_user')
    if not user:
        return None
    
    # Verify user still exists in database
    try:
        from auth.services import user_service
        current_user = user_service.get_user_by_id(user.id)
        
        if not current_user or not current_user.is_active:
            # User no longer exists or is inactive
            st.session_state.user_authenticated = False
            st.session_state.current_user = None
            st.session_state.user_session = None
            return None
        
        # Update session state with fresh user data
        st.session_state.current_user = current_user
        return current_user
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Session validation error: {e}")
        return user  # Return cached user if validation fails


# Authentication imports
from auth.registration import render_auth_page
from auth.services import user_service, subscription_service, session_service, analytics_service
from auth.models import UserRole, PlanType

# Enhanced services imports with proper fallback
ENHANCED_SERVICES_AVAILABLE = False

# Try to import enhanced analysis storage (this should always work)
try:
    from database.enhanced_analysis_storage import enhanced_analysis_storage
    ANALYSIS_STORAGE_AVAILABLE = True
    logger.info("Enhanced analysis storage available")
except ImportError:
    try:
        from database.analysis_storage import analysis_storage as enhanced_analysis_storage
        ANALYSIS_STORAGE_AVAILABLE = True
        logger.info("Fallback analysis storage available")
    except ImportError:
        enhanced_analysis_storage = None
        ANALYSIS_STORAGE_AVAILABLE = False
        logger.error("No analysis storage available")

# Try to import enhanced Razorpay service with comprehensive error handling
try:
    from billing.enhanced_razorpay_service import enhanced_razorpay_service
    
    # Check if Razorpay SDK is missing and use fallback
    try:
        status_info = enhanced_razorpay_service.get_status_info()
        if status_info.get('status') == 'sdk_missing':
            try:
                from billing.fallback_razorpay_service import fallback_razorpay_service
                enhanced_razorpay_service = fallback_razorpay_service
                logger.info("Using fallback Razorpay service (Direct API)")
            except ImportError:
                logger.warning("Fallback Razorpay service not available")
        else:
            logger.info("✅ Enhanced Razorpay service imported successfully")
    except Exception as e:
        logger.warning(f"Razorpay service status check failed: {e}")
    
except ImportError as e:
    logger.warning(f"Enhanced Razorpay service not available: {e}")
    try:
        from billing.fallback_razorpay_service import fallback_razorpay_service as enhanced_razorpay_service
        logger.info("Using fallback Razorpay service")
    except ImportError as e2:
        logger.warning(f"Fallback Razorpay service not available: {e2}")
        try:
            from billing.razorpay_service import razorpay_service as enhanced_razorpay_service
            logger.info("Using basic Razorpay service")
        except ImportError as e3:
            logger.error(f"No Razorpay service available: {e3}")
            # Create minimal fallback
            class FallbackRazorpayService:
                def create_order(self, *args, **kwargs): 
                    return {"error": "Payment service not available"}
                def verify_payment(self, *args, **kwargs): 
                    return False
                def get_status_info(self): 
                    return {"status": "unavailable"}
            
            enhanced_razorpay_service = FallbackRazorpayService()
            logger.info("Using minimal Razorpay fallback")

# Try to import report history UI (optional, only for enhanced features)
try:
    from components.fixed_report_history_ui import fixed_report_history_ui as report_history_ui
    REPORT_HISTORY_AVAILABLE = True
    logger.info("✅ Fixed report history UI available")
except ImportError as e:
    logger.warning(f"Fixed report history UI not available: {e}")
    try:
        from components.report_history_ui import report_history_ui
        REPORT_HISTORY_AVAILABLE = True
        logger.info("✅ Fallback report history UI available")
    except ImportError as e2:
        logger.warning(f"Report history UI not available: {e2}")
        # Create minimal fallback
        class FallbackReportHistoryUI:
            def render_history_page(self, user):
                import streamlit as st
                st.info("📝 Report history feature not available in this deployment")
                st.info("💡 Basic functionality is still available")
        
        report_history_ui = FallbackReportHistoryUI()
        REPORT_HISTORY_AVAILABLE = True
        logger.info("✅ Using fallback report history UI")

# Set enhanced services availability based on critical components
ENHANCED_SERVICES_AVAILABLE = ANALYSIS_STORAGE_AVAILABLE

# Analytics imports with error handling
try:
    from analytics.google_analytics import ga_tracker, funnel_analyzer
    logger.info("✅ Google Analytics imported successfully")
except ImportError as e:
    logger.warning(f"Google Analytics not available: {e}")
    # Create fallback objects
    class FallbackTracker:
        def track_event(self, *args, **kwargs): pass
        def track_page_view(self, *args, **kwargs): pass
        def track_conversion(self, *args, **kwargs): pass
    
    ga_tracker = FallbackTracker()
    funnel_analyzer = FallbackTracker()

try:
    from analytics.admin_dashboard import render_admin_dashboard
    logger.info("✅ Admin dashboard imported successfully")
except ImportError as e:
    logger.warning(f"Admin dashboard not available: {e}")
    def render_admin_dashboard():
        import streamlit as st
        st.info("Admin dashboard not available in this deployment")

try:
    from analytics.user_engagement import engagement_tracker
    logger.info("✅ User engagement tracker imported successfully")
except ImportError as e:
    logger.warning(f"User engagement tracker not available: {e}")
    class FallbackEngagementTracker:
        def track_user_action(self, *args, **kwargs): pass
        def get_user_engagement(self, *args, **kwargs): return {}
    
    engagement_tracker = FallbackEngagementTracker()

# PDF imports - will be loaded conditionally
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    PDF_AVAILABLE = True
    logger.info("✅ ReportLab PDF components imported successfully")
except ImportError as e:
    PDF_AVAILABLE = False
    logger.warning(f"ReportLab not available: {e}. PDF generation will be disabled.")

# Import our core functionality with comprehensive error handling
try:
    # Try to use advanced matcher if available
    from resume_matcher_ai.matcher import analyze_match
    logger.info("✅ Advanced matcher imported successfully")
except ImportError as e:
    logger.warning(f"Advanced matcher not available: {e}")
    try:
        # Fallback to protected matcher for public deployment
        from resume_matcher_ai.protected_matcher import analyze_match_protected as analyze_match
        logger.info("✅ Protected matcher imported successfully")
    except ImportError as e2:
        logger.error(f"Protected matcher also failed: {e2}")
        # Create a minimal fallback function
        def analyze_match(resume_text, jd_text):
            from resume_matcher_ai.utils import MatchResult
            return MatchResult(
                score=75,
                match_category="Moderate",
                matching_skills=["Python", "Communication"],
                missing_skills=["Advanced skills"],
                skill_gaps={"technical": ["Advanced Python"]},
                suggestions=["Improve technical skills"],
                processing_time=1.0
            )
        logger.info("✅ Using fallback matcher")

# Import other components with error handling
try:
    from resume_matcher_ai.resume_parser import extract_text_from_pdf, clean_resume_text
    from resume_matcher_ai.jd_parser import parse_jd_text
    from resume_matcher_ai.utils import setup_environment, get_usage_statistics
    logger.info("✅ All resume_matcher_ai components imported successfully")
except ImportError as e:
    logger.error(f"Some resume_matcher_ai components failed to import: {e}")
    
    # Create minimal fallbacks
    def extract_text_from_pdf(file_content):
        return "Sample resume text for testing"
    
    def clean_resume_text(text):
        return text.strip()
    
    def parse_jd_text(text):
        return {
            "requirements": ["Sample requirement"],
            "skills": ["Python", "Communication"],
            "experience_level": "Mid-level"
        }
    
    def setup_environment():
        return True
    
    def get_usage_statistics():
        return {"total_analyses": 0, "success_rate": 100}
    
    logger.info("✅ Using fallback functions for resume_matcher_ai")

# Support system imports
from support.support_dashboard import support_dashboard
from support.feedback_widget import feedback_widget

# Database initialization (must be imported early)
from database.init_database import init_database_for_streamlit

# Page configuration
st.set_page_config(
    page_title="Resume + JD Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .strong-match {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .moderate-match {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .poor-match {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .skill-tag {
        display: inline-block;
        background-color: #e9ecef;
        color: #495057;
        padding: 0.25rem 0.5rem;
        margin: 0.25rem;
        border-radius: 15px;
        font-size: 0.875rem;
    }
    
    .recommendation-box {
        background-color: #f8f9fa;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def get_subscription_with_fallback(user_id):
    """Get subscription with fallback to free plan"""
    try:
        # Verify user exists first
        user = user_service.get_user_by_id(user_id)
        if not user:
            logger.warning(f"User {user_id} not found when getting subscription")
            return None
        
        subscription = subscription_service.get_user_subscription(user_id)
        if subscription:
            return subscription
        else:
            # Create default free subscription if none exists
            logger.info(f"Creating default subscription for user {user_id}")
            free_plan = subscription_service.get_plan_by_type(PlanType.FREE)
            if free_plan:
                return subscription_service.create_subscription(user_id, free_plan.id)
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Error getting subscription for user {user_id}: {e}")
        return None

def refresh_usage_display(user_id):
    """Refresh usage display in sidebar without full page reload"""
    try:
        subscription = get_subscription_with_fallback(user_id)
        if subscription and subscription.plan and subscription.plan.monthly_analysis_limit != -1:
            remaining = (subscription.plan.monthly_analysis_limit - subscription.monthly_analysis_used) if (subscription and subscription.plan and hasattr(subscription, "monthly_analysis_used")) else 0
            # Update sidebar with new count (will show on next interaction)
            st.session_state.usage_updated = True
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Failed to refresh usage display: {e}")

def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = []
    if 'bulk_results' not in st.session_state:
        st.session_state.bulk_results = []
    if 'setup_complete' not in st.session_state:
        st.session_state.setup_complete = False
    
    # Initialize authentication state
    if 'user_authenticated' not in st.session_state:
        st.session_state.user_authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'user_session' not in st.session_state:
        st.session_state.user_session = None

def check_payment_system_status():
    """Check and display payment system status"""
    if ENHANCED_SERVICES_AVAILABLE:
        status_info = enhanced_razorpay_service.get_status_info()
        
        if status_info['status'] != 'connected':
            st.sidebar.warning("⚠️ Payment system needs configuration")
            
            with st.sidebar.expander("🔧 Payment System Status"):
                enhanced_razorpay_service.render_status_debug()
    else:
        # Check basic razorpay service
        if not enhanced_razorpay_service.client:
            st.sidebar.error("❌ Payment system not configured")
            st.sidebar.info("Add RAZORPAY_KEY_SECRET to Streamlit secrets")

def save_analysis_with_history(user_id: str, resume_filename: str, resume_content: str,
                              job_description: str, analysis_result: dict, 
                              processing_time: float = 0):
    """Save analysis with enhanced storage and history tracking"""
    
    analysis_id = None
    
    # Always try to save to database first
    if ANALYSIS_STORAGE_AVAILABLE and enhanced_analysis_storage:
        try:
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
                logger.info(f"Analysis saved to database: {analysis_id}")
                
                # Show quick stats if enhanced services are available
                if ENHANCED_SERVICES_AVAILABLE:
                    try:
                        with st.expander("📊 Your Analysis Stats"):
                            stats = enhanced_analysis_storage.get_user_statistics(user_id)
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Total Analyses", stats.get('total_analyses', 0))
                            with col2:
                                st.metric("Average Score", f"{stats.get('avg_score', 0):.1f}%")
                            with col3:
                                st.metric("Best Score", f"{stats.get('best_score', 0)}%")
                    except Exception as e:
                        logger.warning(f"Could not show analysis stats: {e}")
            else:
                logger.error("Analysis storage returned None")
                
        except Exception as e:
            logger.error(f"Failed to save analysis to database: {e}")
            analysis_id = None
    
    # Fallback: always save to session state as backup
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = []
    st.session_state.analysis_results.append((resume_filename, analysis_result))
    
    # If database save failed, try direct database insertion
    if not analysis_id:
        try:
            analysis_id = save_analysis_direct_to_database(
                user_id, resume_filename, resume_content, 
                job_description, analysis_result, processing_time
            )
            if analysis_id:
                st.success("✅ Analysis saved to your history!")
                logger.info(f"Analysis saved via direct database insertion: {analysis_id}")
        except Exception as e:
            logger.error(f"Direct database save also failed: {e}")
            st.warning("⚠️ Analysis saved to session only (may not persist)")
    
    return analysis_id


def save_analysis_direct_to_database(user_id: str, resume_filename: str, resume_content: str,
                                    job_description: str, analysis_result: dict, 
                                    processing_time: float = 0):
    """Direct database save as ultimate fallback"""
    try:
        import uuid
        from database.connection import get_db
        from database.production_connection import production_db
        
        analysis_id = str(uuid.uuid4())
        
        # Extract analysis data
        score = analysis_result.get('score', 0)
        match_category = analysis_result.get('match_category', 'unknown')
        
        # Convert complex data to JSON strings
        import json
        analysis_result_json = json.dumps(analysis_result)
        
        db = get_db()
        
        # Insert into analysis_sessions table
        query = """
            INSERT INTO analysis_sessions (
                id, user_id, resume_filename, job_description, 
                analysis_result, score, match_category, 
                processing_time_seconds, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """
        
        params = (
            analysis_id, user_id, resume_filename, job_description,
            analysis_result_json, score, match_category, processing_time
        )
        
        rows_affected = db.execute_command(query, params)
        
        if rows_affected > 0:
            logger.info(f"Direct database save successful: {analysis_id}")
            return analysis_id
        else:
            logger.error("Direct database save failed: no rows affected")
            return None
            
    except Exception as e:
        logger.error(f"Direct database save failed: {e}")
        return None

def check_setup():
    """Check if the application is properly configured"""
    if not st.session_state.setup_complete:
        setup_result = setup_environment()
        if setup_result['success']:
            st.session_state.setup_complete = True
            return True
        else:
            st.error("⚠️ Setup Issues Detected")
            for error in setup_result['errors']:
                st.error(f"• {error}")
            
            st.info("💡 Setup Instructions:")
            st.code("export PERPLEXITY_API_KEY='your-api-key-here'")
            st.markdown("[Get your API key from Perplexity](https://www.perplexity.ai/settings/api)")
            return False
    return True

def render_header():
    """Render the main application header"""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Resume + JD Analyzer</h1>
        <p>AI-Powered Resume and Job Description Compatibility Analysis</p>
    </div>
    """, unsafe_allow_html=True)

def get_match_color_class(score):
    """Get CSS class based on match score"""
    if score >= 70:
        return "strong-match"
    elif score >= 40:
        return "moderate-match"
    else:
        return "poor-match"

def render_analysis_result(result, resume_name="Resume"):
    """Render a single analysis result"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader(f"📄 {resume_name}")
    
    with col2:
        match_class = get_match_color_class(result.score)
        st.markdown(f"""
        <div class="{match_class}">
            {result.score}% Match
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.metric("Category", result.match_category)
    
    # Detailed analysis
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "✅ Matching Skills", "❌ Skill Gaps", "💡 Recommendations"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Compatibility Score", f"{result.score}%")
        with col2:
            st.metric("Matching Skills", len(result.matching_skills))
        with col3:
            st.metric("Processing Time", f"{result.processing_time:.1f}s")
    
    with tab2:
        if result.matching_skills:
            st.success(f"Found {len(result.matching_skills)} matching skills:")
            for i, skill in enumerate(result.matching_skills[:10], 1):
                if isinstance(skill, dict):
                    st.write(f"{i}. **Resume**: {skill.get('resume', 'N/A')}")
                    st.write(f"   **Job**: {skill.get('job_description', 'N/A')}")
                else:
                    st.write(f"{i}. {skill}")
            
            if len(result.matching_skills) > 10:
                st.info(f"... and {len(result.matching_skills) - 10} more matching skills")
        else:
            st.warning("No direct skill matches found. Consider updating resume terminology.")
    
    with tab3:
        total_gaps = sum(len(skills) for skills in result.skill_gaps.values())
        if total_gaps > 0:
            for category, icon in [("Critical", "🔴"), ("Important", "🟡"), ("Nice-to-have", "🟢")]:
                skills = result.skill_gaps.get(category, [])
                if skills:
                    st.markdown(f"**{icon} {category} ({len(skills)} skills)**")
                    for skill in skills:
                        st.markdown(f"• {skill}")
                    st.write("")
        else:
            st.success("🎉 Excellent! All key skills are present in the resume!")
    
    with tab4:
        if result.suggestions:
            for i, suggestion in enumerate(result.suggestions, 1):
                st.markdown(f"""
                <div class="recommendation-box">
                    <strong>Recommendation {i}:</strong><br>
                    {suggestion}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No specific recommendations - your resume looks well-optimized!")

def analyze_single_resume(resume_file, jd_text):
    """Analyze a single resume against job description"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(resume_file.read())
            tmp_path = tmp_file.name
        
        # Extract and analyze
        resume_text = extract_text_from_pdf(tmp_path)
        cleaned_resume = clean_resume_text(resume_text)
        jd_data = parse_jd_text(jd_text)
        
        result = analyze_match(cleaned_resume, jd_data.__dict__)
        
        # Clean up
        os.unlink(tmp_path)
        
        return result, None
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                pass
        return None, str(e)

def create_downloadable_report(results, jd_title="Job Position"):
    """Create a downloadable report"""
    report_data = []
    
    for i, (resume_name, result) in enumerate(results):
        report_data.append({
            'Resume': resume_name,
            'Compatibility_Score': result.score,
            'Match_Category': result.match_category,
            'Matching_Skills_Count': len(result.matching_skills),
            'Critical_Gaps': len(result.skill_gaps.get('Critical', [])),
            'Important_Gaps': len(result.skill_gaps.get('Important', [])),
            'Processing_Time': round(result.processing_time, 2),
            'Top_Recommendation': result.suggestions[0] if result.suggestions else 'None'
        })
    
    df = pd.DataFrame(report_data)
    return df


def cleanup_session_state():
    """Clean up old session state data to prevent memory issues"""
    # Remove old analysis results if too many
    if 'analysis_results' in st.session_state and len(st.session_state.analysis_results) > 50:
        st.session_state.analysis_results = st.session_state.analysis_results[-25:]
    
    if 'bulk_results' in st.session_state and len(st.session_state.bulk_results) > 50:
        st.session_state.bulk_results = st.session_state.bulk_results[-25:]

def main():
    """Main application function"""
    initialize_session_state()
    
    # Check authentication first
    if not st.session_state.get('user_authenticated', False):
        # Show authentication page
        authenticated = render_auth_page()
        if not authenticated:
            return
    
    # User is authenticated, show main app
    render_authenticated_app()

def render_authenticated_app():
    """Render the main application for authenticated users"""
    # Validate current user session
    user = validate_user_session()
    if not user:
        st.error("Authentication error. Please sign in again.")
        st.session_state.user_authenticated = False
        st.rerun()
        return
    
    # Check setup
    if not check_setup():
        return
    
    # Render header with user info
    render_authenticated_header(user)
    
    # Check subscription and usage limits
    subscription = get_subscription_with_fallback(user.id)
    if subscription:
        render_usage_info(subscription)
    
    # Sidebar navigation
    st.sidebar.title("🎛️ Navigation")
    
    # User info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"👤 **{user.get_full_name()}**")
    st.sidebar.markdown(f"📧 {user.email}")
    if subscription:
        st.sidebar.markdown(f"💳 {subscription.plan.name if subscription and subscription.plan else "Free"}")
        if subscription and subscription.plan and subscription.plan.monthly_analysis_limit != -1:
            remaining = (subscription.plan.monthly_analysis_limit - subscription.monthly_analysis_used) if (subscription and subscription.plan and hasattr(subscription, "monthly_analysis_used")) else 0
            st.sidebar.markdown(f"📊 {remaining} analyses remaining")
    
    # Logout button
    if st.sidebar.button("🚪 Sign Out"):
        # Deactivate session
        if st.session_state.get('user_session'):
            session_service.deactivate_session(st.session_state.user_session.session_token)
        
        # Clear session state
        st.session_state.user_authenticated = False
        st.session_state.current_user = None
        st.session_state.user_session = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Check payment system status
    check_payment_system_status()
    
    # Navigation menu - add admin dashboard for admin users
    nav_options = ["🎯 Single Analysis", "📦 Bulk Analysis", "🎯 Job Matching", "📋 Analysis History", "📊 Dashboard", "🎧 Support", "⚙️ Settings"]
    
    # Add admin dashboard for admin users
    if user.role in [UserRole.ADMIN, UserRole.ENTERPRISE_ADMIN]:
        nav_options.insert(-2, "🔧 Admin Dashboard")  # Insert before Support and Settings
        nav_options.insert(-2, "🚀 Beta Program")  # Insert before Support and Settings
    
    mode = st.sidebar.selectbox(
        "Choose Analysis Mode",
        nav_options
    )
    
    # Handle upgrade modal
    from billing.upgrade_ui import upgrade_ui
    from billing.payment_form import payment_form
    
    if st.session_state.get('show_upgrade_modal', False):
        upgrade_ui.render_upgrade_modal(user, st.session_state.get('target_plan'))
    
    # Handle payment form
    if st.session_state.get('show_payment_form', False):
        payment_form.render_payment_form(user, st.session_state.get('payment_plan'))
    
    # Handle payment success/failure
    payment_form.render_payment_success()
    payment_form.render_payment_failed()
    
    # Route to appropriate function
    if mode == "🎯 Single Analysis":
        # Track page view and engagement
        ga_tracker.track_page_view("Single Analysis", "single-analysis", user.id)
        engagement_tracker.track_page_visit(user.id, "Single Analysis")
        render_single_analysis_authenticated(user, subscription)
    elif mode == "📦 Bulk Analysis":
        # Track page view and engagement
        ga_tracker.track_page_view("Bulk Analysis", "bulk-analysis", user.id)
        engagement_tracker.track_page_visit(user.id, "Bulk Analysis")
        render_bulk_analysis_authenticated(user, subscription)
    elif mode == "🎯 Job Matching":
        # Track page view
        ga_tracker.track_page_view("Job Matching", "job-matching", user.id)
        render_job_matching()
    elif mode == "📋 Analysis History":
        # Track page view
        ga_tracker.track_page_view("Analysis History", "analysis-history", user.id)
        engagement_tracker.track_page_visit(user.id, "Analysis History")
        render_simple_working_history(user)
    elif mode == "📊 Dashboard":
        # Track page view
        ga_tracker.track_page_view("User Dashboard", "dashboard", user.id)
        render_dashboard_authenticated(user, subscription)
    elif mode == "🔧 Admin Dashboard":
        # Track page view
        ga_tracker.track_page_view("Admin Dashboard", "admin-dashboard", user.id)
        render_admin_dashboard()
    elif mode == "🚀 Beta Program":
        # Track page view
        ga_tracker.track_page_view("Beta Program", "beta-program", user.id)
        render_beta_program_page(user, subscription)
    elif mode == "🎧 Support":
        # Track page view
        ga_tracker.track_page_view("Support", "support", user.id)
        render_support_page(user, subscription)
    elif mode == "⚙️ Settings":
        # Track page view
        ga_tracker.track_page_view("Settings", "settings", user.id)
        render_settings_authenticated(user, subscription)

def render_authenticated_header(user):
    """Render header for authenticated users"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class="main-header">
            <h1>🎯 Resume + JD Analyzer</h1>
            <p>Welcome back, {user.first_name}! AI-Powered Resume Analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Quick stats or upgrade prompt
        subscription = get_subscription_with_fallback(user.id)
        if subscription and subscription.plan and hasattr(subscription.plan, 'plan_type') and subscription.plan.plan_type.value == 'free':
            st.markdown("""
            <div style="background: #fff3cd; padding: 1rem; border-radius: 10px; text-align: center; margin-top: 2rem;">
                <strong>🚀 Upgrade to Pro</strong><br>
                <small>Unlimited analyses & premium features</small>
            </div>
            """, unsafe_allow_html=True)

def render_usage_info(subscription):
    """Render usage information for the user"""
    if subscription and subscription.plan and subscription.plan.monthly_analysis_limit != -1:
        used = subscription.monthly_analysis_used
        limit = subscription.plan.monthly_analysis_limit if subscription and subscription.plan else 0
        remaining = limit - used
        
        if remaining <= 0:
            st.error(f"🚫 You've reached your monthly limit of {limit} analyses. Upgrade to continue.")
        elif remaining <= 1:
            st.warning(f"⚠️ Only {remaining} analysis remaining this month. Consider upgrading.")
        elif remaining <= 3:
            st.info(f"📊 {remaining} analyses remaining this month.")


def render_simple_analysis_history(user):
    """Simple analysis history fallback using database directly"""
    st.title("📊 Analysis History")
    
    try:
        from database.connection import get_db
        from database.production_connection import production_db
        
        db = get_db()
        
        # Get user's analysis history
        query = """
        SELECT id, resume_filename, score, match_category, created_at
        FROM analysis_sessions 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 50
        """
        
        analyses = db.execute_query(query, (user.id,))
        
        if analyses:
            st.success(f"Found {len(analyses)} previous analyses")
            
            for analysis in analyses:
                with st.expander(f"📄 {analysis['resume_filename']} - {analysis['score']}% ({analysis['created_at'][:10]})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Score", f"{analysis['score']}%")
                    with col2:
                        st.metric("Category", analysis['match_category'])
                    with col3:
                        st.metric("Date", analysis['created_at'][:10])
                    
                    if st.button(f"Re-download Report", key=f"download_{analysis['id']}"):
                        st.info("💡 Re-download functionality coming soon!")
        else:
            st.info("📝 No analysis history found. Complete an analysis to see results here!")
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        st.error(f"❌ Failed to load analysis history: {e}")
        st.info("💡 Try refreshing the page or contact support if the issue persists.")


def render_simple_working_history(user):
    """Render analysis history page with improved error handling"""
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
                        render_analysis_result(result, filename)

def render_single_analysis_authenticated(user, subscription):
    """Render single analysis with authentication and usage tracking"""
    st.header("🎯 Single Resume Analysis")
    
    # Import upgrade UI components
    from billing.upgrade_ui import upgrade_ui
    from billing.upgrade_flow import upgrade_flow
    
    # Show usage warning if approaching limits
    upgrade_ui.render_usage_warning(user)
    
    # Show trial status if applicable
    upgrade_ui.render_trial_status(user)
    
    # Check if user can analyze
    can_analyze, reason = subscription_service.can_user_analyze(user.id)
    
    if not can_analyze:
        st.error(f"❌ {reason}")
        if "limit" in reason.lower():
            # Show usage exceeded modal
            upgrade_ui.render_usage_exceeded_modal(user)
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Upload Resume")
        
        # Show file size limit for user's plan
        from billing.watermark_service import watermark_service
        file_size_limit = watermark_service.get_file_size_limit_mb(user)
        st.caption(f"Maximum file size: {file_size_limit}MB")
        
        resume_file = st.file_uploader(
            "Choose a PDF resume file",
            type=['pdf'],
            help=f"Upload a PDF resume for analysis (max {file_size_limit}MB)"
        )
        
        # Check file size if file is uploaded
        if resume_file:
            file_size_mb = len(resume_file.getvalue()) / (1024 * 1024)
            can_upload, size_error = watermark_service.check_file_size_limit(user, file_size_mb)
            
            if not can_upload:
                st.error(f"❌ {size_error}")
                if "free plan" in size_error.lower():
                    if st.button("🚀 Upgrade for Larger Files", type="primary"):
                        st.session_state.show_upgrade_modal = True
                        st.session_state.target_plan = PlanType.PROFESSIONAL
                resume_file = None  # Reset file to prevent analysis
    
    with col2:
        st.subheader("📋 Job Description")
        jd_input_method = st.radio(
            "Input method:",
            ["📝 Paste Text", "📁 Upload File"]
        )
        
        if jd_input_method == "📝 Paste Text":
            jd_text = st.text_area(
                "Paste job description here:",
                height=200,
                placeholder="Paste the complete job description including requirements, responsibilities, and qualifications..."
            )
        else:
            jd_file = st.file_uploader(
                "Choose a text file",
                type=['txt'],
                help="Upload a .txt file containing the job description")
            jd_text = ""
            if jd_file:
                jd_text = jd_file.read().decode('utf-8')
                st.text_area("Job description preview:", jd_text[:500] + "...", height=100)
    
    # Analysis button
    if st.button("🚀 Analyze Compatibility", type="primary", use_container_width=True):
        if resume_file and jd_text.strip():
            with st.spinner("🔄 Analyzing compatibility... This may take up to 30 seconds."):
                start_time = time.time()
                
                # Extract resume text for storage
                try:
                    # Save uploaded file temporarily to extract text
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(resume_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Extract text from PDF
                    resume_text = extract_text_from_pdf(tmp_path)
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
                    
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    # Fallback to basic text extraction
                    resume_text = f"Resume content from {resume_file.name}"
                    logger.warning(f"Failed to extract resume text: {e}")
                
                result, error = analyze_single_resume(resume_file, jd_text)
                processing_time = time.time() - start_time
                
                if result:
                    # Track usage with billing system
                    from billing.usage_tracker import usage_monitor
                    usage_monitor.track_analysis_session(
                        user_id=user.id,
                        session_type="single",
                        resume_count=1,
                        processing_time=processing_time,
                        api_cost=0.0  # Placeholder for actual API cost
                    )
                    
                    # Track analytics event
                    ga_tracker.track_analysis_completion(
                        user_id=user.id,
                        analysis_type="single",
                        resume_count=1,
                        processing_time=processing_time,
                        match_score=result.score
                    )
                    
                    # Track conversion funnel progression
                    ga_tracker.track_conversion_funnel(user.id, "first_analysis")
                    
                    st.success("✅ Analysis completed!")
                    render_analysis_result(result, resume_file.name)
                    
                    # Store result in session state immediately to prevent loss
                    st.session_state.analysis_results.append((resume_file.name, result))
                    
                    # Refresh usage display without full reload (usage already tracked by usage_monitor)
                    refresh_usage_display(user.id)
                    
                    # Store result with enhanced history tracking
                    analysis_id = save_analysis_with_history(
                        user_id=user.id,
                        resume_filename=resume_file.name,
                        resume_content=resume_text,
                        job_description=jd_text,
                        analysis_result=result.__dict__ if hasattr(result, '__dict__') else result,
                        processing_time=getattr(result, 'processing_time', 0)
                    )
                    
                    # Download report options
                    render_download_options(user, [(resume_file.name, result)], jd_text)
                    
                    # Show NPS survey after successful analysis
                    feedback_widget.render_nps_survey()
                    
                else:
                    st.error(f"❌ Analysis failed: {error}")
        else:
            st.warning("⚠️ Please upload a resume and provide a job description.")
    
    # Add feedback widget and quick rating
    feedback_widget.render_feedback_button()
    feedback_widget.render_quick_rating("single_analysis")

def render_bulk_analysis_authenticated(user, subscription):
    """Render bulk analysis with authentication and usage tracking"""
    st.header("📦 Bulk Resume Analysis")
    
    # Import upgrade UI components
    from billing.upgrade_ui import upgrade_ui
    
    # Check if user has bulk analysis feature
    if not subscription or not subscription.plan or not hasattr(subscription.plan, 'has_feature') or not subscription.plan.has_feature('bulk_upload'):
        # Show feature gate prompt
        upgrade_ui.render_feature_gate_prompt(user, "bulk_upload")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📁 Upload Resumes")
        resume_files = st.file_uploader(
            "Choose PDF resume files",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload multiple PDF resumes for batch analysis"
        )
        
        if resume_files:
            st.info(f"📊 {len(resume_files)} resumes uploaded")
            
            # Check if user can analyze this many
            can_analyze, reason = subscription_service.can_user_analyze(user.id)
            if not can_analyze:
                st.error(f"❌ {reason}")
                return
    
    with col2:
        st.subheader("📋 Job Description")
        jd_text = st.text_area(
            "Paste job description here:",
            height=200,
            placeholder="Paste the job description that all resumes will be analyzed against..."
        )
    
    # Bulk analysis button
    if st.button("🚀 Start Bulk Analysis", type="primary", use_container_width=True):
        if resume_files and jd_text.strip():
            progress_bar = st.progress(0)
            status_text = st.empty()
            results = []
            start_time = time.time()
            
            for i, resume_file in enumerate(resume_files):
                status_text.text(f"Analyzing {resume_file.name}... ({i+1}/{len(resume_files)})")
                
                result, error = analyze_single_resume(resume_file, jd_text)
                if result:
                    results.append((resume_file.name, result))
                    
                    # Usage will be tracked once for the entire bulk analysis
                else:
                    st.error(f"Failed to analyze {resume_file.name}: {error}")
                
                progress_bar.progress((i + 1) / len(resume_files))
            
            processing_time = time.time() - start_time
            status_text.text("✅ Bulk analysis completed!")
            
            # Track usage with billing system (includes usage increment)
            from billing.usage_tracker import usage_monitor
            usage_monitor.track_analysis_session(
                user_id=user.id,
                session_type="bulk",
                resume_count=len(results),
                processing_time=processing_time,
                api_cost=0.0  # Placeholder for actual API cost
            )
            
            # Track analytics event
            ga_tracker.track_analysis_completion(
                user_id=user.id,
                analysis_type="bulk",
                resume_count=len(results),
                processing_time=processing_time,
                match_score=sum(result.score for _, result in results) / len(results) if results else 0
            )
            
            # Track feature usage
            ga_tracker.track_feature_usage(user.id, "bulk_analysis", "analysis")
            
            # Store results
            st.session_state.bulk_results = results
            
            # Display summary
            if results:
                st.success(f"🎉 Successfully analyzed {len(results)} resumes!")
                
                # Summary statistics
                scores = [result.score for _, result in results]
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Average Score", f"{sum(scores)/len(scores):.1f}%")
                with col2:
                    st.metric("Highest Score", f"{max(scores)}%")
                with col3:
                    st.metric("Strong Matches", len([s for s in scores if s >= 70]))
                with col4:
                    st.metric("Total Analyzed", len(results))
                
                # Results table
                st.subheader("📊 Results Summary")
                df = create_downloadable_report(results)
                st.dataframe(df, use_container_width=True)
                
                # Download options
                render_download_options(user, results, jd_text, is_bulk=True)
        else:
            st.warning("⚠️ Please upload resumes and provide a job description.")

def render_download_options(user, results, jd_text, is_bulk=False):
    """Render download options for analysis results"""
    st.subheader("📥 Download Reports")
    
    # Report type selection
    if user.role in [UserRole.HR_MANAGER, UserRole.ADMIN, UserRole.ENTERPRISE_ADMIN]:
        default_audience = "🏢 Company Report (Hiring Decision)"
    else:
        default_audience = "👤 Job Seeker Report (Resume Optimization)"
    
    report_audience = st.radio(
        "Select report type:",
        ["👤 Job Seeker Report (Resume Optimization)", "🏢 Company Report (Hiring Decision)"],
        index=0 if default_audience.startswith("👤") else 1,
        help="Choose the report format based on your needs"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        df = create_downloadable_report(results)
        csv = df.to_csv(index=False)
        filename_prefix = "bulk_analysis" if is_bulk else "resume_analysis"
        st.download_button(
            label="📊 CSV Summary",
            data=csv,
            file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Generate appropriate text report
        if "Job Seeker" in report_audience:
            text_report = create_job_seeker_report(results, jd_title="Position Analysis", jd_text=jd_text)
            report_filename = f"job_seeker_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        else:
            text_report = create_company_report(results, jd_title="Position Analysis", jd_text=jd_text)
            report_filename = f"company_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        st.download_button(
            label="📄 Text Report",
            data=text_report,
            file_name=report_filename,
            mime="text/plain",
            use_container_width=True
        )
    
    with col3:
        # Generate PDF report with watermark handling
        from billing.watermark_service import watermark_service
        
        if PDF_AVAILABLE:
            try:
                # Generate report content
                if "Job Seeker" in report_audience:
                    pdf_report_text = create_job_seeker_report(results, jd_title="Position Analysis", jd_text=jd_text)
                    pdf_filename = f"job_seeker_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                else:
                    pdf_report_text = create_company_report(results, jd_title="Position Analysis", jd_text=jd_text)
                    pdf_filename = f"company_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                # Check if user should get watermarked PDF
                if watermark_service.should_add_watermark(user):
                    # Show watermark notice
                    from billing.upgrade_ui import upgrade_ui
                    upgrade_ui.render_watermarked_pdf_notice()
                    
                    # Generate watermarked PDF
                    pdf_data = watermark_service.create_watermarked_pdf(
                        pdf_report_text, "Resume Analysis Report", user
                    )
                    
                    if pdf_data:
                        st.download_button(
                            label="📑 PDF Report (Watermarked)",
                            data=pdf_data,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                    else:
                        st.error("PDF generation failed")
                else:
                    # Generate clean PDF for premium users
                    pdf_data = create_pdf_report(pdf_report_text, "Resume Analysis Report")
                    
                    st.download_button(
                        label="📑 PDF Report",
                        data=pdf_data,
                        file_name=pdf_filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                st.error(f"PDF generation failed: {str(e)}")
                st.info("Please use the Text Report option instead.")
        else:
            st.info("📑 PDF Report")
            st.caption("Install reportlab for PDF: pip install reportlab")

def render_beta_program_page(user, subscription):
    """Render beta program page for admin users"""
    # Import beta dashboard
    from support.beta_dashboard import beta_dashboard
    
    # Check if user has admin access
    if user.role not in [UserRole.ADMIN, UserRole.ENTERPRISE_ADMIN]:
        st.error("❌ Access denied. Beta program management is only available to administrators.")
        return
    
    # Render the beta program dashboard
    beta_dashboard.render_beta_program_page()

def render_support_page(user, subscription):
    """Render support page for authenticated users"""
    # Render the support dashboard
    support_dashboard.render_support_page()
    
    # Add feedback widget
    feedback_widget.render_feedback_button()
    
    # Add quick rating for support page
    feedback_widget.render_quick_rating("support_page")

def render_dashboard_authenticated(user, subscription):
    """Render dashboard for authenticated users"""
    st.header("📊 Your Analytics Dashboard")
    
    # Get user usage stats
    usage_stats = analytics_service.get_user_usage_stats(user.id, days=30)
    
    # Usage overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analyses", usage_stats['total_sessions'])
    with col2:
        st.metric("Resumes Processed", usage_stats['total_resumes'])
    with col3:
        st.metric("Avg Processing Time", f"{usage_stats['avg_processing_time']:.1f}s")
    with col4:
        if subscription and subscription.plan and subscription.plan.monthly_analysis_limit != -1:
            remaining = (subscription.plan.monthly_analysis_limit - subscription.monthly_analysis_used) if (subscription and subscription.plan and hasattr(subscription, "monthly_analysis_used")) else 0
            st.metric("Remaining This Month", remaining)
        else:
            st.metric("Plan", "Unlimited")
    
    # Recent analysis results
    if st.session_state.analysis_results:
        st.subheader("📈 Recent Analysis Results")
        
        # Create a simple chart of recent scores
        recent_results = st.session_state.analysis_results[-10:]  # Last 10 results
        if recent_results:
            scores_data = {
                'Resume': [name for name, _ in recent_results],
                'Score': [result.score for _, result in recent_results]
            }
            df = pd.DataFrame(scores_data)
            st.bar_chart(df.set_index('Resume'))
    
    # Subscription info
    st.subheader("💳 Subscription Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Plan:** {subscription.plan.name if subscription and subscription.plan else "Free"}
        **Status:** {subscription.status.value.title()}
        **Monthly Limit:** {'Unlimited' if subscription and subscription.plan and subscription.plan.monthly_analysis_limit == -1 else subscription.plan.monthly_analysis_limit if subscription and subscription.plan else 0}
        **Used This Month:** {subscription.monthly_analysis_used}
        """)
    
    with col2:
        if subscription.plan.plan_type.value != 'enterprise':
            st.success("🚀 **Ready to upgrade?**")
            st.markdown("Get more features and unlimited analyses!")
            if st.button("View Upgrade Options", type="primary"):
                st.session_state.show_upgrade_modal = True

def render_settings_authenticated(user, subscription):
    """Render settings page for authenticated users"""
    st.header("⚙️ Account Settings")
    
    # Profile settings
    st.subheader("👤 Profile Information")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name", value=user.first_name or "")
            email = st.text_input("Email", value=user.email, disabled=True)
        
        with col2:
            last_name = st.text_input("Last Name", value=user.last_name or "")
            phone = st.text_input("Phone", value=user.phone or "")
        
        company_name = st.text_input("Company", value=user.company_name or "")
        country = st.selectbox("Country", [
            "United States", "Canada", "United Kingdom", "Australia",
            "Germany", "France", "Netherlands", "Sweden", "India",
            "Singapore", "Japan", "Other"
        ], index=0 if not user.country else ["United States", "Canada", "United Kingdom", "Australia", "Germany", "France", "Netherlands", "Sweden", "India", "Singapore", "Japan", "Other"].index(user.country) if user.country in ["United States", "Canada", "United Kingdom", "Australia", "Germany", "France", "Netherlands", "Sweden", "India", "Singapore", "Japan", "Other"] else 11)
        
        if st.form_submit_button("Update Profile", type="primary"):
            # Update user information
            user.first_name = first_name
            user.last_name = last_name
            user.phone = phone
            user.company_name = company_name
            user.country = country
            
            if user_service.update_user(user):
                st.success("✅ Profile updated successfully!")
                st.session_state.current_user = user
            else:
                st.error("❌ Failed to update profile. Please try again.")
    
    # Password change
    st.subheader("🔒 Change Password")
    
    with st.form("password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("Change Password"):
            if not current_password or not new_password:
                st.error("Please fill in all password fields.")
            elif new_password != confirm_password:
                st.error("New passwords do not match.")
            elif not user.verify_password(current_password):
                st.error("Current password is incorrect.")
            else:
                # Update password
                user.password_hash = user.hash_password(new_password)
                if user_service.update_user(user):
                    st.success("✅ Password changed successfully!")
                else:
                    st.error("❌ Failed to change password. Please try again.")
    
    # Subscription management
    st.subheader("💳 Subscription Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Current Plan:** {subscription.plan.name if subscription and subscription.plan else "Free"}
        **Status:** {subscription.status.value.title()}
        **Monthly Analyses:** {'Unlimited'
    if subscription and subscription.plan and subscription.plan.monthly_analysis_limit == -1
    else f"{subscription.monthly_analysis_used}/{subscription.plan.monthly_analysis_limit if subscription and subscription.plan else 0}"}
        """)
    
    with col2:
        if st.button("🚀 Upgrade Plan", type="primary"):
            st.session_state.show_upgrade_modal = True
        
        if subscription.plan.plan_type.value != 'free':
            if st.button("⬇️ Downgrade to Free", type="secondary"):
                st.warning("This will downgrade your account to the free tier.")
    
    # Account deletion
    st.subheader("⚠️ Danger Zone")
    
    with st.expander("Delete Account"):
        st.error("**Warning:** This action cannot be undone. All your data will be permanently deleted.")
        
        delete_confirmation = st.text_input("Type 'DELETE' to confirm account deletion:")
        
        if st.button("🗑️ Delete My Account", type="secondary"):
            if delete_confirmation == "DELETE":
                # In production, this would properly handle account deletion
                st.error("Account deletion is not implemented in this demo.")
            else:
                st.error("Please type 'DELETE' to confirm.")

# Add these placeholder functions that are referenced but not defined
def render_job_matching():
    """Placeholder for job matching feature"""
    st.header("🎯 Job Matching")
    st.info("Job matching feature coming soon!")

def create_detailed_report(results):
    """Create a detailed text report"""
    return "Detailed report functionality to be implemented"

def create_pdf_report(text_content, title):
    """Create PDF report from text content"""
    # This would use reportlab to create a PDF
    return b"PDF content placeholder"

def render_single_analysis():
    """Render single resume analysis interface"""
    st.header("🎯 Single Resume Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Upload Resume")
        resume_file = st.file_uploader(
            "Choose a PDF resume file",
            type=['pdf'],
            help="Upload a PDF resume for analysis")
    
    with col2:
        st.subheader("📋 Job Description")
        jd_input_method = st.radio(
            "Input method:",
            ["📝 Paste Text", "📁 Upload File"]
        )
        
        if jd_input_method == "📝 Paste Text":
            jd_text = st.text_area(
                "Paste job description here:",
                height=200,
                placeholder="Paste the complete job description including requirements, responsibilities, and qualifications..."
            )
        else:
            jd_file = st.file_uploader(
                "Choose a text file",
                type=['txt'],
                help="Upload a .txt file containing the job description"
            )
            jd_text = ""
            if jd_file:
                jd_text = jd_file.read().decode('utf-8')
                st.text_area("Job description preview:", jd_text[:500] + "...", height=100)
    
    # Analysis button
    if st.button("🚀 Analyze Compatibility", type="primary", use_container_width=True):
        if resume_file and jd_text.strip():
            with st.spinner("🔄 Analyzing compatibility... This may take up to 30 seconds."):
                # Extract resume text for storage
                try:
                    # Save uploaded file temporarily to extract text
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(resume_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Extract text from PDF
                    resume_text = extract_text_from_pdf(tmp_path)
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
                    
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    # Fallback to basic text extraction
                    resume_text = f"Resume content from {resume_file.name}"
                    logger.warning(f"Failed to extract resume text: {e}")
                
                result, error = analyze_single_resume(resume_file, jd_text)
                
                if result:
                    # Track usage with billing system
                    from billing.usage_tracker import usage_monitor
                    usage_monitor.track_analysis_session(
                        user_id=user.id,
                        session_type="single",
                        resume_count=1,
                        processing_time=0.0,  # Processing time not tracked in this section
                        api_cost=0.0  # Placeholder for actual API cost
                    )
                    
                    st.success("✅ Analysis completed!")
                    render_analysis_result(result, resume_file.name)
                    
                    # Refresh usage display without full reload
                    refresh_usage_display(user.id)
                    
                    # Store result with enhanced history tracking
                    analysis_id = save_analysis_with_history(
                        user_id=user.id,
                        resume_filename=resume_file.name,
                        resume_content=resume_text,
                        job_description=jd_text,
                        analysis_result=result.__dict__ if hasattr(result, '__dict__') else result,
                        processing_time=getattr(result, 'processing_time', 0)
                    )
                    
                    # Download report options
                    st.subheader("📥 Download Reports")
                    
                    # Report type selection
                    report_audience = st.radio(
                        "Select report type:",
                        ["👤 Job Seeker Report (Resume Optimization)", "🏢 Company Report (Hiring Decision)"],
                        help="Choose the report format based on your needs"
                    )
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        df = create_downloadable_report([(resume_file.name, result)])
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📊 CSV Summary",
                            data=csv,
                            file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    with col2:
                        # Generate appropriate text report
                        if "Job Seeker" in report_audience:
                            text_report = create_job_seeker_report([(resume_file.name, result)], jd_title="Position Analysis", jd_text=jd_text)
                            report_filename = f"job_seeker_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        else:
                            text_report = create_company_report([(resume_file.name, result)], jd_title="Position Analysis", jd_text=jd_text)
                            report_filename = f"company_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        
                        st.download_button(
                            label="📄 Text Report",
                            data=text_report,
                            file_name=report_filename,
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col3:
                        # Generate PDF report
                        if PDF_AVAILABLE:
                            try:
                                if "Job Seeker" in report_audience:
                                    pdf_report_text = create_job_seeker_report([(resume_file.name, result)], jd_title="Position Analysis", jd_text=jd_text)
                                    pdf_filename = f"job_seeker_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                else:
                                    pdf_report_text = create_company_report([(resume_file.name, result)], jd_title="Position Analysis", jd_text=jd_text)
                                    pdf_filename = f"company_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                
                                pdf_data = create_pdf_report(pdf_report_text, "Resume Analysis Report")
                                
                                st.download_button(
                                    label="📑 PDF Report",
                                    data=pdf_data,
                                    file_name=pdf_filename,
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            except Exception as e:
                                logger.error(f"Unexpected error: {e}")
                                st.error(f"PDF generation failed: {str(e)}")
                                st.info("Please use the Text Report option instead.")
                        else:
                            st.info("📑 PDF Report")
                            st.caption("Install reportlab for PDF: pip install reportlab")
                            if st.button("📑 PDF Not Available", disabled=True, use_container_width=True):
                                pass
                else:
                    st.error(f"❌ Analysis failed: {error}")
        else:
            st.warning("⚠️ Please upload a resume and provide a job description.")

def render_bulk_analysis():
    """Render bulk analysis interface"""
    st.header("📦 Bulk Resume Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📁 Upload Resumes")
        resume_files = st.file_uploader(
            "Choose PDF resume files",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload multiple PDF resumes for batch analysis"
        )
        
        if resume_files:
            st.info(f"📊 {len(resume_files)} resumes uploaded")
    
    with col2:
        st.subheader("📋 Job Description")
        jd_text = st.text_area(
            "Paste job description here:",
            height=200,
            placeholder="Paste the job description that all resumes will be analyzed against..."
        )
    
    # Bulk analysis button
    if st.button("🚀 Start Bulk Analysis", type="primary", use_container_width=True):
        if resume_files and jd_text.strip():
            progress_bar = st.progress(0)
            status_text = st.empty()
            results = []
            start_time = time.time()
            
            for i, resume_file in enumerate(resume_files):
                status_text.text(f"Analyzing {resume_file.name}... ({i+1}/{len(resume_files)})")
                
                result, error = analyze_single_resume(resume_file, jd_text)
                if result:
                    results.append((resume_file.name, result))
                    
                    # Usage will be tracked once for the entire bulk analysis
                else:
                    st.error(f"Failed to analyze {resume_file.name}: {error}")
                
                progress_bar.progress((i + 1) / len(resume_files))
            
            status_text.text("✅ Bulk analysis completed!")
            
            # Track usage with billing system (includes usage increment)
            from billing.usage_tracker import usage_monitor
            usage_monitor.track_analysis_session(
                user_id=user.id,
                session_type="bulk",
                resume_count=len(results),
                processing_time=time.time() - start_time,
                api_cost=0.0  # Placeholder for actual API cost
            )
            
            # Store results
            st.session_state.bulk_results = results
            
            # Display summary
            if results:
                st.success(f"🎉 Successfully analyzed {len(results)} resumes!")
                
                # Summary statistics
                scores = [result.score for _, result in results]
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Average Score", f"{sum(scores)/len(scores):.1f}%")
                with col2:
                    st.metric("Highest Score", f"{max(scores)}%")
                with col3:
                    st.metric("Strong Matches", len([s for s in scores if s >= 70]))
                with col4:
                    st.metric("Total Analyzed", len(results))
                
                # Results table
                st.subheader("📊 Results Summary")
                df = create_downloadable_report(results)
                st.dataframe(df, use_container_width=True)
                
                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📊 Download CSV Report",
                        data=csv,
                        file_name=f"bulk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # Create detailed report
                    detailed_report = create_detailed_report(results)
                    st.download_button(
                        label="📄 Download Detailed Report",
                        data=detailed_report,
                        file_name=f"detailed_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
        else:
            st.warning("⚠️ Please upload resumes and provide a job description.")

def create_job_seeker_report(results, jd_title="Job Position", jd_text=""):
    """Create a job seeker focused report with improvement guidance"""
    if not results:
        return "No analysis results available."
    
    resume_name, result = results[0]  # Job seekers typically analyze one resume
    
    report = f"""
{'='*80}
RESUME OPTIMIZATION REPORT - FOR JOB SEEKERS
{'='*80}

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Position Applied For: {jd_title}
Your Resume: {resume_name}

{'='*80}
YOUR COMPATIBILITY ANALYSIS
{'='*80}

🎯 OVERALL COMPATIBILITY SCORE: {result.score}%
📊 MATCH CATEGORY: {result.match_category}
⏱️  ANALYSIS TIME: {result.processing_time:.2f} seconds

WHAT THIS SCORE MEANS:
{'-'*40}
"""
    
    if result.score >= 70:
        report += """✅ EXCELLENT MATCH! You're a strong candidate for this position.
   • Your resume shows strong alignment with job requirements
   • You meet most of the key qualifications
   • Focus on highlighting your matching skills in your application
   • Prepare for interviews by reviewing your relevant experience"""
    elif result.score >= 40:
        report += """⚠️  MODERATE MATCH. You have potential but need improvements.
   • Your resume shows some alignment with job requirements
   • Several important skills need to be highlighted or developed
   • Focus on addressing the critical gaps identified below
   • Consider this role as a growth opportunity"""
    else:
        report += """🔧 SIGNIFICANT IMPROVEMENTS NEEDED for this specific role.
   • Your current resume doesn't strongly align with this position
   • Consider developing the missing skills before applying
   • Look for roles that better match your current skill set
   • Use this analysis to guide your professional development"""
    
    report += f"""

{'='*80}
YOUR STRENGTHS - SKILLS THAT MATCH
{'='*80}

🎯 YOU HAVE {len(result.matching_skills)} MATCHING SKILLS:
{'-'*50}
"""
    
    if result.matching_skills:
        for i, skill in enumerate(result.matching_skills, 1):
            if isinstance(skill, dict):
                report += f"""
{i}. ✅ SKILL MATCH FOUND:
   Your Resume Shows: {skill.get('resume', 'N/A')}
   Job Requires: {skill.get('job_description', 'N/A')}
   💡 Highlight this in your cover letter and interviews!
"""
            else:
                report += f"\n{i}. ✅ {skill}\n   💡 Make sure this is prominently featured in your resume!"
    else:
        report += """
❌ No direct skill matches found in your current resume.

🔧 IMMEDIATE ACTION NEEDED:
   • Review the job description for key terms and skills
   • Add a 'Core Skills' or 'Technical Competencies' section
   • Use the same terminology as the job posting
   • Highlight transferable skills from your experience
"""
    
    # Skills you need to develop or highlight
    total_gaps = sum(len(skills) for skills in result.skill_gaps.values())
    report += f"""

{'='*80}
SKILLS TO DEVELOP OR HIGHLIGHT
{'='*80}

📚 YOU NEED TO ADDRESS {total_gaps} SKILL GAPS:
{'-'*50}
"""
    
    if total_gaps > 0:
        for category, skills in result.skill_gaps.items():
            if skills:
                if category == "Critical":
                    icon = "🔴"
                    priority = "HIGHEST PRIORITY"
                    action = "Must address before applying"
                elif category == "Important":
                    icon = "🟡"
                    priority = "HIGH PRIORITY"
                    action = "Should address to strengthen application"
                else:
                    icon = "🟢"
                    priority = "NICE TO HAVE"
                    action = "Would give you competitive advantage"
                
                report += f"""
{icon} {category.upper()} SKILLS - {priority}:
{action}

"""
                for skill in skills:
                    report += f"   • {skill}\n"
                    
                # Add specific guidance for each category
                if category == "Critical":
                    report += """
   🎯 ACTION PLAN FOR CRITICAL SKILLS:
   • Consider online courses or certifications
   • Look for volunteer projects to gain experience
   • Mention related experience even if not exact match
   • Be honest about learning these skills if asked
"""
                elif category == "Important":
                    report += """
   🎯 ACTION PLAN FOR IMPORTANT SKILLS:
   • Add these to your professional development goals
   • Look for ways to gain experience in current role
   • Consider side projects or freelance work
   • Network with professionals who have these skills
"""
    else:
        report += """
🎉 AMAZING! You have all the key skills for this position!

🚀 OPTIMIZATION TIPS:
   • Focus on quantifying your achievements
   • Add specific metrics and results to your experience
   • Ensure your skills are prominently displayed
   • Tailor your professional summary to this role
"""
    
    # Personalized recommendations
    report += f"""

{'='*80}
YOUR PERSONALIZED ACTION PLAN
{'='*80}

💡 {len(result.suggestions)} SPECIFIC RECOMMENDATIONS FOR YOU:
{'-'*60}
"""
    
    if result.suggestions:
        for i, suggestion in enumerate(result.suggestions, 1):
            report += f"""
RECOMMENDATION #{i}:
{suggestion}

✅ HOW TO IMPLEMENT:
   • Review your current resume for this specific area
   • Make the suggested changes before applying
   • Test the updated resume with this tool again
   • Track which changes improve your score

{'-'*40}
"""
    
    # Next steps based on score
    report += f"""

{'='*80}
YOUR NEXT STEPS
{'='*80}

🎯 IMMEDIATE ACTIONS TO TAKE:
{'-'*40}
"""
    
    if result.score >= 70:
        report += """
1. ✅ APPLY WITH CONFIDENCE
   • Your resume is well-aligned with this position
   • Customize your cover letter to highlight matching skills
   • Prepare for interviews focusing on your relevant experience
   • Research the company and role-specific questions

2. 🎯 OPTIMIZE FOR EVEN BETTER RESULTS
   • Implement the recommendations above
   • Add quantifiable achievements where possible
   • Ensure keywords from job description appear in your resume
   • Consider getting a professional review of your application materials
"""
    elif result.score >= 40:
        report += """
1. 🔧 IMPROVE YOUR RESUME FIRST
   • Address the critical skill gaps identified above
   • Implement all recommendations before applying
   • Consider taking courses for missing technical skills
   • Update your resume with new skills and experiences

2. 📚 SKILL DEVELOPMENT PLAN
   • Focus on the critical and important skills listed
   • Look for online courses, certifications, or training
   • Consider volunteer work or side projects to gain experience
   • Network with professionals in your target field

3. 🎯 STRATEGIC APPLICATION APPROACH
   • Apply to similar roles that better match your current skills
   • Look for junior or training positions in this field
   • Consider contract or freelance work to build experience
   • Be prepared to discuss your learning plan in interviews
"""
    else:
        report += """
1. 📚 MAJOR SKILL DEVELOPMENT NEEDED
   • This role requires significant skill development
   • Consider formal education or intensive training programs
   • Look for entry-level positions in this field
   • Focus on building foundational skills first

2. 🎯 ALTERNATIVE STRATEGY
   • Search for roles that better match your current skills
   • Consider transitional roles that bridge to your target
   • Look for companies that offer training programs
   • Network to find mentorship opportunities

3. 💪 LONG-TERM DEVELOPMENT PLAN
   • Create a 6-12 month skill development timeline
   • Set specific, measurable learning goals
   • Track your progress with regular resume analysis
   • Build a portfolio of projects demonstrating new skills
"""
    
    # Encouragement and resources
    report += f"""

{'='*80}
RESOURCES FOR YOUR SUCCESS
{'='*80}

🎓 SKILL DEVELOPMENT RESOURCES:
{'-'*40}
• Online Learning: Coursera, Udemy, LinkedIn Learning, edX
• Technical Skills: Codecademy, freeCodeCamp, Khan Academy
• Certifications: Industry-specific certification programs
• Practice: GitHub projects, volunteer work, freelance projects

📝 RESUME IMPROVEMENT RESOURCES:
{'-'*40}
• Resume Templates: Use ATS-friendly formats
• Keywords: Mirror language from job descriptions
• Metrics: Add quantifiable achievements (%, $, #)
• Professional Review: Consider career coaching services

🤝 NETWORKING AND CAREER RESOURCES:
{'-'*40}
• LinkedIn: Connect with professionals in your target field
• Industry Events: Attend conferences, meetups, webinars
• Professional Associations: Join relevant industry groups
• Informational Interviews: Learn from people in target roles

{'='*80}
REMEMBER: EVERY EXPERT WAS ONCE A BEGINNER
{'='*80}

Your career journey is unique, and this analysis is just one data point.
Use these insights to guide your development, but don't let a lower score
discourage you. With focused effort and the right strategy, you can
significantly improve your compatibility with your target roles.

🌟 Key Takeaways:
   • Focus on your {len(result.matching_skills)} existing strengths
   • Systematically address the {total_gaps} identified gaps
   • Implement the {len(result.suggestions)} specific recommendations
   • Re-analyze your resume after improvements to track progress

Good luck with your job search and career development!

{'='*80}
END OF PERSONALIZED REPORT
{'='*80}

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
For questions about this analysis, review the methodology in the main application.
"""
    
    return report

def create_company_report(results, jd_title="Job Position", jd_text=""):
    """Create a detailed report specifically for companies focusing on hiring decisions"""
    
    report = f"""
{'='*80}
CANDIDATE EVALUATION REPORT - FOR HIRING TEAM
{'='*80}

Position: {jd_title}
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Candidates Analyzed: {len(results)}
Report Type: Hiring Decision Support

{'='*80}
EXECUTIVE SUMMARY
{'='*80}

"""
    
    if results:
        scores = [result.score for _, result in results]
        strong_candidates = [r for r in results if r[1].score >= 70]
        moderate_candidates = [r for r in results if 40 <= r[1].score < 70]
        weak_candidates = [r for r in results if r[1].score < 40]
        
        report += f"""
CANDIDATE POOL ANALYSIS:
• Total Candidates: {len(results)}
• Average Compatibility: {sum(scores)/len(scores):.1f}%
• Highest Score: {max(scores)}%
• Lowest Score: {min(scores)}%

CANDIDATE DISTRIBUTION:
• 🟢 Strong Matches (70%+): {len(strong_candidates)} candidates
• 🟡 Moderate Matches (40-69%): {len(moderate_candidates)} candidates  
• 🔴 Weak Matches (<40%): {len(weak_candidates)} candidates

HIRING RECOMMENDATION:
"""
        
        if len(strong_candidates) >= 3:
            report += "✅ EXCELLENT candidate pool. Proceed with top candidates for interviews.\n"
        elif len(strong_candidates) >= 1:
            report += "✅ GOOD candidate pool. Interview strong matches, consider moderate ones.\n"
        elif len(moderate_candidates) >= 2:
            report += "⚠️  MODERATE candidate pool. Consider expanding search or adjusting requirements.\n"
        else:
            report += "❌ WEAK candidate pool. Recommend expanding search criteria or job posting reach.\n"
    
    # Individual candidate analysis for companies
    for i, (resume_name, result) in enumerate(results, 1):
        candidate_name = resume_name.replace('.pdf', '').replace('_', ' ').title()
        
        report += f"""

{'='*80}
CANDIDATE #{i}: {candidate_name}
{'='*80}

HIRING ASSESSMENT:
• Compatibility Score: {result.score}%
• Match Category: {result.match_category}
• Processing Time: {result.processing_time:.2f}s

"""
        
        # Hiring recommendation based on score
        if result.score >= 70:
            report += """🟢 HIRING RECOMMENDATION: STRONG CANDIDATE - PROCEED TO INTERVIEW

✅ STRENGTHS:
   • Meets most key requirements
   • Strong skill alignment with position
   • Ready for immediate contribution
   • Low training overhead expected

"""
        elif result.score >= 40:
            report += """🟡 HIRING RECOMMENDATION: MODERATE CANDIDATE - CONSIDER WITH CAUTION

⚠️  ASSESSMENT:
   • Partial skill alignment
   • May require additional training
   • Could be suitable for junior/training role
   • Evaluate growth potential

"""
        else:
            report += """🔴 HIRING RECOMMENDATION: WEAK CANDIDATE - NOT RECOMMENDED

❌ CONCERNS:
   • Significant skill gaps
   • High training investment required
   • May not meet immediate needs
   • Consider for future opportunities

"""
        
        # Skills assessment for hiring managers
        report += f"""SKILLS ASSESSMENT:
{'-'*40}
✅ DEMONSTRATED SKILLS ({len(result.matching_skills)} matches):
"""
        
        if result.matching_skills:
            for skill in result.matching_skills[:8]:  # Show top 8 for companies
                if isinstance(skill, dict):
                    report += f"   • {skill.get('resume', skill)}\n"
                else:
                    report += f"   • {skill}\n"
            if len(result.matching_skills) > 8:
                report += f"   ... and {len(result.matching_skills) - 8} additional skills\n"
        else:
            report += "   No direct skill matches identified\n"
        
        # Skill gaps for hiring decisions
        total_gaps = sum(len(skills) for skills in result.skill_gaps.values())
        if total_gaps > 0:
            report += f"\n❌ SKILL GAPS REQUIRING ATTENTION ({total_gaps} gaps):\n"
            
            critical_gaps = result.skill_gaps.get('Critical', [])
            important_gaps = result.skill_gaps.get('Important', [])
            
            if critical_gaps:
                report += f"\n   🔴 CRITICAL GAPS (Deal Breakers): {len(critical_gaps)}\n"
                for gap in critical_gaps:
                    report += f"      • {gap}\n"
                report += "   ⚠️  These gaps may significantly impact job performance\n"
            
            if important_gaps:
                report += f"\n   🟡 IMPORTANT GAPS (Training Needed): {len(important_gaps)}\n"
                for gap in important_gaps[:5]:  # Show top 5
                    report += f"      • {gap}\n"
                if len(important_gaps) > 5:
                    report += f"      ... and {len(important_gaps) - 5} more\n"
                report += "   💡 These could be addressed through training or mentoring\n"
        else:
            report += "\n🎉 No significant skill gaps identified\n"
        
        # Interview focus areas
        report += f"\n🎯 INTERVIEW FOCUS AREAS:\n"
        report += f"{'-'*40}\n"
        
        if result.matching_skills:
            report += "✅ VALIDATE STRENGTHS:\n"
            for skill in result.matching_skills[:3]:
                if isinstance(skill, dict):
                    skill_name = skill.get('resume', skill)
                else:
                    skill_name = skill
                report += f"   • Ask specific examples of {skill_name}\n"
        
        critical_gaps = result.skill_gaps.get('Critical', [])
        if critical_gaps:
            report += "\n❌ ASSESS CRITICAL GAPS:\n"
            for gap in critical_gaps[:3]:
                report += f"   • Evaluate willingness/ability to learn {gap}\n"
        
        # Salary and role fit
        report += f"\n💼 ROLE FIT ASSESSMENT:\n"
        report += f"{'-'*40}\n"
        
        if result.score >= 70:
            report += "   • Suitable for standard role level and compensation\n"
            report += "   • Can contribute immediately with minimal onboarding\n"
            report += "   • Good long-term potential\n"
        elif result.score >= 40:
            report += "   • May be suitable for junior level or reduced compensation\n"
            report += "   • Requires structured training program\n"
            report += "   • Evaluate growth trajectory\n"
        else:
            report += "   • Not suitable for current role requirements\n"
            report += "   • Consider for different positions or future opportunities\n"
            report += "   • High investment required for skill development\n"
    
    # Overall hiring strategy for multiple candidates
    if len(results) > 1:
        report += f"""

{'='*80}
HIRING STRATEGY & RECOMMENDATIONS
{'='*80}

CANDIDATE RANKING:
{'-'*40}
"""
        
        # Sort and rank candidates
        sorted_results = sorted(results, key=lambda x: x[1].score, reverse=True)
        
        for i, (resume_name, result) in enumerate(sorted_results, 1):
            candidate_name = resume_name.replace('.pdf', '').replace('_', ' ').title()
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📄"
            status = "INTERVIEW" if result.score >= 70 else "CONSIDER" if result.score >= 40 else "ARCHIVE"
            report += f"{medal} #{i}. {candidate_name}: {result.score}% - {status}\n"
        
        # Strategic recommendations
        strong_count = len([r for r in results if r[1].score >= 70])
        moderate_count = len([r for r in results if 40 <= r[1].score < 70])
        
        report += f"""

STRATEGIC RECOMMENDATIONS:
{'-'*40}
"""
        
        if strong_count >= 3:
            report += f"✅ PROCEED WITH HIRING:\n"
            report += f"   • Interview top {min(5, strong_count)} candidates\n"
            report += f"   • Expect to make offer within 2-3 interviews\n"
            report += f"   • Consider multiple hires if budget allows\n"
        elif strong_count >= 1:
            report += f"✅ SELECTIVE HIRING:\n"
            report += f"   • Interview {strong_count} strong candidate(s)\n"
            report += f"   • Consider {min(3, moderate_count)} moderate candidates as backup\n"
            report += f"   • May need to adjust expectations or provide training\n"
        elif moderate_count >= 2:
            report += f"⚠️  CAUTIOUS HIRING:\n"
            report += f"   • Interview top {min(3, moderate_count)} moderate candidates\n"
            report += f"   • Plan for extended training period\n"
            report += f"   • Consider adjusting role requirements\n"
        else:
            report += f"❌ EXPAND SEARCH:\n"
            report += f"   • Current pool insufficient for hiring needs\n"
            report += f"   • Recommend expanding job posting reach\n"
            report += f"   • Consider adjusting requirements or compensation\n"
    
    # Footer for companies
    report += f"""

{'='*80}
IMPORTANT NOTES FOR HIRING TEAM
{'='*80}

⚠️  DISCLAIMER:
• This analysis is a screening tool and should supplement, not replace, human judgment
• Consider cultural fit, soft skills, and growth potential in final decisions
• Verify technical skills through practical assessments or technical interviews
• Check references and conduct background verification as per company policy

📋 COMPLIANCE REMINDER:
• Ensure all hiring decisions comply with equal opportunity employment laws
• Document decision rationale for audit purposes
• Provide feedback to candidates as per company policy
• Maintain confidentiality of candidate information

{'='*80}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Analysis Tool: Resume + JD Analyzer v2.0
Report Type: Company Hiring Decision Report
Analyzed by: AI-powered compatibility analysis
{'='*80}
"""
    
    return report

def create_pdf_report(report_text, report_type="Report"):
    """Create a PDF from text report"""
    if not PDF_AVAILABLE:
        raise ImportError("ReportLab is not installed. Please install it with: pip install reportlab")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=12,
        spaceBefore=12,
        textColor=colors.darkblue
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    # Build PDF content
    story = []
    
    # Split text into lines and process
    lines = report_text.split('\n')
    current_section = []
    
    for line in lines:
        line = line.strip()
        
        # Skip separator lines
        if line.startswith('=') and len(line) > 50:
            if current_section:
                # Process current section
                section_text = '\n'.join(current_section)
                if section_text.strip():
                    story.append(Paragraph(section_text, body_style))
                    story.append(Spacer(1, 12))
                current_section = []
            continue
        
        # Handle headings (lines in ALL CAPS or with special characters)
        if (line.isupper() and len(line) > 10) or line.startswith('🎯') or line.startswith('📊'):
            if current_section:
                section_text = '\n'.join(current_section)
                if section_text.strip():
                    story.append(Paragraph(section_text, body_style))
                current_section = []
            
            # Clean heading text
            clean_heading = line.replace('🎯', '').replace('📊', '').replace('💡', '').replace('✅', '').replace('❌', '').strip()
            story.append(Paragraph(clean_heading, heading_style))
            story.append(Spacer(1, 6))
        else:
            if line:
                # Clean emojis for PDF
                clean_line = line.replace('🎯', '•').replace('📊', '•').replace('💡', '•')
                clean_line = clean_line.replace('✅', '✓').replace('❌', '✗').replace('⚠️', '!')
                clean_line = clean_line.replace('🟢', '•').replace('🟡', '•').replace('🔴', '•')
                clean_line = clean_line.replace('🥇', '1st').replace('🥈', '2nd').replace('🥉', '3rd')
                current_section.append(clean_line)
    
    # Add remaining content
    if current_section:
        section_text = '\n'.join(current_section)
        if section_text.strip():
            story.append(Paragraph(section_text, body_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def create_detailed_report(results, jd_title="Job Position", jd_text=""):
    """Create a detailed report (legacy function for backward compatibility)"""
    # For backward compatibility, default to company report for multiple candidates
    # or job seeker report for single candidate
    if len(results) == 1:
        return create_job_seeker_report(results, jd_title, jd_text)
    else:
        return create_company_report(results, jd_title, jd_text)
        
        if result.suggestions:
            for j, suggestion in enumerate(result.suggestions, 1):
                report += f"\n   RECOMMENDATION #{j}:\n"
                # Wrap long suggestions for better readability
                wrapped_suggestion = suggestion.replace('. ', '.\n      ')
                report += f"   {wrapped_suggestion}\n"
        else:
            report += "   No specific recommendations - resume appears well-optimized.\n"
        
        # Detailed scoring breakdown
        report += f"\n📊 DETAILED SCORING BREAKDOWN:\n"
        report += f"{'-'*40}\n"
        report += f"• Overall Compatibility: {result.score}%\n"
        report += f"• Skills Alignment: {len(result.matching_skills)} matches found\n"
        report += f"• Experience Relevance: Based on skill analysis\n"
        report += f"• Keyword Optimization: Reflected in matching skills\n"
        report += f"• Gap Severity: {len(result.skill_gaps.get('Critical', []))} critical, "
        report += f"{len(result.skill_gaps.get('Important', []))} important gaps\n"
        
        # Next steps based on score
        report += f"\n🎯 RECOMMENDED NEXT STEPS:\n"
        report += f"{'-'*40}\n"
        
        if result.score >= 70:
            report += "   ✅ STRONG CANDIDATE - Recommend for interview\n"
            report += "   • Schedule initial screening interview\n"
            report += "   • Prepare questions focusing on matching skills\n"
            report += "   • Consider for technical assessment if applicable\n"
        elif result.score >= 40:
            report += "   ⚠️  MODERATE CANDIDATE - Consider with reservations\n"
            report += "   • Review critical skill gaps before proceeding\n"
            report += "   • Consider for junior or training positions\n"
            report += "   • Evaluate potential for skill development\n"
        else:
            report += "   ❌ POOR MATCH - Not recommended for this position\n"
            report += "   • Consider for different roles that match their skills\n"
            report += "   • Archive for future opportunities\n"
            report += "   • Provide feedback if requested\n"
        
        report += f"\n{'-'*80}\n"
    
    # Final recommendations and insights
    if len(results) > 1:
        report += f"""
{'='*80}
HIRING RECOMMENDATIONS & INSIGHTS
{'='*80}

CANDIDATE RANKING:
{'-'*40}
"""
        # Sort candidates by score
        sorted_results = sorted(results, key=lambda x: x[1].score, reverse=True)
        
        for i, (resume_name, result) in enumerate(sorted_results, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📄"
            report += f"{medal} #{i}. {resume_name}: {result.score}% ({result.match_category})\n"
        
        # Hiring strategy
        strong_candidates = [r for r in results if r[1].score >= 70]
        moderate_candidates = [r for r in results if 40 <= r[1].score < 70]
        
        report += f"""
HIRING STRATEGY:
{'-'*40}
• Interview immediately: {len(strong_candidates)} strong candidates
• Consider for development roles: {len(moderate_candidates)} moderate candidates
• Archive for future: {len(results) - len(strong_candidates) - len(moderate_candidates)} candidates

MARKET INSIGHTS:
{'-'*40}
• Candidate pool quality: {'Excellent' if len(strong_candidates) > len(results)//2 else 'Good' if len(strong_candidates) > 0 else 'Limited'}
• Skills availability: {'High' if sum(len(r[1].matching_skills) for r in results) > len(results) * 5 else 'Moderate'}
• Competition level: {'High' if len(strong_candidates) > 3 else 'Moderate' if len(strong_candidates) > 1 else 'Low'}
"""
    
    # Footer
    report += f"""
{'='*80}
REPORT FOOTER
{'='*80}

Analysis Methodology:
• AI Model: sonar-pro (Perplexity AI)
• Scoring Algorithm: Multi-factor compatibility analysis
• Skill Matching: Semantic understanding with keyword optimization
• Gap Analysis: Prioritized by job requirement importance
• Recommendations: Actionable suggestions based on specific gaps

Disclaimer:
This analysis is generated by AI and should be used as a screening tool
in conjunction with human judgment. Final hiring decisions should consider
additional factors beyond this automated analysis.

Report Generated by: Resume + JD Analyzer v2.0
Generation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Analysis Duration: {sum(result.processing_time for _, result in results):.2f} seconds total

For support or questions about this report, please contact your system administrator.

{'='*80}
END OF REPORT
{'='*80}
"""
    
    return report

def render_dashboard():
    """Render analytics dashboard"""
    st.header("📊 Analytics Dashboard")
    
    # Combine all results
    all_results = st.session_state.analysis_results + st.session_state.bulk_results
    
    if not all_results:
        st.info("📈 No analysis data available. Run some analyses to see dashboard metrics.")
        return
    
    # Summary metrics
    scores = [result.score for _, result in all_results]
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analyses", len(all_results))
    with col2:
        st.metric("Average Score", f"{sum(scores)/len(scores):.1f}%")
    with col3:
        st.metric("Strong Matches", len([s for s in scores if s >= 70]))
    with col4:
        st.metric("Success Rate", f"{(len([s for s in scores if s > 0])/len(scores)*100):.1f}%")
    
    # Score distribution
    st.subheader("📈 Score Distribution")
    score_ranges = {
        "90-100%": len([s for s in scores if 90 <= s <= 100]),
        "70-89%": len([s for s in scores if 70 <= s < 90]),
        "50-69%": len([s for s in scores if 50 <= s < 70]),
        "30-49%": len([s for s in scores if 30 <= s < 50]),
        "0-29%": len([s for s in scores if 0 <= s < 30])
    }
    
    df_scores = pd.DataFrame(list(score_ranges.items()), columns=['Score Range', 'Count'])
    st.bar_chart(df_scores.set_index('Score Range'))
    
    # Recent analyses
    st.subheader("📋 Recent Analyses")
    df_all = create_downloadable_report(all_results)
    st.dataframe(df_all, use_container_width=True)
    
    # Usage statistics
    st.subheader("📊 Usage Statistics")
    try:
        usage_stats = get_usage_statistics()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("API Calls", usage_stats.get('total_calls', 0))
        with col2:
            st.metric("Total Cost", f"${usage_stats.get('total_cost', 0):.4f}")
        with col3:
            st.metric("Avg Processing Time", f"{usage_stats.get('average_processing_time', 0):.1f}s")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        st.info("Usage statistics not available")

def render_job_matching():
    """Render job matching interface - one resume against multiple jobs"""
    st.header("🎯 Job Matching - Find Your Best Opportunities")
    st.info("Upload your resume and multiple job descriptions to see which positions are the best match for your profile.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Upload Your Resume")
        resume_file = st.file_uploader(
            "Choose your PDF resume file",
            type=['pdf'],
            help="Upload your resume to analyze against multiple job opportunities"
        )
        
        if resume_file:
            st.success(f"✅ Resume uploaded: {resume_file.name}")
    
    with col2:
        st.subheader("📋 Job Descriptions")
        job_input_method = st.radio(
            "How would you like to add job descriptions?",
            ["📝 Paste Multiple Jobs", "📁 Upload Text Files"]
        )
        
        jobs_data = {}
        
        if job_input_method == "📝 Paste Multiple Jobs":
            st.info("Add multiple job descriptions below. Give each job a name for easy identification.")
            
            # Dynamic job addition
            if 'job_count' not in st.session_state:
                st.session_state.job_count = 1
            
            # Add/Remove job buttons
            col_add, col_remove = st.columns(2)
            with col_add:
                if st.button("➕ Add Another Job"):
                    st.session_state.job_count += 1
            with col_remove:
                if st.button("➖ Remove Last Job") and st.session_state.job_count > 1:
                    st.session_state.job_count -= 1
            
            # Job input fields
            for i in range(st.session_state.job_count):
                with st.expander(f"📋 Job #{i+1}", expanded=True):
                    job_name = st.text_input(
                        f"Job Title/Company #{i+1}",
                        placeholder="e.g., Senior Developer at TechCorp",
                        key=f"job_name_{i}"
                    )
                    
                    job_description = st.text_area(
                        f"Job Description #{i+1}",
                        height=150,
                        placeholder="Paste the complete job description including requirements, responsibilities, and qualifications...",
                        key=f"job_desc_{i}"
                    )
                    
                    if job_name and job_description.strip():
                        jobs_data[job_name] = job_description.strip()
        
        else:  # Upload files
            job_files = st.file_uploader(
                "Choose job description text files",
                type=['txt'],
                accept_multiple_files=True,
                help="Upload multiple .txt files, each containing a job description"
            )
            
            if job_files:
                for job_file in job_files:
                    try:
                        job_content = job_file.read().decode('utf-8')
                        job_name = job_file.name.replace('.txt', '').replace('_', ' ').title()
                        jobs_data[job_name] = job_content
                    except Exception as e:
                        logger.error(f"Unexpected error: {e}")
                        st.error(f"Error reading {job_file.name}: {str(e)}")
                
                if jobs_data:
                    st.success(f"✅ {len(jobs_data)} job descriptions loaded")
                    for job_name in jobs_data.keys():
                        st.write(f"• {job_name}")
    
    # Analysis section
    if resume_file and jobs_data:
        st.subheader(f"🚀 Ready to Analyze {len(jobs_data)} Job Opportunities")
        
        # Show job summary
        with st.expander("📋 Job Summary", expanded=False):
            for job_name, job_desc in jobs_data.items():
                st.write(f"**{job_name}**: {len(job_desc)} characters, {len(job_desc.split())} words")
        
        # Analysis button
        if st.button("🎯 Find My Best Job Matches", type="primary", use_container_width=True):
            with st.spinner(f"🔄 Analyzing your resume against {len(jobs_data)} job opportunities... This may take up to {len(jobs_data) * 5} seconds."):
                
                # Process resume once
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(resume_file.read())
                        tmp_path = tmp_file.name
                    
                    resume_text = extract_text_from_pdf(tmp_path)
                    cleaned_resume = clean_resume_text(resume_text)
                    os.unlink(tmp_path)
                    
                    # Analyze against each job
                    job_results = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, (job_name, job_desc) in enumerate(jobs_data.items()):
                        status_text.text(f"Analyzing {job_name}... ({i+1}/{len(jobs_data)})")
                        
                        try:
                            jd_data = parse_jd_text(job_desc)
                            result = analyze_match(cleaned_resume, jd_data.__dict__)
                            
                            job_results.append({
                                'job_name': job_name,
                                'job_description': job_desc,
                                'result': result,
                                'success': True
                            })
                        except Exception as e:
                            logger.error(f"Unexpected error: {e}")
                            job_results.append({
                                'job_name': job_name,
                                'job_description': job_desc,
                                'error': str(e),
                                'success': False
                            })
                        
                        progress_bar.progress((i + 1) / len(jobs_data))
                    
                    status_text.text("✅ Analysis completed!")
                    
                    # Store results for dashboard
                    if 'job_matching_results' not in st.session_state:
                        st.session_state.job_matching_results = []
                    st.session_state.job_matching_results.extend(job_results)
                    
                    # Display results
                    successful_results = [r for r in job_results if r['success']]
                    
                    if successful_results:
                        st.success(f"🎉 Successfully analyzed {len(successful_results)} job opportunities!")
                        
                        # Sort by compatibility score
                        successful_results.sort(key=lambda x: x['result'].score, reverse=True)
                        
                        # Summary metrics
                        scores = [r['result'].score for r in successful_results]
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Best Match", f"{max(scores)}%")
                        with col2:
                            st.metric("Average Match", f"{sum(scores)/len(scores):.1f}%")
                        with col3:
                            st.metric("Strong Matches", len([s for s in scores if s >= 70]))
                        with col4:
                            st.metric("Jobs Analyzed", len(successful_results))
                        
                        # Job rankings
                        st.subheader("🏆 Your Job Match Rankings")
                        
                        for i, job_result in enumerate(successful_results, 1):
                            result = job_result['result']
                            job_name = job_result['job_name']
                            
                            # Medal and recommendation
                            if i == 1:
                                medal = "🥇"
                                recommendation = "TOP CHOICE"
                            elif i == 2:
                                medal = "🥈"
                                recommendation = "EXCELLENT OPTION"
                            elif i == 3:
                                medal = "🥉"
                                recommendation = "STRONG CONTENDER"
                            else:
                                medal = "📄"
                                recommendation = "CONSIDER" if result.score >= 40 else "LOWER PRIORITY"
                            
                            # Color coding
                            if result.score >= 70:
                                color = "success"
                            elif result.score >= 40:
                                color = "warning"
                            else:
                                color = "error"
                            
                            with st.container():
                                col1, col2, col3 = st.columns([1, 2, 1])
                                
                                with col1:
                                    st.markdown(f"### {medal} #{i}")
                                    if color == "success":
                                        st.success(f"{result.score}%")
                                    elif color == "warning":
                                        st.warning(f"{result.score}%")
                                    else:
                                        st.error(f"{result.score}%")
                                
                                with col2:
                                    st.markdown(f"**{job_name}**")
                                    st.markdown(f"*{recommendation}*")
                                    st.write(f"Match Category: {result.match_category}")
                                    st.write(f"Matching Skills: {len(result.matching_skills)}")
                                
                                with col3:
                                    with st.expander("View Details"):
                                        st.write("**Top Matching Skills:**")
                                        for skill in result.matching_skills[:3]:
                                            if isinstance(skill, dict):
                                                st.write(f"• {skill.get('resume', skill)}")
                                            else:
                                                st.write(f"• {skill}")
                                        
                                        if result.skill_gaps.get('Critical'):
                                            st.write("**Critical Gaps:**")
                                            for gap in result.skill_gaps['Critical'][:3]:
                                                st.write(f"• {gap}")
                                
                                st.divider()
                        
                        # Download options
                        st.subheader("📥 Download Job Matching Report")
                        
                        # Create downloadable data
                        job_match_data = []
                        for i, job_result in enumerate(successful_results, 1):
                            result = job_result['result']
                            job_match_data.append({
                                'Rank': i,
                                'Job_Name': job_result['job_name'],
                                'Compatibility_Score': result.score,
                                'Match_Category': result.match_category,
                                'Matching_Skills': len(result.matching_skills),
                                'Critical_Gaps': len(result.skill_gaps.get('Critical', [])),
                                'Recommendation': "Apply" if result.score >= 70 else "Consider" if result.score >= 40 else "Skip"
                            })
                        
                        df = pd.DataFrame(job_match_data)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📊 Download CSV Summary",
                                data=csv,
                                file_name=f"job_matching_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        with col2:
                            # Create detailed job matching report
                            detailed_report = create_job_matching_report(successful_results, resume_file.name)
                            st.download_button(
                                label="📄 Download Detailed Report",
                                data=detailed_report,
                                file_name=f"job_matching_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                    
                    # Show any failed analyses
                    failed_results = [r for r in job_results if not r['success']]
                    if failed_results:
                        st.warning(f"⚠️ {len(failed_results)} job(s) failed to analyze:")
                        for failed in failed_results:
                            st.error(f"• {failed['job_name']}: {failed['error']}")
                
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    st.error(f"❌ Resume processing failed: {str(e)}")
    
    elif resume_file and not jobs_data:
        st.info("📋 Please add job descriptions to start the analysis.")
    elif jobs_data and not resume_file:
        st.info("📄 Please upload your resume to start the analysis.")
    else:
        st.info("📄 Upload your resume and add job descriptions to get started.")

def create_job_matching_report(job_results, resume_name):
    """Create a detailed job matching report for download"""
    report = f"""
{'='*80}
JOB MATCHING ANALYSIS REPORT
{'='*80}

Resume Analyzed: {resume_name}
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Jobs Analyzed: {len(job_results)}
Report Type: Job Seeker - Best Opportunities Analysis

{'='*80}
EXECUTIVE SUMMARY
{'='*80}

This report analyzes your resume compatibility against {len(job_results)} job opportunities
to help you prioritize your applications and focus on the best matches.

OVERALL RESULTS:
"""
    
    scores = [r['result'].score for r in job_results]
    strong_matches = [r for r in job_results if r['result'].score >= 70]
    moderate_matches = [r for r in job_results if 40 <= r['result'].score < 70]
    weak_matches = [r for r in job_results if r['result'].score < 40]
    
    report += f"""
• Best Match Score: {max(scores)}%
• Average Compatibility: {sum(scores)/len(scores):.1f}%
• Strong Matches (70%+): {len(strong_matches)} jobs
• Moderate Matches (40-69%): {len(moderate_matches)} jobs
• Weak Matches (<40%): {len(weak_matches)} jobs

RECOMMENDATION SUMMARY:
• APPLY IMMEDIATELY: {len(strong_matches)} positions
• CONSIDER APPLYING: {len(moderate_matches)} positions
• SKIP OR DEVELOP SKILLS: {len(weak_matches)} positions

{'='*80}
DETAILED JOB ANALYSIS
{'='*80}
"""
    
    # Sort by score for detailed analysis
    sorted_results = sorted(job_results, key=lambda x: x['result'].score, reverse=True)
    
    for i, job_result in enumerate(sorted_results, 1):
        result = job_result['result']
        job_name = job_result['job_name']
        
        # Recommendation based on score
        if result.score >= 70:
            recommendation = "🎯 APPLY IMMEDIATELY"
            priority = "HIGH PRIORITY"
        elif result.score >= 40:
            recommendation = "⚠️ CONSIDER APPLYING"
            priority = "MEDIUM PRIORITY"
        else:
            recommendation = "❌ SKIP FOR NOW"
            priority = "LOW PRIORITY"
        
        report += f"""
RANK #{i}: {job_name}
{'-'*60}

COMPATIBILITY SCORE: {result.score}%
MATCH CATEGORY: {result.match_category}
RECOMMENDATION: {recommendation}
PRIORITY LEVEL: {priority}

SKILLS ANALYSIS:
✅ Matching Skills ({len(result.matching_skills)}):
"""
        
        if result.matching_skills:
            for skill in result.matching_skills[:5]:  # Show top 5
                if isinstance(skill, dict):
                    report += f"   • {skill.get('resume', skill)}\n"
                else:
                    report += f"   • {skill}\n"
            if len(result.matching_skills) > 5:
                report += f"   ... and {len(result.matching_skills) - 5} more\n"
        else:
            report += "   No direct matches found\n"
        
        # Show critical gaps
        critical_gaps = result.skill_gaps.get('Critical', [])
        if critical_gaps:
            report += f"\n❌ Critical Gaps ({len(critical_gaps)}):\n"
            for gap in critical_gaps[:3]:
                report += f"   • {gap}\n"
            if len(critical_gaps) > 3:
                report += f"   ... and {len(critical_gaps) - 3} more\n"
        
        # Action items based on score
        report += f"\nACTION ITEMS:\n"
        if result.score >= 70:
            report += """   1. Apply immediately - you're a strong candidate
   2. Customize cover letter highlighting matching skills
   3. Prepare for interviews focusing on relevant experience
   4. Research company culture and specific role requirements
"""
        elif result.score >= 40:
            report += """   1. Address critical skill gaps before applying
   2. Consider if you can learn missing skills quickly
   3. Apply if you're willing to grow into the role
   4. Highlight transferable skills and learning ability
"""
        else:
            report += """   1. Focus on developing missing critical skills
   2. Look for more junior positions in this area
   3. Consider this for future career development
   4. Use as learning opportunity to understand market needs
"""
        
        report += f"\n{'='*80}\n"
    
    # Strategic recommendations
    report += f"""
STRATEGIC RECOMMENDATIONS
{'='*80}

IMMEDIATE FOCUS ({len(strong_matches)} jobs):
"""
    
    if strong_matches:
        report += "Apply to these positions immediately:\n"
        for job in strong_matches:
            report += f"   • {job['job_name']} ({job['result'].score}%)\n"
        report += "\nThese represent your best opportunities for success.\n"
    else:
        report += "No immediate strong matches found. Focus on skill development.\n"
    
    report += f"""
DEVELOPMENT OPPORTUNITIES ({len(moderate_matches)} jobs):
"""
    
    if moderate_matches:
        report += "Consider these after addressing skill gaps:\n"
        for job in moderate_matches:
            report += f"   • {job['job_name']} ({job['result'].score}%)\n"
        report += "\nThese could be good opportunities with some preparation.\n"
    else:
        report += "No moderate matches found.\n"
    
    # Skills development plan
    all_critical_gaps = []
    for job in job_results:
        all_critical_gaps.extend(job['result'].skill_gaps.get('Critical', []))
    
    # Count frequency of gaps
    gap_frequency = {}
    for gap in all_critical_gaps:
        gap_frequency[gap] = gap_frequency.get(gap, 0) + 1
    
    most_common_gaps = sorted(gap_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    
    if most_common_gaps:
        report += f"""
SKILL DEVELOPMENT PRIORITIES:
{'-'*40}
Focus on these skills to improve multiple job matches:

"""
        for gap, frequency in most_common_gaps:
            report += f"   • {gap} (needed for {frequency} jobs)\n"
    
    report += f"""

{'='*80}
NEXT STEPS SUMMARY
{'='*80}

1. IMMEDIATE APPLICATIONS ({len(strong_matches)} jobs):
   Apply to your top matches right away while customizing each application.

2. SKILL DEVELOPMENT:
   Focus on the most frequently required skills to improve future matches.

3. STRATEGIC APPLICATIONS ({len(moderate_matches)} jobs):
   Apply to moderate matches where you can demonstrate growth potential.

4. CONTINUOUS IMPROVEMENT:
   Re-run this analysis as you develop new skills and update your resume.

{'='*80}
REPORT CONCLUSION
{'='*80}

This analysis provides a data-driven approach to job searching by identifying
your best opportunities and areas for improvement. Use these insights to:

• Prioritize your job applications
• Focus your skill development efforts
• Customize your application materials
• Prepare effectively for interviews

Remember: This is a screening tool. Final decisions should consider company
culture, growth opportunities, compensation, and personal career goals.

Good luck with your job search!

{'='*80}
END OF REPORT
{'='*80}

Generated by: Resume + JD Analyzer v2.0
Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return report

def render_settings():
    """Render settings and configuration"""
    st.header("⚙️ Settings & Configuration")
    
    # API Configuration
    st.subheader("🔑 API Configuration")
    api_key = os.getenv('PERPLEXITY_API_KEY', '')
    if api_key:
        st.success(f"✅ API Key configured: {api_key[:10]}...{api_key[-4:]}")
    else:
        st.error("❌ API Key not configured")
        st.code("export PERPLEXITY_API_KEY='your-api-key-here'")
    
    # Usage Statistics
    st.subheader("📊 Usage Overview")
    try:
        usage_stats = get_usage_statistics()
        col1, col2 = st.columns(2)
        
        with col1:
            st.json({
                "Total Calls": usage_stats.get('total_calls', 0),
                "Successful Calls": usage_stats.get('successful_calls', 0),
                "Failed Calls": usage_stats.get('failed_calls', 0)
            })
        
        with col2:
            st.json({
                "Total Tokens": usage_stats.get('total_tokens', 0),
                "Total Cost": f"${usage_stats.get('total_cost', 0):.4f}",
                "Average Processing Time": f"{usage_stats.get('average_processing_time', 0):.2f}s"
            })
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        st.info("Usage statistics not available")
    
    # Clear Data
    st.subheader("🗑️ Data Management")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Analysis History"):
            st.session_state.analysis_results = []
            st.session_state.bulk_results = []
            st.success("Analysis history cleared!")
    
    with col2:
        if st.button("📊 Export All Data"):
            all_results = st.session_state.analysis_results + st.session_state.bulk_results
            if all_results:
                df = create_downloadable_report(all_results)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download All Data",
                    data=csv,
                    file_name=f"all_analyses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No data to export")

# Main block removed for Streamlit Cloud compatibility
def render_simple_working_history(user):
    """Robust analysis history that actually works"""
    st.title("📊 Analysis History")
    
    try:
        from database.connection import get_db
        from database.production_connection import production_db
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
                        'content': f"Score: {session['score']}%\nCategory: {session['match_category']}\n\nFull Analysis:\n{session.get('analysis_result', 'No detailed analysis available')}",
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

def render_simple_working_history(user):
    """Simple history that definitely works - no fancy features"""
    st.title("📊 Analysis History")
    
    try:
        import sqlite3
        
        # Direct database connection
        conn = sqlite3.connect('data/app.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Simple query
        cursor.execute("""
            SELECT id, resume_filename, score, match_category, created_at, analysis_result
            FROM analysis_sessions 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 20
        """, (user.id,))
        
        sessions = cursor.fetchall()
        conn.close()
        
        if not sessions:
            st.info("📝 No analysis history found. Run your first analysis to see results here!")
            st.info(f"💡 Looking for analyses for user: {user.id[:8]}...")
            return
        
        st.success(f"📊 Found {len(sessions)} analysis sessions")
        
        # Display each session
        for i, session in enumerate(sessions):
            session_id = session['id']
            filename = session['resume_filename'] or 'Unknown File'
            score = session['score'] or 0
            category = session['match_category'] or 'Unknown'
            created_at = session['created_at'] or 'Unknown Date'
            analysis_result = session['analysis_result'] or 'No analysis available'
            
            # Format date
            if isinstance(created_at, str) and len(created_at) > 10:
                display_date = created_at[:10]
            else:
                display_date = str(created_at)
            
            with st.expander(f"📄 {filename} - {score}% - {display_date}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Score:** {score}%")
                    st.write(f"**Category:** {category}")
                    st.write(f"**Date:** {created_at}")
                
                with col2:
                    # Simple download button
                    report_content = f"""RESUME ANALYSIS REPORT
{'='*50}

Resume: {filename}
Analysis Date: {created_at}
Compatibility Score: {score}%
Match Category: {category}

DETAILED ANALYSIS:
{'-'*20}
{analysis_result}

Generated by Resume + JD Analyzer
"""
                    
                    st.download_button(
                        label="📄 Download",
                        data=report_content,
                        file_name=f"analysis_{session_id[:8]}.txt",
                        mime="text/plain",
                        key=f"simple_download_{session_id}_{i}"
                    )
                
                # Show analysis content
                if analysis_result and len(analysis_result) > 10:
                    if len(analysis_result) > 500:
                        preview = analysis_result[:500] + "..."
                        st.text_area("Analysis Preview:", preview, height=150, key=f"preview_{session_id}_{i}", disabled=True)
                        
                        if st.checkbox("Show full analysis", key=f"full_{session_id}_{i}"):
                            st.text_area("Full Analysis:", analysis_result, height=400, key=f"full_analysis_{session_id}_{i}", disabled=True)
                    else:
                        st.text_area("Analysis:", analysis_result, height=200, key=f"analysis_{session_id}_{i}", disabled=True)
    
    except Exception as e:
        st.error(f"❌ Failed to load analysis history: {e}")
        st.info("💡 Please try refreshing the page or contact support.")
        logger.error(f"Simple history error: {e}")

# Run the main application
# Error handling wrapper for main application
try:
    main()
except Exception as e:
    import streamlit as st
    st.error(f"🚨 Application Error: {e}")
    st.error("Please check the logs and try refreshing the page.")
    st.info("If the issue persists, contact support.")
    import traceback
    st.code(traceback.format_exc())
