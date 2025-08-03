"""
Usage tracking and billing system for Resume + JD Analyzer
Handles real-time usage monitoring, limit enforcement, and billing automation
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from auth.models import User, Subscription, AnalysisSession
from auth.services import subscription_service, analytics_service
from database.connection import get_db

logger = logging.getLogger(__name__)

@dataclass
class UsageEvent:
    """Represents a usage event for billing purposes"""
    id: str
    user_id: str
    event_type: str  # analysis, api_call, bulk_upload, etc.
    quantity: int
    cost_usd: float
    metadata: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['metadata'] = json.dumps(self.metadata)
        return data

@dataclass
class BillingPeriod:
    """Represents a billing period for usage calculations"""
    start_date: datetime
    end_date: datetime
    user_id: str
    subscription_id: str
    base_amount: float
    usage_amount: float
    total_amount: float
    currency: str = 'USD'

class RealTimeUsageMonitor:
    """Real-time usage monitoring and limit enforcement"""
    
    def __init__(self):
        self.db = get_db()
    
    def track_analysis_session(self, user_id: str, session_type: str = 'single', 
                             resume_count: int = 1, processing_time: float = 0,
                             api_cost: float = 0) -> bool:
        """Track an analysis session and update usage counters"""
        try:
            # Create analysis session record
            session = AnalysisSession.create(
                user_id=user_id,
                session_type=session_type,
                resume_count=resume_count,
                job_description_count=1,
                processing_time_seconds=processing_time,
                api_cost_usd=api_cost
            )
            
            # Mark as completed
            session.mark_completed(processing_time, api_cost)
            
            # Store in database
            analytics_service.track_analysis_session(session)
            
            # Update subscription usage counter
            subscription_service.increment_user_usage(user_id, resume_count)
            
            # Track usage event for billing
            self._track_usage_event(
                user_id=user_id,
                event_type='analysis',
                quantity=resume_count,
                cost_usd=api_cost,
                metadata={
                    'session_id': session.id,
                    'session_type': session_type,
                    'processing_time': processing_time
                }
            )
            
            logger.info(f"Tracked analysis session for user {user_id}: {resume_count} resumes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track analysis session for user {user_id}: {e}")
            return False
    
    def check_usage_limits(self, user_id: str, requested_analyses: int = 1) -> Tuple[bool, Optional[str]]:
        """Check if user can perform requested number of analyses"""
        subscription = subscription_service.get_user_subscription(user_id)
        
        if not subscription:
            return False, "No active subscription found"
        
        if not subscription.is_active():
            return False, "Subscription is not active"
        
        # Check monthly analysis limit
        if subscription.plan.monthly_analysis_limit != -1:
            remaining = subscription.plan.monthly_analysis_limit - subscription.monthly_analysis_used
            if requested_analyses > remaining:
                return False, f"Insufficient analyses remaining. You have {remaining} left, but requested {requested_analyses}"
        
        return True, None
    
    def get_current_usage(self, user_id: str) -> Dict[str, Any]:
        """Get current usage statistics for user"""
        subscription = subscription_service.get_user_subscription(user_id)
        
        if not subscription:
            return {'error': 'No subscription found'}
        
        # Get current period usage
        period_start = subscription.current_period_start or datetime.utcnow().replace(day=1)
        period_end = subscription.current_period_end or (period_start + timedelta(days=30))
        
        # Query usage events for current period
        usage_query = """
            SELECT 
                event_type,
                SUM(quantity) as total_quantity,
                SUM(cost_usd) as total_cost,
                COUNT(*) as event_count
            FROM usage_events 
            WHERE user_id = ? AND timestamp >= ? AND timestamp <= ?
            GROUP BY event_type
        """
        
        usage_results = self.db.execute_query(usage_query, (user_id, period_start, period_end))
        
        usage_by_type = {}
        total_cost = 0
        
        for row in usage_results:
            usage_by_type[row['event_type']] = {
                'quantity': row['total_quantity'],
                'cost': row['total_cost'],
                'events': row['event_count']
            }
            total_cost += row['total_cost'] or 0
        
        return {
            'user_id': user_id,
            'period_start': period_start.isoformat(),
            'period_end': period_end.isoformat(),
            'subscription_plan': subscription.plan.name,
            'monthly_limit': subscription.plan.monthly_analysis_limit,
            'monthly_used': subscription.monthly_analysis_used,
            'usage_by_type': usage_by_type,
            'total_cost': total_cost,
            'overage_charges': self._calculate_overage_charges(subscription, usage_by_type)
        }
    
    def enforce_rate_limits(self, user_id: str, action_type: str) -> Tuple[bool, Optional[str]]:
        """Enforce rate limits for different actions"""
        # Define rate limits by action type
        rate_limits = {
            'analysis': {'per_minute': 10, 'per_hour': 100},
            'api_call': {'per_minute': 60, 'per_hour': 1000},
            'bulk_upload': {'per_minute': 2, 'per_hour': 10}
        }
        
        limits = rate_limits.get(action_type, {'per_minute': 5, 'per_hour': 50})
        
        # Check minute-level rate limit
        minute_ago = datetime.utcnow() - timedelta(minutes=1)
        minute_count = self._get_usage_count(user_id, action_type, minute_ago)
        
        if minute_count >= limits['per_minute']:
            return False, f"Rate limit exceeded: {limits['per_minute']} {action_type}s per minute"
        
        # Check hour-level rate limit
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        hour_count = self._get_usage_count(user_id, action_type, hour_ago)
        
        if hour_count >= limits['per_hour']:
            return False, f"Rate limit exceeded: {limits['per_hour']} {action_type}s per hour"
        
        return True, None
    
    def _track_usage_event(self, user_id: str, event_type: str, quantity: int, 
                          cost_usd: float, metadata: Dict[str, Any]):
        """Track a usage event in the database"""
        try:
            import uuid
            
            event = UsageEvent(
                id=str(uuid.uuid4()),
                user_id=user_id,
                event_type=event_type,
                quantity=quantity,
                cost_usd=cost_usd,
                metadata=metadata,
                timestamp=datetime.utcnow()
            )
            
            query = """
                INSERT INTO usage_events (
                    id, user_id, event_type, quantity, cost_usd, metadata, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                event.id, event.user_id, event.event_type, event.quantity,
                event.cost_usd, json.dumps(event.metadata), event.timestamp
            )
            
            self.db.execute_command(query, params)
            
        except Exception as e:
            logger.error(f"Failed to track usage event: {e}")
    
    def _get_usage_count(self, user_id: str, event_type: str, since: datetime) -> int:
        """Get usage count for a user since a specific time"""
        query = """
            SELECT SUM(quantity) as total
            FROM usage_events 
            WHERE user_id = ? AND event_type = ? AND timestamp >= ?
        """
        
        result = self.db.get_single_result(query, (user_id, event_type, since))
        return result['total'] or 0
    
    def _calculate_overage_charges(self, subscription: Subscription, 
                                 usage_by_type: Dict[str, Any]) -> float:
        """Calculate overage charges for usage beyond plan limits"""
        if subscription.plan.plan_type.value in ['free', 'professional']:
            return 0.0  # No overage billing for these tiers
        
        overage_rates = {
            'analysis': 0.50,  # $0.50 per analysis over limit
            'api_call': 0.01,  # $0.01 per API call over limit
            'bulk_upload': 1.00  # $1.00 per bulk upload over limit
        }
        
        total_overage = 0.0
        
        # For business and enterprise tiers, calculate overages
        if subscription.plan.plan_type.value in ['business', 'enterprise']:
            # API call overages (business: 1000/month, enterprise: unlimited)
            if subscription.plan.plan_type.value == 'business':
                api_usage = usage_by_type.get('api_call', {}).get('quantity', 0)
                if api_usage > 1000:
                    api_overage = (api_usage - 1000) * overage_rates['api_call']
                    total_overage += api_overage
        
        return total_overage

