"""
Upgrade flow and conversion optimization for Resume + JD Analyzer
Handles upgrade prompts, A/B testing, trial periods, and abandoned cart recovery
"""

import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from auth.models import User, Subscription, PlanType, SubscriptionStatus, parse_datetime
from auth.services import subscription_service, user_service
from billing.subscription_tiers import tier_manager, usage_tracker

# Import Streamlit only when needed
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

# Import Stripe service only when needed
try:
    from billing.stripe_service import stripe_service
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

logger = logging.getLogger(__name__)

class UpgradePromptType(Enum):
    USAGE_LIMIT = "usage_limit"
    FEATURE_GATE = "feature_gate"
    TRIAL_EXPIRY = "trial_expiry"
    PERIODIC_REMINDER = "periodic_reminder"
    ABANDONED_CART = "abandoned_cart"

@dataclass
class UpgradePrompt:
    """Represents an upgrade prompt configuration"""
    id: str
    prompt_type: UpgradePromptType
    title: str
    message: str
    cta_text: str
    target_plan: PlanType
    urgency_level: str  # low, medium, high
    show_discount: bool = False
    discount_percentage: int = 0
    variant: str = "default"  # For A/B testing

@dataclass
class ConversionEvent:
    """Tracks conversion events for analytics"""
    id: str
    user_id: str
    event_type: str  # prompt_shown, prompt_clicked, trial_started, upgrade_completed
    prompt_id: Optional[str] = None
    variant: Optional[str] = None
    source_plan: Optional[str] = None
    target_plan: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

