"""
Admin dashboard for business metrics and analytics
Provides real-time revenue, subscription, and user engagement metrics
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import pandas as pd
import streamlit as st
from database.connection import get_db
from auth.services import user_service, subscription_service, analytics_service
from auth.models import UserRole, PlanType, SubscriptionStatus

logger = logging.getLogger(__name__)

@dataclass
class BusinessMetrics:
    """Container for business metrics"""
    # Revenue metrics
    mrr: float  # Monthly Recurring Revenue
    arr: float  # Annual Recurring Revenue
    total_revenue: float
    revenue_growth_rate: float
    
    # User metrics
    total_users: int
    active_users: int
    new_users_this_month: int
    user_growth_rate: float
    
    # Subscription metrics
    total_subscriptions: int
    paid_subscriptions: int
    free_users: int
    churn_rate: float
    
    # Usage metrics
    total_analyses: int
    analyses_this_month: int
    avg_analyses_per_user: float
    
    # Conversion metrics
    free_to_paid_conversion: float
    trial_to_paid_conversion: float

class AdminDashboardService:
    """Service for admin dashboard data and metrics"""
    
    def __init__(self):
        self.db = get_db()
    
    def get_business_metrics(self, days: int = 30) -> BusinessMetrics:
        """Get comprehensive business metrics"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Revenue metrics
        revenue_data = self._get_revenue_metrics(since_date)
        
        # User metrics
        user_data = self._get_user_metrics(since_date)
        
        # Subscription metrics
        subscription_data = self._get_subscription_metrics(since_date)
        
        # Usage metrics
        usage_data = self._get_usage_metrics(since_date)
        
        # Conversion metrics
        conversion_data = self._get_conversion_metrics(since_date)
        
        return BusinessMetrics(
            # Revenue
            mrr=revenue_data['mrr'],
            arr=revenue_data['arr'],
            total_revenue=revenue_data['total_revenue'],
            revenue_growth_rate=revenue_data['growth_rate'],
            
            # Users
            total_users=user_data['total_users'],
            active_users=user_data['active_users'],
            new_users_this_month=user_data['new_users'],
            user_growth_rate=user_data['growth_rate'],
            
            # Subscriptions
            total_subscriptions=subscription_data['total_subscriptions'],
            paid_subscriptions=subscription_data['paid_subscriptions'],
            free_users=subscription_data['free_users'],
            churn_rate=subscription_data['churn_rate'],
            
            # Usage
            total_analyses=usage_data['total_analyses'],
            analyses_this_month=usage_data['analyses_this_month'],
            avg_analyses_per_user=usage_data['avg_per_user'],
            
            # Conversion
            free_to_paid_conversion=conversion_data['free_to_paid'],
            trial_to_paid_conversion=conversion_data['trial_to_paid']
        )
    
    def get_revenue_breakdown(self, days: int = 30) -> Dict[str, Any]:
        """Get detailed revenue breakdown by plan type"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        query = """
            SELECT 
                sp.plan_type,
                sp.name as plan_name,
                COUNT(s.id) as subscription_count,
                SUM(sp.price_monthly) as monthly_revenue,
                SUM(sp.price_annual / 12) as annualized_monthly_revenue
            FROM subscriptions s
            JOIN subscription_plans sp ON s.plan_id = sp.id
            WHERE s.status = 'active' AND s.created_at >= %s
            GROUP BY sp.plan_type, sp.name
            ORDER BY monthly_revenue DESC
        """
        
        results = self.db.execute_query(query, (since_date,))
        
        revenue_by_plan = {}
        total_mrr = 0
        
        for row in results:
            plan_type = row['plan_type']
            revenue_by_plan[plan_type] = {
                'plan_name': row['plan_name'],
                'subscription_count': row['subscription_count'],
                'monthly_revenue': row['monthly_revenue'] or 0,
                'annualized_monthly_revenue': row['annualized_monthly_revenue'] or 0
            }
            total_mrr += row['monthly_revenue'] or 0
        
        return {
            'total_mrr': total_mrr,
            'revenue_by_plan': revenue_by_plan,
            'period_days': days
        }
    
    def get_user_acquisition_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get user acquisition and churn metrics"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # New users by day
        new_users_query = """
            SELECT 
                DATE(created_at) as signup_date,
                COUNT(*) as new_users
            FROM users 
            WHERE created_at >= %s AND is_active = TRUE
            GROUP BY DATE(created_at)
            ORDER BY signup_date
        """
        
        new_users_results = self.db.execute_query(new_users_query, (since_date,))
        
        # Churn analysis (users who cancelled subscriptions)
        churn_query = """
            SELECT 
                DATE(cancelled_at) as churn_date,
                COUNT(*) as churned_users
            FROM subscriptions 
            WHERE cancelled_at >= %s AND cancelled_at IS NOT NULL
            GROUP BY DATE(cancelled_at)
            ORDER BY churn_date
        """
        
        churn_results = self.db.execute_query(churn_query, (since_date,))
        
        # Calculate Customer Acquisition Cost (CAC) - placeholder
        # In production, this would integrate with marketing spend data
        total_new_users = sum(row['new_users'] for row in new_users_results)
        estimated_marketing_spend = total_new_users * 25  # $25 estimated CAC
        
        return {
            'new_users_by_day': [
                {'date': row['signup_date'], 'count': row['new_users']}
                for row in new_users_results
            ],
            'churn_by_day': [
                {'date': row['churn_date'], 'count': row['churned_users']}
                for row in churn_results
            ],
            'total_new_users': total_new_users,
            'estimated_cac': 25,  # Placeholder
            'estimated_marketing_spend': estimated_marketing_spend
        }
    
    def get_feature_usage_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get feature usage analytics"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Analysis session types
        session_types_query = """
            SELECT 
                session_type,
                COUNT(*) as session_count,
                COUNT(DISTINCT user_id) as unique_users,
                AVG(processing_time_seconds) as avg_processing_time,
                COUNT(*) as total_resumes
            FROM analysis_sessions 
            WHERE created_at >= %s AND status = 'completed'
            GROUP BY session_type
            ORDER BY session_count DESC
        """
        
        session_results = self.db.execute_query(session_types_query, (since_date,))
        
        # Feature usage from analytics events
        feature_usage_query = """
            SELECT 
                JSON_EXTRACT(parameters, '$.feature_name') as feature_name,
                COUNT(*) as usage_count,
                COUNT(DISTINCT user_id) as unique_users
            FROM analytics_events 
            WHERE event_name = 'feature_used' 
            AND timestamp >= %s
            GROUP BY JSON_EXTRACT(parameters, '$.feature_name')
            ORDER BY usage_count DESC
        """
        
        try:
            feature_results = self.db.execute_query(feature_usage_query, (since_date,))
        except:
            # Fallback if analytics_events table doesn't exist yet
            feature_results = []
        
        return {
            'session_types': [
                {
                    'type': row['session_type'],
                    'session_count': row['session_count'],
                    'unique_users': row['unique_users'],
                    'avg_processing_time': row['avg_processing_time'] or 0,
                    'total_resumes': row['total_resumes'] or 0
                }
                for row in session_results
            ],
            'feature_usage': [
                {
                    'feature_name': row['feature_name'].strip('"') if row['feature_name'] else 'unknown',
                    'usage_count': row['usage_count'],
                    'unique_users': row['unique_users']
                }
                for row in feature_results
            ],
            'period_days': days
        }
    
    def get_customer_support_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get customer support metrics (placeholder implementation)"""
        # This would integrate with a support ticket system in production
        # For now, we'll return mock data based on user activity
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Estimate support load based on user activity
        user_activity_query = """
            SELECT 
                COUNT(DISTINCT user_id) as active_users,
                COUNT(*) as total_sessions,
                AVG(processing_time_seconds) as avg_processing_time
            FROM analysis_sessions 
            WHERE created_at >= %s
        """
        
        result = self.db.get_single_result(user_activity_query, (since_date,))
        
        # Estimate support tickets (rough approximation)
        active_users = result['active_users'] or 0
        estimated_tickets = max(1, int(active_users * 0.05))  # 5% of users might need support
        
        return {
            'total_tickets': estimated_tickets,
            'open_tickets': max(1, int(estimated_tickets * 0.3)),
            'resolved_tickets': int(estimated_tickets * 0.7),
            'avg_resolution_time_hours': 24,  # Placeholder
            'customer_satisfaction_score': 4.2,  # Placeholder
            'period_days': days,
            'note': 'Support metrics are estimated. Integrate with actual support system for real data.'
        }
    
    def get_system_health_metrics(self) -> Dict[str, Any]:
        """Get system health and performance metrics"""
        # Database health
        db_health = self._check_database_health()
        
        # Recent error rates
        error_metrics = self._get_error_metrics()
        
        # Performance metrics
        performance_metrics = self._get_performance_metrics()
        
        return {
            'database_health': db_health,
            'error_metrics': error_metrics,
            'performance_metrics': performance_metrics,
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def _get_revenue_metrics(self, since_date: datetime) -> Dict[str, Any]:
        """Get revenue-related metrics"""
        # Current MRR
        mrr_query = """
            SELECT SUM(sp.price_monthly) as current_mrr
            FROM subscriptions s
            JOIN subscription_plans sp ON s.plan_id = sp.id
            WHERE s.status = 'active'
        """
        
        mrr_result = self.db.get_single_result(mrr_query)
        current_mrr = mrr_result['current_mrr'] or 0
        
        # Previous period MRR for growth calculation
        previous_period = since_date - timedelta(days=30)
        prev_mrr_query = """
            SELECT SUM(sp.price_monthly) as prev_mrr
            FROM subscriptions s
            JOIN subscription_plans sp ON s.plan_id = sp.id
            WHERE s.status = 'active' AND s.created_at <= %s
        """
        
        prev_mrr_result = self.db.get_single_result(prev_mrr_query, (previous_period,))
        previous_mrr = prev_mrr_result['prev_mrr'] or 0
        
        # Calculate growth rate
        growth_rate = 0
        if previous_mrr > 0:
            growth_rate = ((current_mrr - previous_mrr) / previous_mrr) * 100
        
        return {
            'mrr': current_mrr,
            'arr': current_mrr * 12,
            'total_revenue': current_mrr,  # Simplified - would include historical revenue
            'growth_rate': growth_rate
        }
    
    def _get_user_metrics(self, since_date: datetime) -> Dict[str, Any]:
        """Get user-related metrics"""
        # Total users
        total_users_query = "SELECT COUNT(*) as total FROM users WHERE is_active = TRUE"
        total_result = self.db.get_single_result(total_users_query)
        total_users = total_result['total']
        
        # Active users (users with sessions in the period)
        active_users_query = """
            SELECT COUNT(DISTINCT user_id) as active
            FROM analysis_sessions 
            WHERE created_at >= %s
        """
        active_result = self.db.get_single_result(active_users_query, (since_date,))
        active_users = active_result['active'] or 0
        
        # New users this period
        new_users_query = """
            SELECT COUNT(*) as new_users
            FROM users 
            WHERE created_at >= %s AND is_active = TRUE
        """
        new_result = self.db.get_single_result(new_users_query, (since_date,))
        new_users = new_result['new_users']
        
        # Previous period for growth calculation
        previous_period = since_date - timedelta(days=30)
        prev_users_query = """
            SELECT COUNT(*) as prev_total
            FROM users 
            WHERE created_at <= %s AND is_active = TRUE
        """
        prev_result = self.db.get_single_result(prev_users_query, (previous_period,))
        previous_total = prev_result['prev_total']
        
        # Calculate growth rate
        growth_rate = 0
        if previous_total > 0:
            growth_rate = ((total_users - previous_total) / previous_total) * 100
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'new_users': new_users,
            'growth_rate': growth_rate
        }
    
    def _get_subscription_metrics(self, since_date: datetime) -> Dict[str, Any]:
        """Get subscription-related metrics"""
        # Subscription counts by status
        subscription_query = """
            SELECT 
                s.status,
                sp.plan_type,
                COUNT(*) as count
            FROM subscriptions s
            JOIN subscription_plans sp ON s.plan_id = sp.id
            GROUP BY s.status, sp.plan_type
        """
        
        results = self.db.execute_query(subscription_query)
        
        total_subscriptions = 0
        paid_subscriptions = 0
        free_users = 0
        
        for row in results:
            count = row['count']
            total_subscriptions += count
            
            if row['plan_type'] == 'free':
                free_users += count
            else:
                paid_subscriptions += count
        
        # Calculate churn rate (simplified)
        churn_query = """
            SELECT COUNT(*) as churned
            FROM subscriptions 
            WHERE cancelled_at >= %s AND cancelled_at IS NOT NULL
        """
        churn_result = self.db.get_single_result(churn_query, (since_date,))
        churned_users = churn_result['churned']
        
        churn_rate = 0
        if total_subscriptions > 0:
            churn_rate = (churned_users / total_subscriptions) * 100
        
        return {
            'total_subscriptions': total_subscriptions,
            'paid_subscriptions': paid_subscriptions,
            'free_users': free_users,
            'churn_rate': churn_rate
        }
    
    def _get_usage_metrics(self, since_date: datetime) -> Dict[str, Any]:
        """Get usage-related metrics"""
        # Total analyses
        total_query = "SELECT COUNT(*) as total, COUNT(*) as total_resumes FROM analysis_sessions WHERE status = 'completed'"
        total_result = self.db.get_single_result(total_query)
        
        # This period analyses
        period_query = """
            SELECT COUNT(*) as period_total, COUNT(*) as period_resumes
            FROM analysis_sessions 
            WHERE created_at >= %s AND status = 'completed'
        """
        period_result = self.db.get_single_result(period_query, (since_date,))
        
        # Average per user
        user_count_query = "SELECT COUNT(DISTINCT user_id) as unique_users FROM analysis_sessions WHERE status = 'completed'"
        user_result = self.db.get_single_result(user_count_query)
        unique_users = user_result['unique_users'] or 1
        
        avg_per_user = (total_result['total'] or 0) / unique_users
        
        return {
            'total_analyses': total_result['total'] or 0,
            'analyses_this_month': period_result['period_total'] or 0,
            'avg_per_user': avg_per_user
        }
    
    def _get_conversion_metrics(self, since_date: datetime) -> Dict[str, Any]:
        """Get conversion-related metrics"""
        # Free to paid conversion
        free_users_query = """
            SELECT COUNT(DISTINCT s.user_id) as free_users
            FROM subscriptions s
            JOIN subscription_plans sp ON s.plan_id = sp.id
            WHERE sp.plan_type = 'free'
        """
        free_result = self.db.get_single_result(free_users_query)
        free_users = free_result['free_users'] or 1
        
        paid_users_query = """
            SELECT COUNT(DISTINCT s.user_id) as paid_users
            FROM subscriptions s
            JOIN subscription_plans sp ON s.plan_id = sp.id
            WHERE sp.plan_type != 'free' AND s.status = 'active'
        """
        paid_result = self.db.get_single_result(paid_users_query)
        paid_users = paid_result['paid_users'] or 0
        
        free_to_paid = (paid_users / (free_users + paid_users)) * 100 if (free_users + paid_users) > 0 else 0
        
        return {
            'free_to_paid': free_to_paid,
            'trial_to_paid': 75.0  # Placeholder - would need trial tracking
        }
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database health metrics"""
        try:
            # Simple health check
            health_query = "SELECT COUNT(*) as user_count FROM users"
            result = self.db.get_single_result(health_query)
            
            return {
                'status': 'healthy',
                'user_count': result['user_count'],
                'last_check': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }
    
    def _get_error_metrics(self) -> Dict[str, Any]:
        """Get error rate metrics"""
        # This would integrate with error tracking in production
        return {
            'error_rate': 0.5,  # Placeholder: 0.5% error rate
            'total_errors': 12,  # Placeholder
            'critical_errors': 1,  # Placeholder
            'last_24h_errors': 3  # Placeholder
        }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        # Average processing time
        perf_query = """
            SELECT 
                AVG(processing_time_seconds) as avg_processing_time,
                MAX(processing_time_seconds) as max_processing_time,
                MIN(processing_time_seconds) as min_processing_time
            FROM analysis_sessions 
            WHERE status = 'completed' AND created_at >= %s
        """
        
        since_24h = datetime.utcnow() - timedelta(hours=24)
        result = self.db.get_single_result(perf_query, (since_24h,))
        
        return {
            'avg_processing_time': result['avg_processing_time'] or 0,
            'max_processing_time': result['max_processing_time'] or 0,
            'min_processing_time': result['min_processing_time'] or 0,
            'uptime_percentage': 99.5  # Placeholder
        }

def render_admin_dashboard():
    """Render the admin dashboard interface"""
    st.title("📊 Admin Dashboard")
    st.markdown("---")
    
    # Check if user has admin access
    current_user = st.session_state.get('current_user')
    if not current_user or current_user.role not in [UserRole.ADMIN, UserRole.ENTERPRISE_ADMIN]:
        st.error("🚫 Access denied. Admin privileges required.")
        return
    
    # Initialize dashboard service
    dashboard_service = AdminDashboardService()
    
    # Time period selector
    col1, col2 = st.columns([3, 1])
    with col2:
        period_days = st.selectbox(
            "Time Period",
            [7, 30, 90, 365],
            index=1,
            format_func=lambda x: f"Last {x} days"
        )
    
    with col1:
        st.subheader(f"Business Metrics - Last {period_days} Days")
    
    # Get business metrics
    with st.spinner("Loading business metrics..."):
        metrics = dashboard_service.get_business_metrics(period_days)
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Monthly Recurring Revenue",
            f"${metrics.mrr:,.2f}",
            delta=f"{metrics.revenue_growth_rate:+.1f}%"
        )
    
    with col2:
        st.metric(
            "Total Users",
            f"{metrics.total_users:,}",
            delta=f"{metrics.user_growth_rate:+.1f}%"
        )
    
    with col3:
        st.metric(
            "Paid Subscriptions",
            f"{metrics.paid_subscriptions:,}",
            delta=f"{metrics.free_to_paid_conversion:.1f}% conversion"
        )
    
    with col4:
        st.metric(
            "Total Analyses",
            f"{metrics.total_analyses:,}",
            delta=f"{metrics.analyses_this_month:,} this month"
        )
    
    st.markdown("---")
    
    # Detailed metrics tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💰 Revenue", "👥 Users", "📊 Usage", "🎯 Conversion", "⚙️ System Health"
    ])
    
    with tab1:
        render_revenue_metrics(dashboard_service, period_days)
    
    with tab2:
        render_user_metrics(dashboard_service, period_days)
    
    with tab3:
        render_usage_metrics(dashboard_service, period_days)
    
    with tab4:
        render_conversion_metrics(dashboard_service, period_days)
    
    with tab5:
        render_system_health_metrics(dashboard_service)

def render_revenue_metrics(dashboard_service: AdminDashboardService, period_days: int):
    """Render revenue metrics section"""
    st.subheader("💰 Revenue Analytics")
    
    # Revenue breakdown
    revenue_data = dashboard_service.get_revenue_breakdown(period_days)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total MRR", f"${revenue_data['total_mrr']:,.2f}")
        
        # Revenue by plan type
        st.subheader("Revenue by Plan")
        for plan_type, data in revenue_data['revenue_by_plan'].items():
            st.write(f"**{data['plan_name']}**: ${data['monthly_revenue']:,.2f} ({data['subscription_count']} subs)")
    
    with col2:
        # Revenue chart (placeholder)
        if revenue_data['revenue_by_plan']:
            chart_data = pd.DataFrame([
                {'Plan': data['plan_name'], 'Revenue': data['monthly_revenue']}
                for data in revenue_data['revenue_by_plan'].values()
            ])
            st.bar_chart(chart_data.set_index('Plan'))

def render_user_metrics(dashboard_service: AdminDashboardService, period_days: int):
    """Render user metrics section"""
    st.subheader("👥 User Analytics")
    
    # User acquisition metrics
    acquisition_data = dashboard_service.get_user_acquisition_metrics(period_days)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("New Users", acquisition_data['total_new_users'])
        st.metric("Estimated CAC", f"${acquisition_data['estimated_cac']}")
        
        # New users by day
        if acquisition_data['new_users_by_day']:
            st.subheader("New Users by Day")
            chart_data = pd.DataFrame(acquisition_data['new_users_by_day'])
            st.line_chart(chart_data.set_index('date'))
    
    with col2:
        st.metric("Estimated Marketing Spend", f"${acquisition_data['estimated_marketing_spend']:,}")
        
        # Churn by day
        if acquisition_data['churn_by_day']:
            st.subheader("Churn by Day")
            churn_data = pd.DataFrame(acquisition_data['churn_by_day'])
            st.line_chart(churn_data.set_index('date'))

def render_usage_metrics(dashboard_service: AdminDashboardService, period_days: int):
    """Render usage metrics section"""
    st.subheader("📊 Usage Analytics")
    
    # Feature usage analytics
    usage_data = dashboard_service.get_feature_usage_analytics(period_days)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Analysis Session Types")
        for session in usage_data['session_types']:
            st.write(f"**{session['type'].title()}**: {session['session_count']} sessions ({session['unique_users']} users)")
    
    with col2:
        st.subheader("Feature Usage")
        for feature in usage_data['feature_usage'][:10]:  # Top 10 features
            st.write(f"**{feature['feature_name']}**: {feature['usage_count']} uses ({feature['unique_users']} users)")

def render_conversion_metrics(dashboard_service: AdminDashboardService, period_days: int):
    """Render conversion metrics section"""
    st.subheader("🎯 Conversion Analytics")
    
    # Import funnel analyzer
    from analytics.google_analytics import funnel_analyzer
    
    try:
        funnel_data = funnel_analyzer.get_funnel_metrics(period_days)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Conversion Funnel")
            for step, data in funnel_data['funnel_steps'].items():
                st.write(f"**{step.title()}**: {data['unique_users']} users")
        
        with col2:
            st.subheader("Conversion Rates")
            for conversion, rate in funnel_data['conversion_rates'].items():
                st.write(f"**{conversion.replace('_', ' ').title()}**: {rate}%")
    
    except Exception as e:
        st.warning("Conversion funnel data not available yet. Analytics events need to be tracked first.")

def render_system_health_metrics(dashboard_service: AdminDashboardService):
    """Render system health metrics section"""
    st.subheader("⚙️ System Health")
    
    # System health metrics
    health_data = dashboard_service.get_system_health_metrics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Database Health")
        db_health = health_data['database_health']
        if db_health['status'] == 'healthy':
            st.success(f"✅ Healthy ({db_health['user_count']} users)")
        else:
            st.error(f"❌ Error: {db_health.get('error', 'Unknown')}")
    
    with col2:
        st.subheader("Error Metrics")
        error_metrics = health_data['error_metrics']
        st.metric("Error Rate", f"{error_metrics['error_rate']}%")
        st.metric("24h Errors", error_metrics['last_24h_errors'])
    
    with col3:
        st.subheader("Performance")
        perf_metrics = health_data['performance_metrics']
        st.metric("Avg Processing Time", f"{perf_metrics['avg_processing_time']:.1f}s")
        st.metric("Uptime", f"{perf_metrics['uptime_percentage']}%")
    
    # Customer support metrics
    st.subheader("📞 Customer Support")
    support_data = dashboard_service.get_customer_support_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tickets", support_data['total_tickets'])
    with col2:
        st.metric("Open Tickets", support_data['open_tickets'])
    with col3:
        st.metric("Avg Resolution", f"{support_data['avg_resolution_time_hours']}h")
    with col4:
        st.metric("CSAT Score", f"{support_data['customer_satisfaction_score']}/5")
    
    if support_data.get('note'):
        st.info(support_data['note'])

# Service instance
admin_dashboard_service = AdminDashboardService()