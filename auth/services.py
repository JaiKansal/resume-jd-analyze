"""
User authentication services for Resume + JD Analyzer
Handles database operations for users, subscriptions, and teams
"""

import logging
import uuid
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from database.connection import get_db, DatabaseManager
from auth.models import (
    User, UserRole, Subscription, SubscriptionPlan, SubscriptionStatus, 
    PlanType, Team, TeamMember, UserSession, AnalysisSession
)

logger = logging.getLogger(__name__)

class UserService:
    """Service for user management operations"""
    
    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or get_db()
    
    def create_user(self, email: str, password: str, **kwargs) -> Optional[User]:
        """Create a new user account"""
        try:
            # Check if user already exists
            if self.get_user_by_email(email):
                logger.warning(f"User creation failed: email {email} already exists")
                return None
            
            # Create user object
            user = User.create(email, password, **kwargs)
            
            # Insert into database
            query = """
                INSERT INTO users (
                    id, email, password_hash, first_name, last_name, company_name,
                    role, phone, country, timezone, email_verified, 
                    email_verification_token, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                user.id, user.email, user.password_hash, user.first_name,
                user.last_name, user.company_name, user.role.value, user.phone,
                user.country, user.timezone, user.email_verified,
                user.email_verification_token, user.is_active,
                user.created_at, user.updated_at
            )
            
            self.db.execute_command(query, params)
            
            # Create default free subscription
            self._create_default_subscription(user.id)
            
            logger.info(f"Created user: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Failed to create user {email}: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = ? AND is_active = TRUE"
        result = self.db.get_single_result(query, (user_id,))
        
        if result:
            return self._row_to_user(result)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        # Use simple query without is_active dependency
        query = "SELECT * FROM users WHERE email = ?"
        result = self.db.get_single_result(query, (email.lower().strip(),))
        
        if result:
            return self._row_to_user(result)
        return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        
        if user and user.verify_password(password):
            # Update login statistics
            user.update_login()
            self.update_user(user)
            return user
        
        return None
    
    def update_user(self, user: User) -> bool:
        """Update user information"""
        try:
            query = """
                UPDATE users SET
                    first_name = ?, last_name = ?, company_name = ?, role = ?,
                    phone = ?, country = ?, timezone = ?, email_verified = ?,
                    email_verification_token = ?, password_reset_token = ?,
                    password_reset_expires = ?, last_login = ?, login_count = ?,
                    is_active = ?, updated_at = ?
                WHERE id = ?
            """
            
            params = (
                user.first_name, user.last_name, user.company_name, user.role.value,
                user.phone, user.country, user.timezone, user.email_verified,
                user.email_verification_token, user.password_reset_token,
                user.password_reset_expires, user.last_login, user.login_count,
                user.is_active, datetime.utcnow(), user.id
            )
            
            rows_affected = self.db.execute_command(query, params)
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Failed to update user {user.id}: {e}")
            return False
    
    def verify_email(self, token: str) -> bool:
        """Verify user email with token"""
        query = "SELECT * FROM users WHERE email_verification_token = ?"
        result = self.db.get_single_result(query, (token,))
        
        if result:
            user = self._row_to_user(result)
            if user.verify_email(token):
                return self.update_user(user)
        
        return False
    
    def request_password_reset(self, email: str) -> Optional[str]:
        """Request password reset and return token"""
        user = self.get_user_by_email(email)
        
        if user:
            token = user.generate_password_reset_token()
            if self.update_user(user):
                return token
        
        return None
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using token"""
        query = "SELECT * FROM users WHERE password_reset_token = ?"
        result = self.db.get_single_result(query, (token,))
        
        if result:
            user = self._row_to_user(result)
            if user.reset_password(new_password, token):
                return self.update_user(user)
        
        return False
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        query = "UPDATE users SET is_active = FALSE, updated_at = ? WHERE id = ?"
        rows_affected = self.db.execute_command(query, (datetime.utcnow(), user_id))
        return rows_affected > 0
    
    def _create_default_subscription(self, user_id: str):
        """Create default free subscription for new user"""
        subscription_service = SubscriptionService(self.db)
        free_plan = subscription_service.get_plan_by_type(PlanType.FREE)
        
        if free_plan:
            subscription_service.create_subscription(user_id, free_plan.id)
    
    def _row_to_user(self, row: Dict[str, Any]) -> User:
        """Convert database row to User object"""
        from datetime import datetime
        from auth.models import parse_datetime
        
        return User(
            id=row['id'],
            email=row['email'],
            password_hash=row['password_hash'],
            first_name=row.get('first_name', ''),
            last_name=row.get('last_name', ''),
            company_name=row.get('company_name', ''),
            role=UserRole(row.get('role', 'user')),
            phone=row.get('phone', ''),
            country=row.get('country', 'IN'),
            timezone=row.get('timezone', 'Asia/Kolkata'),
            email_verified=bool(row.get('email_verified', row.get('is_verified', False))),
            email_verification_token=row.get('email_verification_token'),
            password_reset_token=row.get('password_reset_token'),
            password_reset_expires=parse_datetime(row.get('password_reset_expires')),
            last_login=parse_datetime(row.get('last_login')),
            login_count=row.get('login_count', 0),
            is_active=bool(row.get('is_active', True)),
            created_at=parse_datetime(row.get('created_at')),
            updated_at=parse_datetime(row.get('updated_at'))
        )