class UpgradeFlowManager:
    """Manages upgrade flows and conversion optimization"""
    
    def __init__(self):
        self.prompts = self._initialize_upgrade_prompts()
        self.ab_test_variants = self._initialize_ab_variants()
    
    def _initialize_upgrade_prompts(self) -> Dict[str, UpgradePrompt]:
        """Initialize upgrade prompt configurations"""
        return {
            "usage_limit_warning": UpgradePrompt(
                id="usage_limit_warning",
                prompt_type=UpgradePromptType.USAGE_LIMIT,
                title="🚀 You're Almost at Your Limit!",
                message="You've used most of your free analyses this month. Upgrade to Professional for unlimited access.",
                cta_text="Upgrade to Professional",
                target_plan=PlanType.PROFESSIONAL,
                urgency_level="medium"
            ),
            
            "usage_limit_exceeded": UpgradePrompt(
                id="usage_limit_exceeded",
                prompt_type=UpgradePromptType.USAGE_LIMIT,
                title="🔒 Monthly Limit Reached",
                message="You've reached your monthly limit of 3 analyses. Upgrade now to continue analyzing resumes.",
                cta_text="Unlock Unlimited Analyses",
                target_plan=PlanType.PROFESSIONAL,
                urgency_level="high"
            ),
            
            "bulk_upload_gate": UpgradePrompt(
                id="bulk_upload_gate",
                prompt_type=UpgradePromptType.FEATURE_GATE,
                title="📦 Bulk Analysis Available",
                message="Analyze multiple resumes at once with our Business plan. Save time and get better insights.",
                cta_text="Upgrade to Business",
                target_plan=PlanType.BUSINESS,
                urgency_level="low"
            ),
            
            "premium_ai_gate": UpgradePrompt(
                id="premium_ai_gate",
                prompt_type=UpgradePromptType.FEATURE_GATE,
                title="🧠 Unlock Premium AI",
                message="Get more accurate analysis and detailed insights with our advanced AI models.",
                cta_text="Try Professional Free",
                target_plan=PlanType.PROFESSIONAL,
                urgency_level="medium"
            ),
            
            "api_access_gate": UpgradePrompt(
                id="api_access_gate",
                prompt_type=UpgradePromptType.FEATURE_GATE,
                title="🔌 API Access Available",
                message="Integrate our analysis into your workflow with API access in the Business plan.",
                cta_text="Get API Access",
                target_plan=PlanType.BUSINESS,
                urgency_level="low"
            ),
            
            "trial_reminder": UpgradePrompt(
                id="trial_reminder",
                prompt_type=UpgradePromptType.TRIAL_EXPIRY,
                title="⏰ Trial Ending Soon",
                message="Your free trial ends in 3 days. Continue with unlimited access for just $19/month.",
                cta_text="Continue with Professional",
                target_plan=PlanType.PROFESSIONAL,
                urgency_level="high"
            )
        }
    
    def _initialize_ab_variants(self) -> Dict[str, Dict[str, Any]]:
        """Initialize A/B test variants for conversion optimization"""
        return {
            "usage_limit_exceeded": {
                "variant_a": {
                    "title": "🔒 Monthly Limit Reached",
                    "message": "You've reached your monthly limit. Upgrade to continue.",
                    "cta_text": "Upgrade Now"
                },
                "variant_b": {
                    "title": "🚀 Ready for More?",
                    "message": "You're clearly getting value! Unlock unlimited analyses with Professional.",
                    "cta_text": "Get Unlimited Access"
                },
                "variant_c": {
                    "title": "💡 Don't Stop Now!",
                    "message": "Keep the momentum going with unlimited analyses. Join thousands of professionals.",
                    "cta_text": "Join Professional"
                }
            },
            
            "premium_ai_gate": {
                "variant_a": {
                    "title": "🧠 Unlock Premium AI",
                    "message": "Get more accurate analysis with advanced AI models.",
                    "cta_text": "Try Professional Free"
                },
                "variant_b": {
                    "title": "⚡ Supercharge Your Analysis",
                    "message": "Professional users get 40% more accurate results with our premium AI.",
                    "cta_text": "Start Free Trial"
                }
            }
        }
    
    def should_show_upgrade_prompt(self, user: User, context: str) -> Optional[UpgradePrompt]:
        """Determine if and which upgrade prompt to show"""
        subscription = subscription_service.get_user_subscription(user.id)
        if not subscription:
            return None
        
        # Don't show prompts to enterprise users
        if subscription.plan.plan_type == PlanType.ENTERPRISE:
            return None
        
        # Context-based prompt selection
        if context == "analysis_limit_warning":
            if subscription.plan.plan_type == PlanType.FREE:
                remaining = subscription.plan.monthly_analysis_limit - subscription.monthly_analysis_used
                if remaining <= 1:
                    return self._get_prompt_variant("usage_limit_warning", user.id)
        
        elif context == "analysis_limit_exceeded":
            if subscription.plan.plan_type == PlanType.FREE:
                if subscription.monthly_analysis_used >= subscription.plan.monthly_analysis_limit:
                    return self._get_prompt_variant("usage_limit_exceeded", user.id)
        
        elif context == "bulk_upload_attempt":
            if subscription.plan.plan_type in [PlanType.FREE, PlanType.PROFESSIONAL]:
                return self._get_prompt_variant("bulk_upload_gate", user.id)
        
        elif context == "premium_ai_attempt":
            if subscription.plan.plan_type == PlanType.FREE:
                return self._get_prompt_variant("premium_ai_gate", user.id)
        
        elif context == "api_access_attempt":
            if subscription.plan.plan_type in [PlanType.FREE, PlanType.PROFESSIONAL]:
                return self._get_prompt_variant("api_access_gate", user.id)
        
        elif context == "trial_expiry":
            if subscription.is_trial() and subscription.trial_end:
                trial_end_dt = parse_datetime(subscription.trial_end)
                if trial_end_dt:
                    days_left = (trial_end_dt - datetime.utcnow()).days
                    if days_left <= 3:
                        return self._get_prompt_variant("trial_reminder", user.id)
        
        return None
    
    def _get_prompt_variant(self, prompt_id: str, user_id: str) -> Optional[UpgradePrompt]:
        """Get prompt variant for A/B testing"""
        base_prompt = self.prompts.get(prompt_id)
        if not base_prompt:
            return None
        
        # Determine variant based on user ID hash (consistent assignment)
        variant_key = self._get_user_variant(user_id, prompt_id)
        variants = self.ab_test_variants.get(prompt_id, {})
        
        if variant_key in variants:
            variant_data = variants[variant_key]
            # Create modified prompt with variant data
            prompt = UpgradePrompt(
                id=base_prompt.id,
                prompt_type=base_prompt.prompt_type,
                title=variant_data.get("title", base_prompt.title),
                message=variant_data.get("message", base_prompt.message),
                cta_text=variant_data.get("cta_text", base_prompt.cta_text),
                target_plan=base_prompt.target_plan,
                urgency_level=base_prompt.urgency_level,
                variant=variant_key
            )
            return prompt
        
        return base_prompt
    
    def _get_user_variant(self, user_id: str, prompt_id: str) -> str:
        """Get consistent variant assignment for user"""
        # Use hash of user_id + prompt_id for consistent assignment
        import hashlib
        hash_input = f"{user_id}_{prompt_id}".encode()
        hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
        
        # Simple A/B/C split
        variant_num = hash_value % 3
        variant_map = {0: "variant_a", 1: "variant_b", 2: "variant_c"}
        return variant_map.get(variant_num, "variant_a")
    
    def track_conversion_event(self, user_id: str, event_type: str, **kwargs):
        """Track conversion event for analytics"""
        try:
            event = ConversionEvent(
                id=str(uuid.uuid4()),
                user_id=user_id,
                event_type=event_type,
                timestamp=datetime.utcnow(),
                **kwargs
            )
            
            # Store in database (simplified for now)
            self._store_conversion_event(event)
            
            logger.info(f"Tracked conversion event: {event_type} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to track conversion event: {e}")
    
    def _store_conversion_event(self, event: ConversionEvent):
        """Store conversion event in database"""
        # This would integrate with your analytics database
        # For now, we'll use a simple approach
        pass

