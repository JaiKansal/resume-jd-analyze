"""
User engagement tracking and metrics for Resume + JD Analyzer
Tracks user behavior, feature adoption, and engagement patterns
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from database.connection import get_db
from analytics.google_analytics import ga_tracker

logger = logging.getLogger(__name__)

@dataclass
class EngagementSession:
    """Represents a user engagement session"""
    user_id: str
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    pages_visited: List[str]
    features_used: List[str]
    analyses_performed: int
    time_spent_minutes: float

class UserEngagementTracker:
    """Track user engagement and behavior patterns"""
    
    def __init__(self):
        self.db = get_db()
    
    def start_session(self, user_id: str, session_id: str) -> bool:
        """Start tracking a user session"""
        try:
            # Track session start
            ga_tracker.track_event('session_start', user_id, {
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start session tracking for user {user_id}: {e}")
            return False
    
    def track_page_visit(self, user_id: str, page_name: str, session_id: str = None) -> bool:
        """Track page visit"""
        try:
            # Track with Google Analytics
            ga_tracker.track_page_view(page_name, f"/{page_name.lower().replace(' ', '-')}", user_id)
            
            # Store in local database for detailed analytics
            self._store_engagement_event(user_id, 'page_visit', {
                'page_name': page_name,
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track page visit for user {user_id}: {e}")
            return False
    
    def track_feature_usage(self, user_id: str, feature_name: str, 
                          feature_category: str = None, metadata: Dict[str, Any] = None) -> bool:
        """Track feature usage"""
        try:
            # Track with Google Analytics
            ga_tracker.track_feature_usage(user_id, feature_name, feature_category)
            
            # Store detailed metadata locally
            event_data = {
                'feature_name': feature_name,
                'feature_category': feature_category or 'general',
                'metadata': metadata or {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self._store_engagement_event(user_id, 'feature_usage', event_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track feature usage for user {user_id}: {e}")
            return False
    
    def track_user_action(self, user_id: str, action_name: str, 
                         action_value: str = None, metadata: Dict[str, Any] = None) -> bool:
        """Track specific user actions"""
        try:
            event_data = {
                'action_name': action_name,
                'action_value': action_value,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Track with Google Analytics
            ga_tracker.track_event('user_action', user_id, event_data)
            
            # Store locally
            self._store_engagement_event(user_id, 'user_action', event_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track user action for user {user_id}: {e}")
            return False
    
    def update_daily_engagement(self, user_id: str, date: datetime = None) -> bool:
        """Update daily engagement metrics for a user"""
        try:
            if date is None:
                date = datetime.utcnow().date()
            
            # Get engagement events for the day
            start_of_day = datetime.combine(date, datetime.min.time())
            end_of_day = datetime.combine(date, datetime.max.time())
            
            events_query = """
                SELECT 
                    event_type,
                    COUNT(*) as event_count,
                    parameters
                FROM engagement_events 
                WHERE user_id = ? AND timestamp >= ? AND timestamp <= ?
                GROUP BY event_type
            """
            
            events = self.db.execute_query(events_query, (user_id, start_of_day, end_of_day))
            
            # Calculate metrics
            sessions_count = 0
            analyses_performed = 0
            features_used = set()
            pages_visited = set()
            
            for event in events:
                event_type = event['event_type']
                count = event['event_count']
                
                try:
                    params = json.loads(event['parameters']) if event['parameters'] else {}
                except:
                    params = {}
                
                if event_type == 'session_start':
                    sessions_count += count
                elif event_type == 'feature_usage':
                    features_used.add(params.get('feature_name', 'unknown'))
                elif event_type == 'page_visit':
                    pages_visited.add(params.get('page_name', 'unknown'))
                elif event_type == 'analysis_completed':
                    analyses_performed += count
            
            # Estimate time spent (simplified calculation)
            time_spent_minutes = sessions_count * 15  # Assume 15 minutes per session on average
            
            # Update or insert daily engagement record
            upsert_query = """
                INSERT OR REPLACE INTO user_engagement (
                    user_id, date, sessions_count, analyses_performed, 
                    features_used, time_spent_minutes, pages_visited, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                user_id, date, sessions_count, analyses_performed,
                json.dumps(list(features_used)), time_spent_minutes,
                len(pages_visited), datetime.utcnow()
            )
            
            self.db.execute_command(upsert_query, params)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update daily engagement for user {user_id}: {e}")
            return False
    
    def get_user_engagement_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user engagement summary"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get engagement data
        query = """
            SELECT 
                SUM(sessions_count) as total_sessions,
                SUM(analyses_performed) as total_analyses,
                SUM(time_spent_minutes) as total_time_minutes,
                SUM(pages_visited) as total_pages_visited,
                COUNT(DISTINCT date) as active_days,
                AVG(sessions_count) as avg_sessions_per_day,
                AVG(time_spent_minutes) as avg_time_per_day
            FROM user_engagement 
            WHERE user_id = ? AND date >= ?
        """
        
        result = self.db.get_single_result(query, (user_id, since_date.date()))
        
        # Get unique features used
        features_query = """
            SELECT DISTINCT features_used
            FROM user_engagement 
            WHERE user_id = ? AND date >= ? AND features_used IS NOT NULL
        """
        
        features_results = self.db.execute_query(features_query, (user_id, since_date.date()))
        
        all_features = set()
        for row in features_results:
            try:
                features = json.loads(row['features_used']) if row['features_used'] else []
                all_features.update(features)
            except:
                pass
        
        return {
            'user_id': user_id,
            'period_days': days,
            'total_sessions': result['total_sessions'] or 0,
            'total_analyses': result['total_analyses'] or 0,
            'total_time_minutes': result['total_time_minutes'] or 0,
            'total_pages_visited': result['total_pages_visited'] or 0,
            'active_days': result['active_days'] or 0,
            'avg_sessions_per_day': result['avg_sessions_per_day'] or 0,
            'avg_time_per_day': result['avg_time_per_day'] or 0,
            'unique_features_used': list(all_features),
            'engagement_score': self._calculate_engagement_score(result, len(all_features))
        }
    
    def get_feature_adoption_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get feature adoption metrics across all users"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get feature usage data
        query = """
            SELECT 
                JSON_EXTRACT(parameters, '$.feature_name') as feature_name,
                JSON_EXTRACT(parameters, '$.feature_category') as feature_category,
                COUNT(*) as usage_count,
                COUNT(DISTINCT user_id) as unique_users
            FROM engagement_events 
            WHERE event_type = 'feature_usage' 
            AND timestamp >= ?
            GROUP BY JSON_EXTRACT(parameters, '$.feature_name')
            ORDER BY usage_count DESC
        """
        
        try:
            results = self.db.execute_query(query, (since_date,))
        except:
            # Fallback if table doesn't exist
            results = []
        
        features = []
        for row in results:
            feature_name = row['feature_name']
            if feature_name:
                features.append({
                    'feature_name': feature_name.strip('"'),
                    'feature_category': row['feature_category'].strip('"') if row['feature_category'] else 'general',
                    'usage_count': row['usage_count'],
                    'unique_users': row['unique_users']
                })
        
        return {
            'period_days': days,
            'features': features,
            'total_features_tracked': len(features)
        }
    
    def _store_engagement_event(self, user_id: str, event_type: str, parameters: Dict[str, Any]):
        """Store engagement event in database"""
        try:
            import uuid
            
            query = """
                INSERT INTO engagement_events (
                    id, user_id, event_type, parameters, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """
            
            params = (
                str(uuid.uuid4()),
                user_id,
                event_type,
                json.dumps(parameters),
                datetime.utcnow()
            )
            
            self.db.execute_command(query, params)
            
        except Exception as e:
            logger.error(f"Failed to store engagement event: {e}")
    
    def _calculate_engagement_score(self, engagement_data: Dict[str, Any], unique_features: int) -> float:
        """Calculate engagement score (0-100)"""
        try:
            # Weighted scoring based on different engagement factors
            sessions_score = min((engagement_data['total_sessions'] or 0) * 2, 30)  # Max 30 points
            analyses_score = min((engagement_data['total_analyses'] or 0) * 3, 25)  # Max 25 points
            time_score = min((engagement_data['total_time_minutes'] or 0) / 10, 20)  # Max 20 points
            features_score = min(unique_features * 5, 25)  # Max 25 points
            
            total_score = sessions_score + analyses_score + time_score + features_score
            return min(total_score, 100)
            
        except:
            return 0.0