class SubscriptionService:
    """Service for subscription management operations"""
    
    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or get_db()
    
    def get_plan_by_type(self, plan_type: PlanType) -> Optional[SubscriptionPlan]:
        """Get subscription plan by type"""
        query = "SELECT * FROM subscription_plans WHERE plan_type = ? AND is_active = TRUE"
        result = self.db.get_single_result(query, (plan_type.value,))
        
        if result:
            return self._row_to_plan(result)
        return None
    
    def get_all_plans(self) -> List[SubscriptionPlan]:
        """Get all active subscription plans"""
        # Use simple query without is_active dependency
        query = "SELECT * FROM subscription_plans ORDER BY price_monthly"
        results = self.db.execute_query(query)
        
        return [self._row_to_plan(row) for row in results]
    
    def create_subscription(self, user_id: str, plan_id: str, 
                          stripe_customer_id: str = None) -> Optional[Subscription]:
        """Create new subscription for user"""
        try:
            subscription = Subscription(
                id=str(uuid.uuid4()),
                user_id=user_id,
                plan_id=plan_id,
                status=SubscriptionStatus.ACTIVE,
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30),
                stripe_customer_id=stripe_customer_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            query = """
                INSERT INTO subscriptions (
                    id, user_id, plan_id, status, current_period_start,
                    current_period_end, stripe_customer_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                subscription.id, subscription.user_id, subscription.plan_id,
                subscription.status.value, subscription.current_period_start,
                subscription.current_period_end, subscription.stripe_customer_id,
                subscription.created_at, subscription.updated_at
            )
            
            self.db.execute_command(query, params)
            return subscription
            
        except Exception as e:
            logger.error(f"Failed to create subscription for user {user_id}: {e}")
            return None
    
    def get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get active subscription for user"""
        query = """
            SELECT s.*, sp.id as plan_id_full, sp.name, sp.plan_type, sp.price_monthly, sp.price_annual,
                   sp.monthly_analysis_limit, sp.features, sp.is_active, sp.created_at as plan_created_at
            FROM subscriptions s
            JOIN subscription_plans sp ON s.plan_id = sp.id
            WHERE s.user_id = ? AND s.status IN ('active', 'trialing')
            ORDER BY s.created_at DESC
            LIMIT 1
        """
        
        result = self.db.get_single_result(query, (user_id,))
        
        if result:
            subscription = self._row_to_subscription(result)
            # Create plan object with proper field mapping
            plan_data = {
                'id': result['plan_id_full'],
                'name': result['name'],
                'plan_type': result['plan_type'],
                'price_monthly': result['price_monthly'],
                'price_annual': result['price_annual'],
                'monthly_analysis_limit': result['monthly_analysis_limit'],
                'features': result['features'],
                'is_active': result['is_active'],
                'created_at': result['plan_created_at']
            }
            subscription.plan = self._row_to_plan(plan_data)
            return subscription
        
        return None
    
    def update_subscription(self, subscription: Subscription) -> bool:
        """Update subscription information"""
        try:
            query = """
                UPDATE subscriptions SET
                    status = ?, current_period_start = ?, current_period_end = ?,
                    trial_start = ?, trial_end = ?, monthly_analysis_used = ?,
                    stripe_subscription_id = ?, cancel_at_period_end = ?,
                    canceled_at = ?, updated_at = ?
                WHERE id = ?
            """
            
            params = (
                subscription.status.value, subscription.current_period_start,
                subscription.current_period_end, subscription.trial_start,
                subscription.trial_end, subscription.monthly_analysis_used,
                subscription.stripe_subscription_id, subscription.cancel_at_period_end,
                subscription.cancelled_at, datetime.utcnow(), subscription.id
            )
            
            rows_affected = self.db.execute_command(query, params)
            return rows_affected > 0
            
        except Exception as e:
            logger.error(f"Failed to update subscription {subscription.id}: {e}")
            return False
    
    def can_user_analyze(self, user_id: str) -> Tuple[bool, Optional[str]]:
        """Check if user can perform analysis and return reason if not"""
        subscription = self.get_user_subscription(user_id)
        
        if not subscription:
            return False, "No active subscription found"
        
        if not subscription.is_active():
            return False, "Subscription is not active"
        
        if not subscription.can_analyze():
            return False, f"Monthly limit of {subscription.plan.monthly_analysis_limit} analyses reached"
        
        return True, None
    
    def increment_user_usage(self, user_id: str, count: int = 1) -> bool:
        """Increment user's analysis usage count"""
        subscription = self.get_user_subscription(user_id)
        
        if subscription:
            subscription.increment_usage(count)
            return self.update_subscription(subscription)
        
        return False
    
    def get_subscription_by_id(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID"""
        query = """
            SELECT s.*, sp.id as plan_id_full, sp.name, sp.plan_type, sp.price_monthly, sp.price_annual,
                   sp.monthly_analysis_limit, sp.features, sp.is_active, sp.created_at as plan_created_at
            FROM subscriptions s
            JOIN subscription_plans sp ON s.plan_id = sp.id
            WHERE s.id = ?
        """
        
        result = self.db.get_single_result(query, (subscription_id,))
        
        if result:
            subscription = self._row_to_subscription(result)
            # Create plan object with proper field mapping
            plan_data = {
                'id': result['plan_id_full'],
                'name': result['name'],
                'plan_type': result['plan_type'],
                'price_monthly': result['price_monthly'],
                'price_annual': result['price_annual'],
                'monthly_analysis_limit': result['monthly_analysis_limit'],
                'features': result['features'],
                'is_active': result['is_active'],
                'created_at': result['plan_created_at']
            }
            subscription.plan = self._row_to_plan(plan_data)
            return subscription
        
        return None
    
    def get_plan_by_id(self, plan_id: str) -> Optional[SubscriptionPlan]:
        """Get subscription plan by ID"""
        query = "SELECT * FROM subscription_plans WHERE id = ? AND is_active = TRUE"
        result = self.db.get_single_result(query, (plan_id,))
        
        if result:
            return self._row_to_plan(result)
        return None
    
    def _row_to_plan(self, row: Dict[str, Any]) -> SubscriptionPlan:
        """Convert database row to SubscriptionPlan object"""
        import json
        from auth.models import parse_datetime
        
        # Handle JSON features field
        features = row.get('features', '[]')
        if isinstance(features, str):
            try:
                features = json.loads(features)
            except (json.JSONDecodeError, TypeError):
                features = []
        elif not isinstance(features, (dict, list)):
            features = []
        
        # Convert features list to dict format expected by model
        if isinstance(features, list):
            features = {f"feature_{i}": feature for i, feature in enumerate(features)}
        
        # Set monthly analysis limits based on plan type
        plan_type = row['plan_type']
        if plan_type == 'free':
            monthly_limit = 3
        elif plan_type in ['professional', 'business', 'enterprise']:
            monthly_limit = -1  # Unlimited
        else:
            monthly_limit = row.get('monthly_analysis_limit', 3)
        
        return SubscriptionPlan(
            id=row['id'],
            name=row['name'],
            plan_type=PlanType(row['plan_type']),
            price_monthly=float(row['price_monthly']),
            price_annual=float(row['price_annual']),
            monthly_analysis_limit=monthly_limit,
            features=features,
            is_active=row.get('is_active', True),
            created_at=parse_datetime(row.get('created_at'))
        )
    
    def _row_to_subscription(self, row: Dict[str, Any]) -> Subscription:
        """Convert database row to Subscription object"""
        return Subscription(
            id=row['id'],
            user_id=row['user_id'],
            plan_id=row['plan_id'],
            status=SubscriptionStatus(row['status']),
            current_period_start=row['current_period_start'],
            current_period_end=row['current_period_end'],
            trial_start=row['trial_start'],
            trial_end=row['trial_end'],
            monthly_analysis_used=row['monthly_analysis_used'],
            stripe_customer_id=row['stripe_customer_id'],
            stripe_subscription_id=row['stripe_subscription_id'],
            cancel_at_period_end=row['cancel_at_period_end'],
            cancelled_at=row['canceled_at'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

class SessionService:
    """Service for user session management"""
    
    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or get_db()
    
    def create_session(self, user_id: str, ip_address: str = None, 
                      user_agent: str = None) -> UserSession:
        """Create new user session"""
        session = UserSession.create(user_id, ip_address, user_agent)
        
        query = """
            INSERT INTO user_sessions (
                id, user_id, session_token, ip_address, user_agent,
                expires_at, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            session.id, session.user_id, session.session_token,
            session.ip_address, session.user_agent, session.expires_at,
            session.is_active, session.created_at
        )
        
        self.db.execute_command(query, params)
        return session
    
    def get_session(self, session_token: str) -> Optional[UserSession]:
        """Get session by token"""
        query = "SELECT * FROM user_sessions WHERE session_token = ? AND is_active = TRUE"
        result = self.db.get_single_result(query, (session_token,))
        
        if result:
            session = self._row_to_session(result)
            if session.is_valid():
                return session
            else:
                # Deactivate expired session
                self.deactivate_session(session_token)
        
        return None
    
    def extend_session(self, session_token: str, hours: int = 24) -> bool:
        """Extend session expiration"""
        new_expires = datetime.utcnow() + timedelta(hours=hours)
        query = "UPDATE user_sessions SET expires_at = ? WHERE session_token = ?"
        rows_affected = self.db.execute_command(query, (new_expires, session_token))
        return rows_affected > 0
    
    def deactivate_session(self, session_token: str) -> bool:
        """Deactivate session"""
        query = "UPDATE user_sessions SET is_active = FALSE WHERE session_token = ?"
        rows_affected = self.db.execute_command(query, (session_token,))
        return rows_affected > 0
    
    def deactivate_user_sessions(self, user_id: str) -> bool:
        """Deactivate all sessions for user"""
        query = "UPDATE user_sessions SET is_active = FALSE WHERE user_id = ?"
        rows_affected = self.db.execute_command(query, (user_id,))
        return rows_affected > 0
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        query = "UPDATE user_sessions SET is_active = FALSE WHERE expires_at < ?"
        rows_affected = self.db.execute_command(query, (datetime.utcnow(),))
        return rows_affected
    
    def _row_to_session(self, row: Dict[str, Any]) -> UserSession:
        """Convert database row to UserSession object"""
        from datetime import datetime
        
        # Parse datetime strings if needed
        expires_at = row['expires_at']
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        
        created_at = row['created_at']
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        return UserSession(
            id=row['id'],
            user_id=row['user_id'],
            session_token=row['session_token'],
            ip_address=row['ip_address'],
            user_agent=row['user_agent'],
            expires_at=expires_at,
            is_active=bool(row['is_active']),
            created_at=created_at
        )

class AnalyticsService:
    """Service for usage analytics and tracking"""
    
    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or get_db()
    
    def track_analysis_session(self, session: AnalysisSession) -> bool:
        """Track analysis session for billing and analytics"""
        try:
            query = """
                INSERT INTO analysis_sessions (
                    id, user_id, team_id, session_type, resume_count,
                    job_description_count, processing_time_seconds, api_cost_usd,
                    tokens_used, status, error_message, metadata, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                session.id, session.user_id, session.team_id, session.session_type,
                session.resume_count, session.job_description_count,
                session.processing_time_seconds, session.api_cost_usd,
                session.tokens_used, session.status, session.error_message,
                session.metadata, session.created_at
            )
            
            self.db.execute_command(query, params)
            return True
            
        except Exception as e:
            logger.error(f"Failed to track analysis session: {e}")
            return False
    
    def get_user_usage_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user usage statistics"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        query = """
            SELECT 
                COUNT(*) as total_sessions,
                SUM(resume_count) as total_resumes,
                AVG(processing_time_seconds) as avg_processing_time,
                SUM(api_cost_usd) as total_cost,
                SUM(tokens_used) as total_tokens
            FROM analysis_sessions
            WHERE user_id = ? AND created_at >= ? AND status = 'completed'
        """
        
        result = self.db.get_single_result(query, (user_id, since_date))
        
        return {
            'total_sessions': result['total_sessions'] or 0,
            'total_resumes': result['total_resumes'] or 0,
            'avg_processing_time': result['avg_processing_time'] or 0,
            'total_cost': result['total_cost'] or 0,
            'total_tokens': result['total_tokens'] or 0,
            'period_days': days
        }

# Service instances
user_service = UserService()
subscription_service = SubscriptionService()
session_service = SessionService()
analytics_service = AnalyticsService()