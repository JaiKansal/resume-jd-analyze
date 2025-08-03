"""
Stripe webhook handler for Resume + JD Analyzer
Handles subscription events, payment processing, and dunning management
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from billing.stripe_service import stripe_service
from billing.usage_tracker import billing_system
from auth.services import subscription_service, user_service
from auth.models import SubscriptionStatus

logger = logging.getLogger(__name__)

class StripeWebhookHandler:
    """Handles Stripe webhook events for subscription management"""
    
    def __init__(self):
        self.stripe_service = stripe_service
        self.billing_system = billing_system
    
    def handle_webhook(self, payload: str, signature: str) -> Dict[str, Any]:
        """Main webhook handler that routes events to appropriate handlers"""
        try:
            # Verify webhook signature and parse event
            if not self.stripe_service.handle_webhook(payload, signature):
                return {'error': 'Invalid webhook signature'}, 400
            
            event = json.loads(payload)
            event_type = event['type']
            event_data = event['data']['object']
            
            logger.info(f"Processing webhook event: {event_type}")
            
            # Route to appropriate handler
            handlers = {
                'customer.subscription.created': self._handle_subscription_created,
                'customer.subscription.updated': self._handle_subscription_updated,
                'customer.subscription.deleted': self._handle_subscription_deleted,
                'customer.subscription.trial_will_end': self._handle_trial_will_end,
                'invoice.payment_succeeded': self._handle_payment_succeeded,
                'invoice.payment_failed': self._handle_payment_failed,
                'invoice.created': self._handle_invoice_created,
                'invoice.finalized': self._handle_invoice_finalized,
                'customer.created': self._handle_customer_created,
                'customer.updated': self._handle_customer_updated,
                'payment_method.attached': self._handle_payment_method_attached,
                'setup_intent.succeeded': self._handle_setup_intent_succeeded
            }
            
            handler = handlers.get(event_type)
            if handler:
                result = handler(event_data)
                logger.info(f"Successfully processed {event_type}")
                return result
            else:
                logger.info(f"Unhandled webhook event type: {event_type}")
                return {'status': 'ignored'}
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return {'error': str(e)}, 500
    
    def _handle_subscription_created(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription creation"""
        user_id = subscription_data['metadata'].get('user_id')
        if not user_id:
            logger.warning("Subscription created without user_id in metadata")
            return {'status': 'ignored'}
        
        # Update local subscription record
        subscription = subscription_service.get_user_subscription(user_id)
        if subscription:
            subscription.stripe_subscription_id = subscription_data['id']
            subscription.stripe_customer_id = subscription_data['customer']
            subscription.status = self._map_stripe_status(subscription_data['status'])
            subscription.current_period_start = datetime.fromtimestamp(
                subscription_data['current_period_start']
            )
            subscription.current_period_end = datetime.fromtimestamp(
                subscription_data['current_period_end']
            )
            
            if subscription_data.get('trial_end'):
                subscription.trial_end = datetime.fromtimestamp(
                    subscription_data['trial_end']
                )
            
            subscription_service.update_subscription(subscription)
            
            # Send welcome email
            self._send_subscription_welcome_email(user_id, subscription)
        
        return {'status': 'processed'}
    
    def _handle_subscription_updated(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription updates"""
        user_id = subscription_data['metadata'].get('user_id')
        if not user_id:
            return {'status': 'ignored'}
        
        subscription = subscription_service.get_user_subscription(user_id)
        if subscription:
            old_status = subscription.status
            
            # Update subscription details
            subscription.status = self._map_stripe_status(subscription_data['status'])
            subscription.current_period_start = datetime.fromtimestamp(
                subscription_data['current_period_start']
            )
            subscription.current_period_end = datetime.fromtimestamp(
                subscription_data['current_period_end']
            )
            subscription.cancel_at_period_end = subscription_data.get('cancel_at_period_end', False)
            
            if subscription_data.get('canceled_at'):
                subscription.cancelled_at = datetime.fromtimestamp(
                    subscription_data['canceled_at']
                )
            
            subscription_service.update_subscription(subscription)
            
            # Handle status changes
            if old_status != subscription.status:
                self._handle_subscription_status_change(user_id, old_status, subscription.status)
        
        return {'status': 'processed'}
    
    def _handle_subscription_deleted(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription cancellation"""
        user_id = subscription_data['metadata'].get('user_id')
        if not user_id:
            return {'status': 'ignored'}
        
        subscription = subscription_service.get_user_subscription(user_id)
        if subscription:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = datetime.utcnow()
            subscription_service.update_subscription(subscription)
            
            # Create free subscription for user
            free_plan = subscription_service.get_plan_by_type(subscription_service.PlanType.FREE)
            if free_plan:
                subscription_service.create_subscription(user_id, free_plan.id)
            
            # Send cancellation confirmation email
            self._send_subscription_cancelled_email(user_id)
        
        return {'status': 'processed'}
    
    def _handle_trial_will_end(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trial ending soon notification"""
        user_id = subscription_data['metadata'].get('user_id')
        if not user_id:
            return {'status': 'ignored'}
        
        # Send trial ending notification
        trial_end_date = datetime.fromtimestamp(subscription_data['trial_end'])
        days_remaining = (trial_end_date - datetime.utcnow()).days
        
        self._send_trial_ending_email(user_id, days_remaining)
        
        return {'status': 'processed'}
    
    def _handle_payment_succeeded(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment"""
        customer_id = invoice_data['customer']
        amount_paid = invoice_data['amount_paid'] / 100  # Convert from cents
        
        # Find subscription by customer ID
        subscription = self._get_subscription_by_customer_id(customer_id)
        if not subscription:
            return {'status': 'ignored'}
        
        # Track revenue event
        self._track_revenue_event(
            user_id=subscription.user_id,
            subscription_id=subscription.id,
            amount=amount_paid,
            event_type='subscription_payment',
            stripe_payment_id=invoice_data.get('payment_intent'),
            stripe_invoice_id=invoice_data['id']
        )
        
        # Reset usage if this is a new billing period
        if invoice_data.get('billing_reason') == 'subscription_cycle':
            subscription.reset_monthly_usage()
            subscription_service.update_subscription(subscription)
        
        # Send payment confirmation email
        self._send_payment_success_email(subscription.user_id, amount_paid)
        
        return {'status': 'processed'}
    
    def _handle_payment_failed(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment with dunning management"""
        customer_id = invoice_data['customer']
        subscription = self._get_subscription_by_customer_id(customer_id)
        
        if not subscription:
            return {'status': 'ignored'}
        
        # Update subscription status
        subscription.status = SubscriptionStatus.PAST_DUE
        subscription_service.update_subscription(subscription)
        
        # Get attempt count from invoice
        attempt_count = invoice_data.get('attempt_count', 1)
        
        # Handle dunning management
        self.billing_system.handle_failed_payment(subscription.id, attempt_count)
        
        return {'status': 'processed'}
    
    def _handle_invoice_created(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invoice creation"""
        customer_id = invoice_data['customer']
        subscription = self._get_subscription_by_customer_id(customer_id)
        
        if not subscription:
            return {'status': 'ignored'}
        
        # Send upcoming invoice notification for large amounts
        amount = invoice_data['amount_due'] / 100
        if amount > 100:  # Notify for invoices over $100
            self._send_upcoming_invoice_email(subscription.user_id, amount, invoice_data)
        
        return {'status': 'processed'}
    
    def _handle_invoice_finalized(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invoice finalization"""
        customer_id = invoice_data['customer']
        subscription = self._get_subscription_by_customer_id(customer_id)
        
        if not subscription:
            return {'status': 'ignored'}
        
        # Create local invoice record
        self._create_local_invoice_record(subscription, invoice_data)
        
        return {'status': 'processed'}
    
    def _handle_customer_created(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer creation"""
        user_id = customer_data['metadata'].get('user_id')
        if not user_id:
            return {'status': 'ignored'}
        
        # Update user's Stripe customer ID
        subscription = subscription_service.get_user_subscription(user_id)
        if subscription:
            subscription.stripe_customer_id = customer_data['id']
            subscription_service.update_subscription(subscription)
        
        return {'status': 'processed'}
    
    def _handle_customer_updated(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer updates"""
        # Log customer updates for audit purposes
        logger.info(f"Customer {customer_data['id']} updated")
        return {'status': 'processed'}
    
    def _handle_payment_method_attached(self, payment_method_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment method attachment"""
        customer_id = payment_method_data['customer']
        subscription = self._get_subscription_by_customer_id(customer_id)
        
        if subscription:
            # Send payment method confirmation email
            self._send_payment_method_updated_email(subscription.user_id, payment_method_data)
        
        return {'status': 'processed'}
    
    def _handle_setup_intent_succeeded(self, setup_intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful setup intent"""
        customer_id = setup_intent_data.get('customer')
        if customer_id:
            subscription = self._get_subscription_by_customer_id(customer_id)
            if subscription:
                # Send setup confirmation email
                self._send_setup_complete_email(subscription.user_id)
        
        return {'status': 'processed'}
    
    def _map_stripe_status(self, stripe_status: str) -> SubscriptionStatus:
        """Map Stripe subscription status to internal status"""
        status_mapping = {
            'active': SubscriptionStatus.ACTIVE,
            'canceled': SubscriptionStatus.CANCELLED,
            'past_due': SubscriptionStatus.PAST_DUE,
            'trialing': SubscriptionStatus.TRIALING,
            'incomplete': SubscriptionStatus.INCOMPLETE,
            'incomplete_expired': SubscriptionStatus.CANCELLED
        }
        
        return status_mapping.get(stripe_status, SubscriptionStatus.ACTIVE)
    
    def _get_subscription_by_customer_id(self, customer_id: str) -> Optional[Any]:
        """Get subscription by Stripe customer ID"""
        from database.connection import get_db
        
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
            subscription = subscription_service._row_to_subscription(result)
            # Create plan object
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
            subscription.plan = subscription_service._row_to_plan(plan_data)
            return subscription
        return None
    
    def _handle_subscription_status_change(self, user_id: str, old_status: SubscriptionStatus, 
                                         new_status: SubscriptionStatus):
        """Handle subscription status changes"""
        if old_status == SubscriptionStatus.TRIALING and new_status == SubscriptionStatus.ACTIVE:
            self._send_trial_converted_email(user_id)
        elif new_status == SubscriptionStatus.PAST_DUE:
            self._send_payment_failed_email(user_id)
        elif new_status == SubscriptionStatus.CANCELLED:
            self._send_subscription_cancelled_email(user_id)
    
    def _track_revenue_event(self, user_id: str, subscription_id: str, amount: float,
                           event_type: str, stripe_payment_id: str = None,
                           stripe_invoice_id: str = None):
        """Track revenue event in database"""
        try:
            from database.connection import get_db
            import uuid
            
            db = get_db()
            query = """
                INSERT INTO revenue_events (
                    id, user_id, subscription_id, event_type, amount_usd,
                    stripe_payment_id, stripe_invoice_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                str(uuid.uuid4()),
                user_id,
                subscription_id,
                event_type,
                amount,
                stripe_payment_id,
                stripe_invoice_id,
                datetime.utcnow()
            )
            
            db.execute_command(query, params)
            logger.info(f"Tracked revenue event: {event_type} ${amount} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to track revenue event: {e}")
    
    def _create_local_invoice_record(self, subscription: Any, invoice_data: Dict[str, Any]):
        """Create local invoice record"""
        try:
            from database.connection import get_db
            import uuid
            
            db = get_db()
            query = """
                INSERT INTO invoices (
                    id, user_id, subscription_id, billing_period_start, billing_period_end,
                    base_amount, usage_amount, total_amount, currency, status,
                    stripe_invoice_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            amount = invoice_data['amount_due'] / 100
            
            params = (
                str(uuid.uuid4()),
                subscription.user_id,
                subscription.id,
                datetime.fromtimestamp(invoice_data['period_start']),
                datetime.fromtimestamp(invoice_data['period_end']),
                amount,
                0.0,  # Usage amount (calculated separately)
                amount,
                invoice_data['currency'].upper(),
                'pending',
                invoice_data['id'],
                datetime.utcnow()
            )
            
            db.execute_command(query, params)
            
        except Exception as e:
            logger.error(f"Failed to create local invoice record: {e}")
    
    # Email notification methods (placeholders for email service integration)
    def _send_subscription_welcome_email(self, user_id: str, subscription: Any):
        """Send welcome email for new subscription"""
        logger.info(f"Sending welcome email to user {user_id}")
        # TODO: Integrate with email service
    
    def _send_subscription_cancelled_email(self, user_id: str):
        """Send subscription cancellation email"""
        logger.info(f"Sending cancellation email to user {user_id}")
        # TODO: Integrate with email service
    
    def _send_trial_ending_email(self, user_id: str, days_remaining: int):
        """Send trial ending notification"""
        logger.info(f"Sending trial ending email to user {user_id} ({days_remaining} days)")
        # TODO: Integrate with email service
    
    def _send_trial_converted_email(self, user_id: str):
        """Send trial conversion confirmation"""
        logger.info(f"Sending trial conversion email to user {user_id}")
        # TODO: Integrate with email service
    
    def _send_payment_success_email(self, user_id: str, amount: float):
        """Send payment success confirmation"""
        logger.info(f"Sending payment success email to user {user_id}: ${amount}")
        # TODO: Integrate with email service
    
    def _send_payment_failed_email(self, user_id: str):
        """Send payment failure notification"""
        logger.info(f"Sending payment failed email to user {user_id}")
        # TODO: Integrate with email service
    
    def _send_upcoming_invoice_email(self, user_id: str, amount: float, invoice_data: Dict[str, Any]):
        """Send upcoming invoice notification"""
        logger.info(f"Sending upcoming invoice email to user {user_id}: ${amount}")
        # TODO: Integrate with email service
    
    def _send_payment_method_updated_email(self, user_id: str, payment_method_data: Dict[str, Any]):
        """Send payment method update confirmation"""
        logger.info(f"Sending payment method update email to user {user_id}")
        # TODO: Integrate with email service
    
    def _send_setup_complete_email(self, user_id: str):
        """Send setup completion confirmation"""
        logger.info(f"Sending setup complete email to user {user_id}")
        # TODO: Integrate with email service

# Service instance
webhook_handler = StripeWebhookHandler()

# Flask route for webhook endpoint
def create_webhook_app() -> Flask:
    """Create Flask app for webhook handling"""
    app = Flask(__name__)
    
    @app.route('/webhooks/stripe', methods=['POST'])
    def handle_stripe_webhook():
        payload = request.get_data(as_text=True)
        signature = request.headers.get('Stripe-Signature')
        
        if not signature:
            return jsonify({'error': 'Missing signature'}), 400
        
        result = webhook_handler.handle_webhook(payload, signature)
        
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        else:
            return jsonify(result)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy'})
    
    return app