class TrialManager:
    """Manages trial periods and trial-to-paid conversions"""
    
    def __init__(self):
        self.trial_lengths = {
            PlanType.PROFESSIONAL: 14,  # 14-day trial
            PlanType.BUSINESS: 14,      # 14-day trial
            PlanType.ENTERPRISE: 30     # 30-day trial
        }
    
    def start_trial(self, user_id: str, plan_type: PlanType) -> bool:
        """Start trial period for user"""
        try:
            # Check if user is eligible for trial
            if not self._is_trial_eligible(user_id, plan_type):
                return False
            
            # Get the plan
            plan = subscription_service.get_plan_by_type(plan_type)
            if not plan:
                return False
            
            # Create trial subscription
            trial_days = self.trial_lengths.get(plan_type, 14)
            trial_end = datetime.utcnow() + timedelta(days=trial_days)
            
            subscription = subscription_service.get_user_subscription(user_id)
            if subscription:
                # Update existing subscription to trial
                subscription.plan_id = plan.id
                subscription.status = SubscriptionStatus.TRIALING
                subscription.trial_start = datetime.utcnow()
                subscription.trial_end = trial_end
                subscription.monthly_analysis_used = 0  # Reset usage for trial
                
                success = subscription_service.update_subscription(subscription)
                
                if success:
                    # Track trial start event
                    upgrade_flow.track_conversion_event(
                        user_id=user_id,
                        event_type="trial_started",
                        target_plan=plan_type.value,
                        trial_days=trial_days
                    )
                
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to start trial for user {user_id}: {e}")
            return False
    
    def _is_trial_eligible(self, user_id: str, plan_type: PlanType) -> bool:
        """Check if user is eligible for trial"""
        # Users can only have one trial per plan type
        # This would check trial history in a real implementation
        return True
    
    def get_trial_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get trial status for user"""
        subscription = subscription_service.get_user_subscription(user_id)
        
        if not subscription or not subscription.is_trial():
            return None
        
        trial_end_dt = parse_datetime(subscription.trial_end)
        if not trial_end_dt:
            return None
            
        days_remaining = (trial_end_dt - datetime.utcnow()).days
        
        return {
            'is_trial': True,
            'plan_name': subscription.plan.name,
            'trial_end': subscription.trial_end,
            'days_remaining': max(0, days_remaining),
            'usage_this_period': subscription.monthly_analysis_used
        }

class AbandonedCartRecovery:
    """Handles abandoned cart recovery for incomplete upgrades"""
    
    def __init__(self):
        self.recovery_sequences = self._initialize_recovery_sequences()
    
    def _initialize_recovery_sequences(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize abandoned cart recovery email sequences"""
        return {
            "professional": [
                {
                    "delay_hours": 1,
                    "subject": "Complete your upgrade to Professional",
                    "message": "You were just one step away from unlimited analyses. Complete your upgrade now!",
                    "discount": 0
                },
                {
                    "delay_hours": 24,
                    "subject": "Don't miss out - 10% off Professional plan",
                    "message": "We saved your upgrade! Get 10% off your first month of Professional.",
                    "discount": 10
                },
                {
                    "delay_hours": 72,
                    "subject": "Last chance - Your upgrade is waiting",
                    "message": "This is your final reminder. Complete your Professional upgrade with 10% off.",
                    "discount": 10
                }
            ],
            "business": [
                {
                    "delay_hours": 2,
                    "subject": "Complete your Business plan upgrade",
                    "message": "Unlock team features and bulk analysis. Complete your upgrade now!",
                    "discount": 0
                },
                {
                    "delay_hours": 24,
                    "subject": "15% off Business plan - Limited time",
                    "message": "Get your team started with 15% off the first month of Business plan.",
                    "discount": 15
                },
                {
                    "delay_hours": 96,
                    "subject": "Don't let your team wait - Complete upgrade",
                    "message": "Your team is waiting for advanced features. Complete your upgrade with 15% off.",
                    "discount": 15
                }
            ]
        }
    
    def track_abandoned_upgrade(self, user_id: str, target_plan: PlanType, 
                              checkout_session_id: str = None):
        """Track abandoned upgrade attempt"""
        try:
            # Store abandoned cart record
            abandoned_cart = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'target_plan': target_plan.value,
                'checkout_session_id': checkout_session_id,
                'created_at': datetime.utcnow(),
                'recovered': False
            }
            
            # Schedule recovery sequence
            self._schedule_recovery_sequence(user_id, target_plan.value)
            
            logger.info(f"Tracked abandoned upgrade for user {user_id} to {target_plan.value}")
            
        except Exception as e:
            logger.error(f"Failed to track abandoned upgrade: {e}")
    
    def _schedule_recovery_sequence(self, user_id: str, plan_type: str):
        """Schedule recovery email sequence"""
        # In production, this would integrate with an email service
        # For now, we'll just log the scheduling
        sequence = self.recovery_sequences.get(plan_type, [])
        
        for i, email in enumerate(sequence):
            logger.info(f"Scheduled recovery email {i+1} for user {user_id} in {email['delay_hours']} hours")

# Service instances
upgrade_flow = UpgradeFlowManager()
trial_manager = TrialManager()
abandoned_cart = AbandonedCartRecovery()