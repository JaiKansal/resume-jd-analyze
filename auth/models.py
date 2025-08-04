"""
User authentication models for Resume + JD Analyzer
Handles user management, subscriptions, and team relationships
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
import bcrypt
import logging

logger = logging.getLogger(__name__)

def parse_datetime(dt_value: Union[str, datetime, None]) -> Optional[datetime]:
    """Parse datetime from string or return datetime object"""
    if dt_value is None:
        return None
    if isinstance(dt_value, datetime):
        return dt_value
    if isinstance(dt_value, str):
        try:
            # Handle ISO format with or without microseconds
            if 'T' in dt_value:
                if '.' in dt_value:
                    return datetime.fromisoformat(dt_value.replace('Z', '+00:00'))
                else:
                    return datetime.fromisoformat(dt_value.replace('Z', '+00:00'))
            else:
                # Handle SQLite datetime format
                return datetime.fromisoformat(dt_value)
        except (ValueError, TypeError):
            logger.warning(f"Could not parse datetime: {dt_value}")
            return None
    return None

class UserRole(Enum):
    USER = "user"
    INDIVIDUAL = "individual"
    HR_MANAGER = "hr_manager"
    ADMIN = "admin"
    ENTERPRISE_ADMIN = "enterprise_admin"

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"

class PlanType(Enum):
    FREE = "free"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"

@dataclass
class User:
    """User model with authentication and profile information"""
    id: str
    email: str
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    role: UserRole = UserRole.INDIVIDUAL
    phone: Optional[str] = None
    country: Optional[str] = None
    timezone: str = "UTC"
    email_verified: bool = False
    email_verification_token: Optional[str] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    last_login: Optional[datetime] = None
    login_count: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def create(cls, email: str, password: str, **kwargs) -> 'User':
        """Create a new user with hashed password"""
        user_id = str(uuid.uuid4())
        password_hash = cls.hash_password(password)
        email_verification_token = secrets.token_urlsafe(32)
        
        return cls(
            id=user_id,
            email=email.lower().strip(),
            password_hash=password_hash,
            email_verification_token=email_verification_token,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **kwargs
        )
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            self.password_hash.encode('utf-8')
        )
    
    def generate_password_reset_token(self) -> str:
        """Generate password reset token"""
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        self.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
        return token
    
    def reset_password(self, new_password: str, token: str) -> bool:
        """Reset password using token"""
        if (self.password_reset_token != token or 
            not self.password_reset_expires):
            return False
        
        expires_dt = parse_datetime(self.password_reset_expires)
        if not expires_dt or datetime.utcnow() > expires_dt:
            return False
        
        self.password_hash = self.hash_password(new_password)
        self.password_reset_token = None
        self.password_reset_expires = None
        self.updated_at = datetime.utcnow()
        return True
    
    def verify_email(self, token: str) -> bool:
        """Verify email using token"""
        if self.email_verification_token == token:
            self.email_verified = True
            self.email_verification_token = None
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def update_login(self):
        """Update login statistics"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        self.updated_at = datetime.utcnow()
    
    def get_full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email.split('@')[0]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary (excluding sensitive data)"""
        data = asdict(self)
        # Remove sensitive fields
        data.pop('password_hash', None)
        data.pop('email_verification_token', None)
        data.pop('password_reset_token', None)
        
        # Convert enums to strings
        if isinstance(data.get('role'), UserRole):
            data['role'] = data['role'].value
        
        return data

@dataclass
class SubscriptionPlan:
    """Subscription plan model"""
    id: str
    name: str
    plan_type: PlanType
    price_monthly: float
    price_annual: float
    monthly_analysis_limit: Optional[int]  # -1 for unlimited
    features: Dict[str, Any]
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    def is_unlimited(self) -> bool:
        """Check if plan has unlimited analyses"""
        return self.monthly_analysis_limit == -1
    
    def has_feature(self, feature_name: str) -> bool:
        """Check if plan includes a specific feature"""
        return self.features.get(feature_name, False)

@dataclass
class Subscription:
    """User subscription model"""
    id: str
    user_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    monthly_analysis_used: int = 0
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    cancel_at_period_end: bool = False
    cancelled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Related objects (loaded separately)
    plan: Optional[SubscriptionPlan] = None
    
    def is_active(self) -> bool:
        """Check if subscription is active"""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
    
    def is_trial(self) -> bool:
        """Check if subscription is in trial period"""
        if self.status != SubscriptionStatus.TRIALING or not self.trial_end:
            return False
        
        trial_end_dt = parse_datetime(self.trial_end)
        if not trial_end_dt:
            return False
            
        return datetime.utcnow() < trial_end_dt
    
    def days_until_renewal(self) -> Optional[int]:
        """Get days until next renewal"""
        if not self.current_period_end:
            return None
        
        period_end_dt = parse_datetime(self.current_period_end)
        if not period_end_dt:
            return None
            
        delta = period_end_dt - datetime.utcnow()
        return max(0, delta.days)
    
    def can_analyze(self) -> bool:
        """Check if user can perform analysis based on limits"""
        if not self.is_active():
            return False
        
        if not self.plan:
            return False
        
        if self.plan.is_unlimited():
            return True
        
        return self.monthly_analysis_used < self.plan.monthly_analysis_limit
    
    def increment_usage(self, count: int = 1):
        """Increment analysis usage count"""
        self.monthly_analysis_used += count
        self.updated_at = datetime.utcnow()
    
    def reset_monthly_usage(self):
        """Reset monthly usage counter (called on billing cycle)"""
        self.monthly_analysis_used = 0
        self.updated_at = datetime.utcnow()

@dataclass
class Team:
    """Team model for business/enterprise accounts"""
    id: str
    name: str
    owner_id: str
    subscription_id: Optional[str] = None
    description: Optional[str] = None
    seat_limit: int = 5
    seats_used: int = 1
    settings: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def has_available_seats(self) -> bool:
        """Check if team has available seats"""
        return self.seats_used < self.seat_limit
    
    def can_add_member(self) -> bool:
        """Check if team can add new member"""
        return self.is_active and self.has_available_seats()

@dataclass
class TeamMember:
    """Team member relationship model"""
    id: str
    team_id: str
    user_id: str
    role: str = "member"  # member, admin, owner
    permissions: Optional[Dict[str, Any]] = None
    invited_by: Optional[str] = None
    invited_at: Optional[datetime] = None
    joined_at: Optional[datetime] = None
    is_active: bool = True
    
    # Related objects
    user: Optional[User] = None
    team: Optional[Team] = None
    
    def is_admin(self) -> bool:
        """Check if member has admin privileges"""
        return self.role in ["admin", "owner"]
    
    def can_invite_members(self) -> bool:
        """Check if member can invite other members"""
        return self.is_admin() and self.is_active

@dataclass
class UserSession:
    """User session model for authentication"""
    id: str
    user_id: str
    session_token: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    @classmethod
    def create(cls, user_id: str, ip_address: str = None, user_agent: str = None, 
               expires_hours: int = 24) -> 'UserSession':
        """Create new user session"""
        session_id = str(uuid.uuid4())
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        
        return cls(
            id=session_id,
            user_id=user_id,
            session_token=session_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            created_at=datetime.utcnow()
        )
    
    def is_valid(self) -> bool:
        """Check if session is valid and not expired"""
        if not self.is_active or not self.expires_at:
            return False
        
        expires_dt = parse_datetime(self.expires_at)
        if not expires_dt:
            return False
            
        return datetime.utcnow() < expires_dt
    
    def extend_session(self, hours: int = 24):
        """Extend session expiration"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)

@dataclass
class AnalysisSession:
    """Analysis session tracking model"""
    id: str
    user_id: str
    team_id: Optional[str] = None
    session_type: str = "single"  # single, bulk, job_matching, api
    resume_count: int = 1
    job_description_count: int = 1
    processing_time_seconds: Optional[float] = None
    api_cost_usd: Optional[float] = None
    tokens_used: Optional[int] = None
    status: str = "completed"  # completed, failed, processing
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def create(cls, user_id: str, session_type: str = "single", **kwargs) -> 'AnalysisSession':
        """Create new analysis session"""
        session_id = str(uuid.uuid4())
        
        return cls(
            id=session_id,
            user_id=user_id,
            session_type=session_type,
            created_at=datetime.utcnow(),
            **kwargs
        )
    
    def mark_completed(self, processing_time: float, api_cost: float = None, 
                      tokens_used: int = None):
        """Mark session as completed with metrics"""
        self.status = "completed"
        self.processing_time_seconds = processing_time
        self.api_cost_usd = api_cost
        self.tokens_used = tokens_used
    
    def mark_failed(self, error_message: str):
        """Mark session as failed with error"""
        self.status = "failed"
        self.error_message = error_message