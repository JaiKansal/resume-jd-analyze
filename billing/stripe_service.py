"""
Stripe payment processing service for Resume + JD Analyzer
Handles subscription creation, modification, cancellation, and webhook processing
"""

import os
import logging
import stripe
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from auth.models import User, Subscription, SubscriptionPlan, SubscriptionStatus, PlanType
from auth.services import subscription_service, user_service
from database.connection import get_db

logger = logging.getLogger(__name__)

class StripeService:
    """Service for Stripe payment processing and subscription management"""
    
    def __init__(self):
        # Initialize Stripe with API key from environment
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        if not stripe.api_key:
            logger.warning("Stripe API key not found. Payment processing will be disabled.")
    
    def create_customer(self, user: User) -> Optional[str]:
        """Create a Stripe customer for the user"""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.get_full_name(),
                metadata={
                    'user_id': user.id,
                    'company': user.company_name or '',
                    'role': user.role.value
                }
            )
            
            logger.info(f"Created Stripe customer {customer.id} for user {user.id}")
            return customer.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer for user {user.id}: {e}")
            return None
    
    def create_subscription(self, user_id: str, plan_id: str, 
                          payment_method_id: str = None, 
                          trial_days: int = None) -> Optional[Dict[str, Any]]:
        """Create a new Stripe subscription"""
        try:
            user = user_service.get_user_by_id(user_id)
            plan = subscription_service.get_plan_by_id(plan_id)
            
            if not user or not plan:
                logger.error(f"User {user_id} or plan {plan_id} not found")
                return None
            
            # Get or create Stripe customer
            stripe_customer_id = self._get_or_create_customer(user)
            if not stripe_customer_id:
                return None
            
            # Create subscription parameters
            subscription_params = {
                'customer': stripe_customer_id,
                'items': [{
                    'price': self._get_stripe_price_id(plan),
                }],
                'metadata': {
                    'user_id': user_id,
                    'plan_id': plan_id,
                    'plan_type': plan.plan_type.value
                },
                'expand': ['latest_invoice.payment_intent']
            }
            
            # Add payment method if provided
            if payment_method_id:
                subscription_params['default_payment_method'] = payment_method_id
            
            # Add trial period if specified
            if trial_days:
                subscription_params['trial_period_days'] = trial_days
            
            # Create Stripe subscription
            stripe_subscription = stripe.Subscription.create(**subscription_params)
            
            # Update local subscription record
            local_subscription = subscription_service.get_user_subscription(user_id)
            if local_subscription:
                local_subscription.stripe_subscription_id = stripe_subscription.id
                local_subscription.stripe_customer_id = stripe_customer_id
                local_subscription.status = self._map_stripe_status(stripe_subscription.status)
                local_subscription.current_period_start = datetime.fromtimestamp(
                    stripe_subscription.current_period_start
                )
                local_subscription.current_period_end = datetime.fromtimestamp(
                    stripe_subscription.current_period_end
                )
                
                if stripe_subscription.trial_end:
                    local_subscription.trial_end = datetime.fromtimestamp(
                        stripe_subscription.trial_end
                    )
                
                subscription_service.update_subscription(local_subscription)
            
            logger.info(f"Created Stripe subscription {stripe_subscription.id} for user {user_id}")
            
            return {
                'subscription_id': stripe_subscription.id,
                'client_secret': stripe_subscription.latest_invoice.payment_intent.client_secret,
                'status': stripe_subscription.status
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe subscription: {e}")
            return None
    
    def update_subscription(self, subscription_id: str, new_plan_id: str) -> bool:
        """Update an existing Stripe subscription to a new plan"""
        try:
            # Get current subscription
            stripe_subscription = stripe.Subscription.retrieve(subscription_id)
            new_plan = subscription_service.get_plan_by_id(new_plan_id)
            
            if not new_plan:
                logger.error(f"Plan {new_plan_id} not found")
                return False
            
            # Update subscription item
            stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': stripe_subscription['items']['data'][0].id,
                    'price': self._get_stripe_price_id(new_plan),
                }],
                metadata={
                    **stripe_subscription.metadata,
                    'plan_id': new_plan_id,
                    'plan_type': new_plan.plan_type.value
                }
            )
            
            logger.info(f"Updated Stripe subscription {subscription_id} to plan {new_plan_id}")
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update Stripe subscription {subscription_id}: {e}")
            return False
    
    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> bool:
        """Cancel a Stripe subscription"""
        try:
            if at_period_end:
                # Cancel at period end
                stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                # Cancel immediately
                stripe.Subscription.delete(subscription_id)
            
            logger.info(f"Cancelled Stripe subscription {subscription_id}")
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel Stripe subscription {subscription_id}: {e}")
            return False
    
    def create_payment_intent(self, amount: int, currency: str = 'usd', 
                            customer_id: str = None, 
                            metadata: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """Create a payment intent for one-time payments"""
        try:
            payment_intent_params = {
                'amount': amount,  # Amount in cents
                'currency': currency,
                'automatic_payment_methods': {'enabled': True},
            }
            
            if customer_id:
                payment_intent_params['customer'] = customer_id
            
            if metadata:
                payment_intent_params['metadata'] = metadata
            
            payment_intent = stripe.PaymentIntent.create(**payment_intent_params)
            
            return {
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create payment intent: {e}")
            return None
    
    def handle_webhook(self, payload: str, signature: str) -> bool:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            # Handle different event types
            if event['type'] == 'customer.subscription.created':
                self._handle_subscription_created(event['data']['object'])
            elif event['type'] == 'customer.subscription.updated':
                self._handle_subscription_updated(event['data']['object'])
            elif event['type'] == 'customer.subscription.deleted':
                self._handle_subscription_deleted(event['data']['object'])
            elif event['type'] == 'invoice.payment_succeeded':
                self._handle_payment_succeeded(event['data']['object'])
            elif event['type'] == 'invoice.payment_failed':
                self._handle_payment_failed(event['data']['object'])
            else:
                logger.info(f"Unhandled webhook event type: {event['type']}")
            
            return True
            
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            return False
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            return False
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return False
    
    def get_customer_payment_methods(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get customer's saved payment methods"""
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )
            
            return [{
                'id': pm.id,
                'type': pm.type,
                'card': {
                    'brand': pm.card.brand,
                    'last4': pm.card.last4,
                    'exp_month': pm.card.exp_month,
                    'exp_year': pm.card.exp_year
                }
            } for pm in payment_methods.data]
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get payment methods for customer {customer_id}: {e}")
            return []
    
    def get_billing_history(self, customer_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get customer's billing history"""
        try:
            invoices = stripe.Invoice.list(
                customer=customer_id,
                limit=limit
            )
            
            return [{
                'id': invoice.id,
                'amount_paid': invoice.amount_paid / 100,  # Convert from cents
                'currency': invoice.currency,
                'status': invoice.status,
                'created': datetime.fromtimestamp(invoice.created),
                'period_start': datetime.fromtimestamp(invoice.period_start) if invoice.period_start else None,
                'period_end': datetime.fromtimestamp(invoice.period_end) if invoice.period_end else None,
                'invoice_pdf': invoice.invoice_pdf
            } for invoice in invoices.data]
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get billing history for customer {customer_id}: {e}")
            return []
    
    def _get_or_create_customer(self, user: User) -> Optional[str]:
        """Get existing Stripe customer or create new one"""
        # Check if user already has a Stripe customer ID
        subscription = subscription_service.get_user_subscription(user.id)
        if subscription and subscription.stripe_customer_id:
            return subscription.stripe_customer_id
        
        # Create new customer
        return self.create_customer(user)
    
    def _get_stripe_price_id(self, plan: SubscriptionPlan) -> str:
        """Get Stripe price ID for a subscription plan"""
        # In production, these would be actual Stripe price IDs
        # For now, we'll use placeholder IDs based on plan type
        price_mapping = {
            PlanType.FREE: 'price_free',
            PlanType.PROFESSIONAL: 'price_professional_monthly',
            PlanType.BUSINESS: 'price_business_monthly',
            PlanType.ENTERPRISE: 'price_enterprise_monthly'
        }
        
        return price_mapping.get(plan.plan_type, 'price_professional_monthly')
    
    def _map_stripe_status(self, stripe_status: str) -> SubscriptionStatus:
        """Map Stripe subscription status to our internal status"""
        status_mapping = {
            'active': SubscriptionStatus.ACTIVE,
            'canceled': SubscriptionStatus.CANCELLED,
            'past_due': SubscriptionStatus.PAST_DUE,
            'trialing': SubscriptionStatus.TRIALING,
            'incomplete': SubscriptionStatus.INCOMPLETE,
            'incomplete_expired': SubscriptionStatus.CANCELLED
        }
        
        return status_mapping.get(stripe_status, SubscriptionStatus.ACTIVE)
    
    def _handle_subscription_created(self, subscription_data: Dict[str, Any]):
        """Handle subscription created webhook"""
        user_id = subscription_data['metadata'].get('user_id')
        if user_id:
            logger.info(f"Subscription created for user {user_id}")
            # Update local subscription record
            self._sync_subscription_from_stripe(subscription_data)
    
    def _handle_subscription_updated(self, subscription_data: Dict[str, Any]):
        """Handle subscription updated webhook"""
        user_id = subscription_data['metadata'].get('user_id')
        if user_id:
            logger.info(f"Subscription updated for user {user_id}")
            # Update local subscription record
            self._sync_subscription_from_stripe(subscription_data)
    
    def _handle_subscription_deleted(self, subscription_data: Dict[str, Any]):
        """Handle subscription deleted webhook"""
        user_id = subscription_data['metadata'].get('user_id')
        if user_id:
            logger.info(f"Subscription cancelled for user {user_id}")
            # Update local subscription to cancelled status
            subscription = subscription_service.get_user_subscription(user_id)
            if subscription:
                subscription.status = SubscriptionStatus.CANCELLED
                subscription.cancelled_at = datetime.utcnow()
                subscription_service.update_subscription(subscription)
    
    def _handle_payment_succeeded(self, invoice_data: Dict[str, Any]):
        """Handle successful payment webhook"""
        customer_id = invoice_data['customer']
        amount = invoice_data['amount_paid'] / 100  # Convert from cents
        
        logger.info(f"Payment succeeded for customer {customer_id}: ${amount}")
        
        # Track revenue event
        self._track_revenue_event(
            customer_id=customer_id,
            amount=amount,
            event_type='subscription',
            stripe_payment_id=invoice_data.get('payment_intent'),
            stripe_invoice_id=invoice_data['id']
        )
    
    def _handle_payment_failed(self, invoice_data: Dict[str, Any]):
        """Handle failed payment webhook"""
        customer_id = invoice_data['customer']
        logger.warning(f"Payment failed for customer {customer_id}")
        
        # Update subscription status to past_due
        # This would trigger dunning management logic
        subscription = self._get_subscription_by_customer_id(customer_id)
        if subscription:
            subscription.status = SubscriptionStatus.PAST_DUE
            subscription_service.update_subscription(subscription)
    
    def _sync_subscription_from_stripe(self, stripe_subscription: Dict[str, Any]):
        """Sync local subscription with Stripe subscription data"""
        user_id = stripe_subscription['metadata'].get('user_id')
        if not user_id:
            return
        
        subscription = subscription_service.get_user_subscription(user_id)
        if subscription:
            subscription.stripe_subscription_id = stripe_subscription['id']
            subscription.status = self._map_stripe_status(stripe_subscription['status'])
            subscription.current_period_start = datetime.fromtimestamp(
                stripe_subscription['current_period_start']
            )
            subscription.current_period_end = datetime.fromtimestamp(
                stripe_subscription['current_period_end']
            )
            
            if stripe_subscription.get('trial_end'):
                subscription.trial_end = datetime.fromtimestamp(
                    stripe_subscription['trial_end']
                )
            
            subscription_service.update_subscription(subscription)
    
    def _get_subscription_by_customer_id(self, customer_id: str) -> Optional[Subscription]:
        """Get subscription by Stripe customer ID"""
        db = get_db()
        query = """
            SELECT s.*, sp.id as plan_id_full, sp.name, sp.plan_type, sp.price_monthly, sp.price_annual,
                   sp.monthly_analysis_limit, sp.features, sp.is_active, sp.created_at as plan_created_at
            FROM subscriptions s
            JOIN subscription_plans sp ON s.plan_id = sp.id
            WHERE s.stripe_customer_id = ?
            ORDER BY s.created_at DESC
            LIMIT 1
        """
        
        result = db.get_single_result(query, (customer_id,))
        if result:
            return subscription_service._row_to_subscription(result)
        return None
    
    def _track_revenue_event(self, customer_id: str, amount: float, event_type: str,
                           stripe_payment_id: str = None, stripe_invoice_id: str = None):
        """Track revenue event in database"""
        try:
            subscription = self._get_subscription_by_customer_id(customer_id)
            if not subscription:
                return
            
            db = get_db()
            query = """
                INSERT INTO revenue_events (
                    id, user_id, subscription_id, event_type, amount_usd,
                    stripe_payment_id, stripe_invoice_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            import uuid
            params = (
                str(uuid.uuid4()),
                subscription.user_id,
                subscription.id,
                event_type,
                amount,
                stripe_payment_id,
                stripe_invoice_id,
                datetime.utcnow()
            )
            
            db.execute_command(query, params)
            logger.info(f"Tracked revenue event: {event_type} ${amount} for user {subscription.user_id}")
            
        except Exception as e:
            logger.error(f"Failed to track revenue event: {e}")

# Service instance
stripe_service = StripeService()