class CohortAnalyzer:
    """Analyze user cohorts and retention patterns"""
    
    def __init__(self):
        self.db = get_db()
    
    def get_cohort_retention(self, cohort_period: str = 'monthly') -> Dict[str, Any]:
        """Get cohort retention analysis"""
        # This is a simplified cohort analysis
        # In production, you'd want more sophisticated cohort tracking
        
        if cohort_period == 'monthly':
            date_format = '%Y-%m'
            period_days = 30
        else:  # weekly
            date_format = '%Y-%W'
            period_days = 7
        
        # Get user cohorts based on signup date
        cohorts_query = """
            SELECT 
                strftime(?, created_at) as cohort_period,
                COUNT(*) as cohort_size,
                GROUP_CONCAT(id) as user_ids
            FROM users 
            WHERE is_active = TRUE
            GROUP BY strftime(?, created_at)
            ORDER BY cohort_period
        """
        
        cohorts = self.db.execute_query(cohorts_query, (date_format, date_format))
        
        cohort_data = {}
        for cohort in cohorts:
            period = cohort['cohort_period']
            size = cohort['cohort_size']
            user_ids = cohort['user_ids'].split(',') if cohort['user_ids'] else []
            
            # Calculate retention for this cohort
            retention_periods = self._calculate_cohort_retention(user_ids, period_days)
            
            cohort_data[period] = {
                'cohort_size': size,
                'retention_periods': retention_periods
            }
        
        return {
            'cohort_period': cohort_period,
            'cohorts': cohort_data
        }
    
    def _calculate_cohort_retention(self, user_ids: List[str], period_days: int) -> Dict[str, float]:
        """Calculate retention rates for a cohort"""
        if not user_ids:
            return {}
        
        retention_periods = {}
        
        # Check retention for periods 1, 2, 3, 6 months
        for period in [1, 2, 3, 6]:
            period_start = datetime.utcnow() - timedelta(days=period * period_days)
            period_end = period_start + timedelta(days=period_days)
            
            # Count active users in this period
            active_query = """
                SELECT COUNT(DISTINCT user_id) as active_users
                FROM analysis_sessions 
                WHERE user_id IN ({}) 
                AND created_at >= ? AND created_at <= ?
            """.format(','.join(['?' for _ in user_ids]))
            
            params = user_ids + [period_start, period_end]
            result = self.db.get_single_result(active_query, params)
            
            active_users = result['active_users'] or 0
            retention_rate = (active_users / len(user_ids)) * 100 if user_ids else 0
            
            retention_periods[f"period_{period}"] = round(retention_rate, 2)
        
        return retention_periods

# Create engagement tracking tables
def create_engagement_tables():
    """Create engagement tracking tables"""
    db = get_db()
    
    engagement_events_table = """
        CREATE TABLE IF NOT EXISTS engagement_events (
            id TEXT PRIMARY KEY,
            user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
            event_type VARCHAR(50) NOT NULL,
            parameters TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    
    # Create indexes
    engagement_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_engagement_events_user_id ON engagement_events(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_engagement_events_event_type ON engagement_events(event_type)",
        "CREATE INDEX IF NOT EXISTS idx_engagement_events_timestamp ON engagement_events(timestamp)"
    ]
    
    try:
        db.execute_command(engagement_events_table)
        
        for index in engagement_indexes:
            db.execute_command(index)
        
        logger.info("Engagement tracking tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create engagement tracking tables: {e}")

# Service instances
engagement_tracker = UserEngagementTracker()
cohort_analyzer = CohortAnalyzer()

# Initialize tables on import
create_engagement_tables()