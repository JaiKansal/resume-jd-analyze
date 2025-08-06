"""
Google Analytics integration for Resume + JD Analyzer
Handles event tracking, conversion funnel analysis, and user engagement metrics
"""

import logging
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import streamlit as st

logger = logging.getLogger(__name__)

@dataclass
class AnalyticsEvent:
    """Represents an analytics event"""
    event_name: str
    user_id: Optional[str]
    session_id: Optional[str]
    parameters: Dict[str, Any]
    timestamp: datetime
    
    def to_ga4_format(self) -> Dict[str, Any]:
        """Convert to Google Analytics 4 format"""
        return {
            'name': self.event_name,
            'params': {
                **self.parameters,
                'user_id': self.user_id,
                'session_id': self.session_id,
                'timestamp_micros': int(self.timestamp.timestamp() * 1000000)
            }
        }

class GoogleAnalyticsTracker:
    """Google Analytics 4 integration for tracking user events"""
    
    def __init__(self, measurement_id: str = None, api_secret: str = None):
        self.measurement_id = measurement_id or os.getenv('GA4_MEASUREMENT_ID')
        self.api_secret = api_secret or os.getenv('GA4_API_SECRET')
        self.enabled = bool(self.measurement_id and self.api_secret)
        
        if not self.enabled:
            logger.warning("Google Analytics not configured. Set GA4_MEASUREMENT_ID and GA4_API_SECRET environment variables.")
    
    def track_event(self, event_name: str, user_id: str = None, 
                   parameters: Dict[str, Any] = None) -> bool:
        """Track a custom event"""
        if not self.enabled:
            return False
        
        try:
            event = AnalyticsEvent(
                event_name=event_name,
                user_id=user_id,
                session_id=self._get_session_id(),
                parameters=parameters or {},
                timestamp=datetime.utcnow()
            )
            
            # Send to Google Analytics
            success = self._send_to_ga4(event)
            
            # Also store locally for our own analytics
            self._store_event_locally(event)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to track event {event_name}: {e}")
            return False
    
    def track_page_view(self, page_title: str, page_location: str, 
                       user_id: str = None) -> bool:
        """Track page view"""
        return self.track_event('page_view', user_id, {
            'page_title': page_title,
            'page_location': page_location,
            'page_referrer': self._get_referrer()
        })
    
    def track_user_signup(self, user_id: str, signup_method: str = 'email') -> bool:
        """Track user registration"""
        return self.track_event('sign_up', user_id, {
            'method': signup_method,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def track_subscription_event(self, user_id: str, event_type: str, 
                               plan_name: str, value: float = 0) -> bool:
        """Track subscription-related events"""
        return self.track_event(event_type, user_id, {
            'plan_name': plan_name,
            'value': value,
            'currency': 'USD'
        })
    
    def track_analysis_completion(self, user_id: str, analysis_type: str,
                                resume_count: int, processing_time: float,
                                match_score: float = None) -> bool:
        """Track analysis completion"""
        parameters = {
            'analysis_type': analysis_type,
            'resume_count': resume_count,
            'processing_time': processing_time
        }
        
        if match_score is not None:
            parameters['match_score'] = match_score
        
        return self.track_event('analysis_completed', user_id, parameters)
    
    def track_conversion_funnel(self, user_id: str, funnel_step: str,
                              step_value: str = None) -> bool:
        """Track conversion funnel progression"""
        parameters = {
            'funnel_step': funnel_step,
            'step_number': self._get_funnel_step_number(funnel_step)
        }
        
        if step_value:
            parameters['step_value'] = step_value
        
        return self.track_event('funnel_progression', user_id, parameters)
    
    def track_feature_usage(self, user_id: str, feature_name: str,
                          feature_category: str = None) -> bool:
        """Track feature usage"""
        parameters = {
            'feature_name': feature_name,
            'feature_category': feature_category or 'general'
        }
        
        return self.track_event('feature_used', user_id, parameters)
    
    def track_error(self, user_id: str, error_type: str, error_message: str,
                   context: Dict[str, Any] = None) -> bool:
        """Track application errors"""
        parameters = {
            'error_type': error_type,
            'error_message': error_message[:100],  # Truncate long messages
            'context': json.dumps(context or {})[:500]  # Limit context size
        }
        
        return self.track_event('app_error', user_id, parameters)
    
    def _send_to_ga4(self, event: AnalyticsEvent) -> bool:
        """Send event to Google Analytics 4"""
        try:
            import requests
            
            url = f"https://www.google-analytics.com/mp/collect"
            params = {
                'measurement_id': self.measurement_id,
                'api_secret': self.api_secret
            }
            
            payload = {
                'client_id': event.user_id or self._generate_client_id(),
                'events': [event.to_ga4_format()]
            }
            
            response = requests.post(url, params=params, json=payload, timeout=5)
            return response.status_code == 204
            
        except Exception as e:
            logger.error(f"Failed to send event to GA4: {e}")
            return False
    
    def _store_event_locally(self, event: AnalyticsEvent):
        """Store event in local database for our own analytics"""
        try:
            from database.connection import get_db
            
            db = get_db()
            query = """
                INSERT INTO analytics_events (
                    id, event_name, user_id, session_id, parameters, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?)
            """
            
            import uuid
            params = (
                str(uuid.uuid4()),
                event.event_name,
                event.user_id,
                event.session_id,
                json.dumps(event.parameters),
                event.timestamp
            )
            
            db.execute_command(query, params)
            
        except Exception as e:
            logger.error(f"Failed to store event locally: {e}")
    
    def _get_session_id(self) -> str:
        """Get current session ID"""
        if 'analytics_session_id' not in st.session_state:
            import uuid
            st.session_state.analytics_session_id = str(uuid.uuid4())
        return st.session_state.analytics_session_id
    
    def _get_referrer(self) -> str:
        """Get page referrer"""
        # In Streamlit, we can't easily get the referrer
        # This would be implemented differently in a web framework
        return "streamlit_app"
    
    def _generate_client_id(self) -> str:
        """Generate a client ID for anonymous users"""
        import uuid
        return str(uuid.uuid4())
    
    def _get_funnel_step_number(self, funnel_step: str) -> int:
        """Map funnel step names to numbers"""
        step_mapping = {
            'landing': 1,
            'signup': 2,
            'first_analysis': 3,
            'upgrade_prompt': 4,
            'payment': 5,
            'subscription_active': 6
        }
        return step_mapping.get(funnel_step, 0)

class ConversionFunnelAnalyzer:
    """Analyze conversion funnel performance"""
    
    def __init__(self):
        from database.connection import get_db
        self.db = get_db()
    
    def get_funnel_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get conversion funnel metrics"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get funnel step counts
        query = """
            SELECT 
                JSON_EXTRACT(parameters, '$.funnel_step') as step,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(*) as total_events
            FROM analytics_events 
            WHERE event_name = 'funnel_progression' 
            AND timestamp >= ?
            GROUP BY JSON_EXTRACT(parameters, '$.funnel_step')
            ORDER BY JSON_EXTRACT(parameters, '$.step_number')
        """
        
        results = self.db.execute_query(query, (since_date,))
        
        funnel_data = {}
        for row in results:
            step = row['step']
            if step:
                funnel_data[step.strip('"')] = {
                    'unique_users': row['unique_users'],
                    'total_events': row['total_events']
                }
        
        # Calculate conversion rates
        conversion_rates = self._calculate_conversion_rates(funnel_data)
        
        return {
            'period_days': days,
            'funnel_steps': funnel_data,
            'conversion_rates': conversion_rates,
            'total_top_of_funnel': funnel_data.get('landing', {}).get('unique_users', 0)
        }
    
    def get_cohort_analysis(self, cohort_period: str = 'weekly') -> Dict[str, Any]:
        """Get cohort retention analysis"""
        # This is a simplified cohort analysis
        # In production, you'd want more sophisticated cohort tracking
        
        query = """
            SELECT 
                DATE(created_at) as cohort_date,
                user_id,
                MIN(created_at) as first_seen,
                MAX(created_at) as last_seen,
                COUNT(*) as total_events
            FROM analytics_events 
            WHERE user_id IS NOT NULL
            GROUP BY user_id, DATE(created_at)
            ORDER BY cohort_date, user_id
        """
        
        results = self.db.execute_query(query)
        
        # Process cohort data
        cohorts = {}
        for row in results:
            cohort_date = row['cohort_date']
            if cohort_date not in cohorts:
                cohorts[cohort_date] = {
                    'users': set(),
                    'retention': {}
                }
            cohorts[cohort_date]['users'].add(row['user_id'])
        
        # Calculate retention rates (simplified)
        for cohort_date, cohort_data in cohorts.items():
            cohort_data['size'] = len(cohort_data['users'])
            cohort_data['users'] = list(cohort_data['users'])  # Convert set to list for JSON serialization
        
        return {
            'cohort_period': cohort_period,
            'cohorts': cohorts
        }
    
    def _calculate_conversion_rates(self, funnel_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate conversion rates between funnel steps"""
        steps = ['landing', 'signup', 'first_analysis', 'upgrade_prompt', 'payment', 'subscription_active']
        conversion_rates = {}
        
        for i in range(len(steps) - 1):
            current_step = steps[i]
            next_step = steps[i + 1]
            
            current_users = funnel_data.get(current_step, {}).get('unique_users', 0)
            next_users = funnel_data.get(next_step, {}).get('unique_users', 0)
            
            if current_users > 0:
                rate = (next_users / current_users) * 100
                conversion_rates[f"{current_step}_to_{next_step}"] = round(rate, 2)
            else:
                conversion_rates[f"{current_step}_to_{next_step}"] = 0.0
        
        return conversion_rates

# Create analytics events table
def create_analytics_tables():
    """Create analytics tracking tables"""
    from database.connection import get_db
    
    db = get_db()
    
    analytics_events_table = """
        CREATE TABLE IF NOT EXISTS analytics_events (
            id TEXT PRIMARY KEY,
            event_name VARCHAR(100) NOT NULL,
            user_id TEXT,
            session_id TEXT,
            parameters TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    
    # Create indexes
    analytics_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON analytics_events(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_analytics_events_event_name ON analytics_events(event_name)",
        "CREATE INDEX IF NOT EXISTS idx_analytics_events_created_at ON analytics_events(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_analytics_events_session_id ON analytics_events(session_id)"
    ]
    
    try:
        db.execute_command(analytics_events_table)
        
        for index in analytics_indexes:
            db.execute_command(index)
        
        logger.info("Analytics tracking tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create analytics tracking tables: {e}")

# Service instances
ga_tracker = GoogleAnalyticsTracker()
funnel_analyzer = ConversionFunnelAnalyzer()

# Initialize tables on import
create_analytics_tables()