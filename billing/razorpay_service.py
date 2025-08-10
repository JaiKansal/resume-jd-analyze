"""
Razorpay Payment Service for Resume + JD Analyzer
Handles subscription payments, billing, and webhooks for Indian market
"""

import os
import json
import logging
import hmac
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Razorpay SDK
try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False

from auth.models import User, PlanType
from database.connection import get_db

logger = logging.getLogger(__name__)

class RazorpayService:
    """Service for handling Razorpay payments and subscriptions"""
    
    def __init__(self):
        # Try to get credentials from multiple sources
        self.key_id = self._get_key_id()
        self.key_secret = self._get_key_secret()
        self.webhook_secret = self._get_webhook_secret()
        
        if not self.key_id or not self.key_secret:
            logger.warning("Razorpay credentials not found. Payment processing will be disabled.")
            self.client = None
        elif not RAZORPAY_AVAILABLE:
            logger.warning("Razorpay SDK not installed. Payment processing will be disabled.")
            self.client = None
        else:
            try:
                self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
                logger.info("Razorpay client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Razorpay client: {e}")
                self.client = None
    
    def _get_key_id(self):
        """Get API key ID from multiple sources"""
        # Try environment variables first
        key_id = os.getenv('RAZORPAY_KEY_ID')
        if key_id:
            return key_id
        
        # Try Streamlit secrets
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'RAZORPAY_KEY_ID' in st.secrets:
                return st.secrets['RAZORPAY_KEY_ID']
        except:
            pass
        
        return None
    
    def _get_key_secret(self):
        """Get API key secret from multiple sources"""
        # Try environment variables first
        key_secret = os.getenv('RAZORPAY_KEY_SECRET')
        if key_secret:
            return key_secret
        
        # Try Streamlit secrets
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'RAZORPAY_KEY_SECRET' in st.secrets:
                return st.secrets['RAZORPAY_KEY_SECRET']
        except:
            pass
        
        return None
    
    def _get_webhook_secret(self):
        """Get webhook secret from multiple sources"""
        # Try environment variables first
        webhook_secret = os.getenv('RAZORPAY_WEBHOOK_SECRET')
        if webhook_secret:
            return webhook_secret
        
        # Try Streamlit secrets
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'RAZORPAY_WEBHOOK_SECRET' in st.secrets:
                return st.secrets['RAZORPAY_WEBHOOK_SECRET']
        except:
            pass
        
        return None
    
    def create_customer(self, user: User) -> Optional[Dict[str, Any]]:
        """Create a Razorpay customer"""
        if not self.client:
            logger.error("Razorpay client not initialized - check API keys")
            return None
        
        try:
            # Prepare customer data with fallbacks
            customer_data = {
                'name': getattr(user, 'first_name', 'User') + ' ' + getattr(user, 'last_name', ''),
                'email': user.email,
                'contact': getattr(user, 'phone', '') or '',
                'notes': {
                    'user_id': str(user.id),
                    'company': getattr(user, 'company_name', '') or '',
                    'role': getattr(user, 'role', 'user').value if hasattr(getattr(user, 'role', None), 'value') else 'user'
                }
            }
            
            # Clean up empty contact field if no phone
            if not customer_data['contact']:
                del customer_data['contact']
            
            logger.info(f"Creating Razorpay customer with data: {customer_data}")
            customer = self.client.customer.create(customer_data)
            logger.info(f"Created Razorpay customer: {customer['id']}")
            return customer
            
        except Exception as e:
            logger.error(f"Failed to create Razorpay customer: {e}")
            logger.error(f"Customer data attempted: {customer_data}")
            return None
    
    def create_subscription_plan(self, plan_type: PlanType, billing_cycle: str = 'monthly') -> Optional[Dict[str, Any]]:
        """Create a Razorpay subscription plan"""
        if not self.client:
            return None
        
        # Plan pricing in paisa (1 INR = 100 paisa)
        plan_pricing = {
            PlanType.FREE: {'monthly': 0, 'annual': 0},
            PlanType.PROFESSIONAL: {'monthly': 149900, 'annual': 1499000},  # ₹1499/month, ₹14990/year
            PlanType.BUSINESS: {'monthly': 799900, 'annual': 7999000},      # ₹7999/month, ₹79990/year
            PlanType.ENTERPRISE: {'monthly': 3999900, 'annual': 39999000}   # ₹39999/month, ₹399990/year
        }
        
        try:
            amount = plan_pricing[plan_type][billing_cycle]
            if amount == 0:
                return None  # Free plan doesn't need Razorpay plan
            
            period = 'monthly' if billing_cycle == 'monthly' else 'yearly'
            interval = 1
            
            plan_data = {
                'period': period,
                'interval': interval,
                'item': {
                    'name': f'Resume Analyzer {plan_type.value.title()} Plan',
                    'amount': amount,
                    'currency': 'INR',
                    'description': f'{plan_type.value.title()} subscription for Resume + JD Analyzer'
                },
                'notes': {
                    'plan_type': plan_type.value,
                    'billing_cycle': billing_cycle
                }
            }
            
            plan = self.client.plan.create(plan_data)
            logger.info(f"Created Razorpay plan: {plan['id']}")
            return plan
            
        except Exception as e:
            logger.error(f"Failed to create Razorpay plan: {e}")
            return None
    
    def create_subscription(self, customer_id: str, plan_id: str, 
                          trial_days: int = 0) -> Optional[Dict[str, Any]]:
        """Create a Razorpay subscription"""
        if not self.client:
            return None
        
        try:
            subscription_data = {
                'plan_id': plan_id,
                'customer_id': customer_id,
                'quantity': 1,
                'total_count': 12 if 'yearly' in plan_id else 120,  # 1 year or 10 years
                'notes': {
                    'created_by': 'resume_analyzer_app'
                }
            }
            
            # Add trial period if specified
            if trial_days > 0:
                trial_end = datetime.now() + timedelta(days=trial_days)
                subscription_data['trial_end'] = int(trial_end.timestamp())
            
            subscription = self.client.subscription.create(subscription_data)
            logger.info(f"Created Razorpay subscription: {subscription['id']}")
            return subscription
            
        except Exception as e:
            logger.error(f"Failed to create Razorpay subscription: {e}")
            return None
    
    def create_payment_link(self, amount: int, description: str, 
                          customer_email: str, plan_type: PlanType) -> Optional[Dict[str, Any]]:
        """Create a payment link for one-time payments"""
        if not self.client:
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
                'callback_url': f"{os.getenv('APP_URL', 'http://localhost:8501')}/payment/success",
                'callback_method': 'get'
            }
            
            payment_link = self.client.payment_link.create(payment_link_data)
            logger.info(f"Created payment link: {payment_link['id']}")
            return payment_link
            
        except Exception as e:
            logger.error(f"Failed to create payment link: {e}")
            return None
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify Razorpay webhook signature"""
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured")
            return False
        
        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Failed to verify webhook signature: {e}")
            return False
    
    def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Razorpay webhook events"""
        event_type = payload.get('event')
        
        try:
            if event_type == 'subscription.activated':
                return self._handle_subscription_activated(payload)
            elif event_type == 'subscription.charged':
                return self._handle_subscription_charged(payload)
            elif event_type == 'subscription.cancelled':
                return self._handle_subscription_cancelled(payload)
            elif event_type == 'payment.captured':
                return self._handle_payment_captured(payload)
            elif event_type == 'payment.failed':
                return self._handle_payment_failed(payload)
            else:
                logger.info(f"Unhandled webhook event: {event_type}")
                return {'status': 'ignored'}
                
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _handle_subscription_activated(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription activation"""
        subscription = payload['payload']['subscription']['entity']
        
        # Update subscription status in database
        db = get_db()
        db.execute_command("""
            UPDATE subscriptions 
            SET status = 'active', 
                razorpay_subscription_id = ?,
                current_period_start = ?,
                current_period_end = ?
            WHERE razorpay_subscription_id = ?
        """, (
            subscription['id'],
            datetime.fromtimestamp(subscription['current_start']).isoformat(),
            datetime.fromtimestamp(subscription['current_end']).isoformat(),
            subscription['id']
        ))
        
        logger.info(f"Activated subscription: {subscription['id']}")
        return {'status': 'processed'}
    
    def _handle_subscription_charged(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful subscription charge"""
        payment = payload['payload']['payment']['entity']
        subscription = payload['payload']['subscription']['entity']
        
        # Record revenue event
        db = get_db()
        db.execute_command("""
            INSERT INTO revenue_events 
            (id, user_id, event_type, amount_usd, currency, razorpay_payment_id, description)
            SELECT ?, u.id, 'subscription', ?, 'INR', ?, ?
            FROM subscriptions s
            JOIN users u ON s.user_id = u.id
            WHERE s.razorpay_subscription_id = ?
        """, (
            str(uuid.uuid4()),
            payment['amount'] / 100,  # Convert paisa to rupees
            payment['id'],
            f"Subscription payment for {subscription['id']}",
            subscription['id']
        ))
        
        logger.info(f"Recorded subscription payment: {payment['id']}")
        return {'status': 'processed'}
    
    def _handle_subscription_cancelled(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription cancellation"""
        subscription = payload['payload']['subscription']['entity']
        
        # Update subscription status
        db = get_db()
        db.execute_command("""
            UPDATE subscriptions 
            SET status = 'cancelled', cancelled_at = ?
            WHERE razorpay_subscription_id = ?
        """, (
            datetime.utcnow().isoformat(),
            subscription['id']
        ))
        
        logger.info(f"Cancelled subscription: {subscription['id']}")
        return {'status': 'processed'}
    
    def _handle_payment_captured(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful one-time payment"""
        payment = payload['payload']['payment']['entity']
        
        # Record revenue event
        db = get_db()
        db.execute_command("""
            INSERT INTO revenue_events 
            (id, event_type, amount_usd, currency, razorpay_payment_id, description)
            VALUES (?, 'service', ?, 'INR', ?, ?)
        """, (
            str(uuid.uuid4()),
            payment['amount'] / 100,
            payment['id'],
            f"One-time payment: {payment.get('description', 'Service payment')}"
        ))
        
        logger.info(f"Recorded one-time payment: {payment['id']}")
        return {'status': 'processed'}
    
    def _handle_payment_failed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment"""
        payment = payload['payload']['payment']['entity']
        
        logger.warning(f"Payment failed: {payment['id']} - {payment.get('error_description', 'Unknown error')}")
        
        # You might want to notify the user or take other actions
        return {'status': 'processed'}
    
    def get_payment_methods(self) -> List[Dict[str, Any]]:
        """Get available payment methods for Indian customers"""
        return [
            {
                'type': 'card',
                'name': 'Credit/Debit Cards',
                'description': 'Visa, Mastercard, RuPay, American Express',
                'icon': '💳'
            },
            {
                'type': 'upi',
                'name': 'UPI',
                'description': 'Google Pay, PhonePe, Paytm, BHIM',
                'icon': '📱'
            },
            {
                'type': 'netbanking',
                'name': 'Net Banking',
                'description': 'All major Indian banks',
                'icon': '🏦'
            },
            {
                'type': 'wallet',
                'name': 'Wallets',
                'description': 'Paytm, Mobikwik, Freecharge',
                'icon': '👛'
            },
            {
                'type': 'emi',
                'name': 'EMI',
                'description': 'No-cost EMI available',
                'icon': '📊'
            }
        ]

# Global instance
razorpay_service = RazorpayService()