class AutomatedBillingSystem:
    """Automated billing and invoice generation system"""
    
    def __init__(self):
        self.db = get_db()
        self.usage_monitor = RealTimeUsageMonitor()
    
    def generate_monthly_invoice(self, user_id: str, billing_period: BillingPeriod) -> Optional[str]:
        """Generate monthly invoice for a user"""
        try:
            subscription = subscription_service.get_user_subscription(user_id)
            if not subscription:
                return None
            
            # Calculate base subscription cost
            base_amount = subscription.plan.price_monthly
            
            # Get usage for billing period
            usage_data = self.usage_monitor.get_current_usage(user_id)
            usage_amount = usage_data.get('overage_charges', 0.0)
            
            total_amount = base_amount + usage_amount
            
            # Create invoice record
            invoice_id = self._create_invoice_record(
                user_id=user_id,
                subscription_id=subscription.id,
                billing_period=billing_period,
                base_amount=base_amount,
                usage_amount=usage_amount,
                total_amount=total_amount
            )
            
            # Generate invoice document
            invoice_data = self._generate_invoice_data(
                user_id, subscription, billing_period, usage_data, total_amount
            )
            
            logger.info(f"Generated invoice {invoice_id} for user {user_id}: ${total_amount}")
            return invoice_id
            
        except Exception as e:
            logger.error(f"Failed to generate invoice for user {user_id}: {e}")
            return None
    
    def process_subscription_renewal(self, subscription_id: str) -> bool:
        """Process subscription renewal and reset usage counters"""
        try:
            subscription = subscription_service.get_subscription_by_id(subscription_id)
            if not subscription:
                return False
            
            # Reset monthly usage counter
            subscription.reset_monthly_usage()
            
            # Update billing period
            subscription.current_period_start = datetime.utcnow()
            subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
            
            # Save changes
            subscription_service.update_subscription(subscription)
            
            # Generate invoice for previous period
            previous_period = BillingPeriod(
                start_date=subscription.current_period_start - timedelta(days=30),
                end_date=subscription.current_period_start,
                user_id=subscription.user_id,
                subscription_id=subscription.id,
                base_amount=subscription.plan.price_monthly,
                usage_amount=0.0,
                total_amount=subscription.plan.price_monthly
            )
            
            self.generate_monthly_invoice(subscription.user_id, previous_period)
            
            logger.info(f"Processed renewal for subscription {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process renewal for subscription {subscription_id}: {e}")
            return False
    
    def handle_failed_payment(self, subscription_id: str, attempt_count: int = 1) -> bool:
        """Handle failed payment with retry logic"""
        try:
            subscription = subscription_service.get_subscription_by_id(subscription_id)
            if not subscription:
                return False
            
            # Update subscription status
            subscription.status = subscription_service.SubscriptionStatus.PAST_DUE
            subscription_service.update_subscription(subscription)
            
            # Implement dunning management
            if attempt_count <= 3:
                # Schedule retry
                retry_date = datetime.utcnow() + timedelta(days=attempt_count * 2)
                self._schedule_payment_retry(subscription_id, retry_date, attempt_count + 1)
                
                # Send notification to user
                self._send_payment_failure_notification(subscription.user_id, attempt_count)
                
                logger.info(f"Scheduled payment retry {attempt_count} for subscription {subscription_id}")
            else:
                # Cancel subscription after 3 failed attempts
                subscription.status = subscription_service.SubscriptionStatus.CANCELLED
                subscription.cancelled_at = datetime.utcnow()
                subscription_service.update_subscription(subscription)
                
                # Send cancellation notification
                self._send_subscription_cancelled_notification(subscription.user_id)
                
                logger.warning(f"Cancelled subscription {subscription_id} after 3 failed payment attempts")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle payment failure for subscription {subscription_id}: {e}")
            return False
    
    def calculate_prorated_amount(self, subscription: Subscription, 
                                new_plan_price: float, change_date: datetime) -> float:
        """Calculate prorated amount for plan changes"""
        if not subscription.current_period_end:
            return new_plan_price
        
        # Calculate remaining days in current period
        remaining_days = (subscription.current_period_end - change_date).days
        total_days = (subscription.current_period_end - subscription.current_period_start).days
        
        if total_days <= 0:
            return new_plan_price
        
        # Calculate prorated amounts
        old_daily_rate = subscription.plan.price_monthly / total_days
        new_daily_rate = new_plan_price / total_days
        
        # Credit for unused portion of old plan
        old_plan_credit = old_daily_rate * remaining_days
        
        # Charge for new plan for remaining period
        new_plan_charge = new_daily_rate * remaining_days
        
        # Net amount (positive = charge, negative = credit)
        prorated_amount = new_plan_charge - old_plan_credit
        
        return max(0, prorated_amount)  # Don't allow negative charges
    
    def _create_invoice_record(self, user_id: str, subscription_id: str, 
                             billing_period: BillingPeriod, base_amount: float,
                             usage_amount: float, total_amount: float) -> str:
        """Create invoice record in database"""
        import uuid
        
        invoice_id = str(uuid.uuid4())
        
        query = """
            INSERT INTO invoices (
                id, user_id, subscription_id, billing_period_start, billing_period_end,
                base_amount, usage_amount, total_amount, currency, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            invoice_id, user_id, subscription_id, billing_period.start_date,
            billing_period.end_date, base_amount, usage_amount, total_amount,
            'USD', 'pending', datetime.utcnow()
        )
        
        self.db.execute_command(query, params)
        return invoice_id
    
    def _generate_invoice_data(self, user_id: str, subscription: Subscription,
                             billing_period: BillingPeriod, usage_data: Dict[str, Any],
                             total_amount: float) -> Dict[str, Any]:
        """Generate invoice data structure"""
        user = subscription_service.user_service.get_user_by_id(user_id)
        
        return {
            'invoice_id': f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{user_id[:8]}",
            'user': {
                'name': user.get_full_name(),
                'email': user.email,
                'company': user.company_name
            },
            'subscription': {
                'plan_name': subscription.plan.name,
                'plan_type': subscription.plan.plan_type.value
            },
            'billing_period': {
                'start': billing_period.start_date.strftime('%Y-%m-%d'),
                'end': billing_period.end_date.strftime('%Y-%m-%d')
            },
            'charges': {
                'base_subscription': billing_period.base_amount,
                'usage_charges': billing_period.usage_amount,
                'total': total_amount
            },
            'usage_summary': usage_data.get('usage_by_type', {}),
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _schedule_payment_retry(self, subscription_id: str, retry_date: datetime, attempt_count: int):
        """Schedule payment retry (placeholder for job queue integration)"""
        # In production, this would integrate with a job queue like Celery
        logger.info(f"Payment retry scheduled for {retry_date} (attempt {attempt_count})")
    
    def _send_payment_failure_notification(self, user_id: str, attempt_count: int):
        """Send payment failure notification to user"""
        # In production, this would integrate with email service
        logger.info(f"Payment failure notification sent to user {user_id} (attempt {attempt_count})")
    
    def _send_subscription_cancelled_notification(self, user_id: str):
        """Send subscription cancellation notification"""
        # In production, this would integrate with email service
        logger.info(f"Subscription cancellation notification sent to user {user_id}")

# Create database table for usage events if it doesn't exist
def create_usage_tables():
    """Create usage tracking tables"""
    db = get_db()
    
    # Usage events table
    usage_events_table = """
        CREATE TABLE IF NOT EXISTS usage_events (
            id TEXT PRIMARY KEY,
            user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
            event_type VARCHAR(50) NOT NULL,
            quantity INTEGER DEFAULT 1,
            cost_usd REAL DEFAULT 0.0,
            metadata TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    
    # Invoices table
    invoices_table = """
        CREATE TABLE IF NOT EXISTS invoices (
            id TEXT PRIMARY KEY,
            user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
            subscription_id TEXT REFERENCES subscriptions(id) ON DELETE SET NULL,
            billing_period_start TIMESTAMP NOT NULL,
            billing_period_end TIMESTAMP NOT NULL,
            base_amount REAL NOT NULL,
            usage_amount REAL DEFAULT 0.0,
            total_amount REAL NOT NULL,
            currency VARCHAR(3) DEFAULT 'USD',
            status VARCHAR(20) DEFAULT 'pending',
            stripe_invoice_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            paid_at TIMESTAMP
        )
    """
    
    # Create indexes
    usage_events_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_usage_events_user_id ON usage_events(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_usage_events_timestamp ON usage_events(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_usage_events_event_type ON usage_events(event_type)"
    ]
    
    invoices_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status)",
        "CREATE INDEX IF NOT EXISTS idx_invoices_created_at ON invoices(created_at)"
    ]
    
    try:
        db.execute_command(usage_events_table)
        db.execute_command(invoices_table)
        
        for index in usage_events_indexes + invoices_indexes:
            db.execute_command(index)
        
        logger.info("Usage tracking tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create usage tracking tables: {e}")

# Service instances
usage_monitor = RealTimeUsageMonitor()
billing_system = AutomatedBillingSystem()

# Initialize tables on import
create_usage_tables()