"""
Payment Gateway Manager
Handles both Stripe (international) and Razorpay (India) payment processing
"""

import os
import logging
from typing import Dict, Any, Optional, List
from enum import Enum

from auth.models import User, PlanType
# Stripe service removed - using Razorpay only
from billing.razorpay_service import razorpay_service

logger = logging.getLogger(__name__)

class PaymentGateway(Enum):
    # STRIPE = "stripe"  # Removed - using Razorpay only
    RAZORPAY = "razorpay"

class PaymentGatewayManager:
    """Manages multiple payment gateways based on user location and preferences"""
    
    def __init__(self):
        # Check if payment gateways are available
        self.stripe_available = hasattr(razorpay_service)  # Using Razorpay instead of Stripe, 'create_customer') and os.getenv('STRIPE_SECRET_KEY') is not None
        self.razorpay_available = razorpay_service.client is not None
        
        # Default gateway based on availability
        if self.razorpay_available:
            self.default_gateway = PaymentGateway.RAZORPAY
        elif self.stripe_available:
            self.default_gateway = PaymentGateway.STRIPE
        else:
            self.default_gateway = None
            logger.warning("No payment gateways available")
    
    def get_recommended_gateway(self, user: User) -> Optional[PaymentGateway]:
        """Get recommended payment gateway based on user location"""
        # Indian users should use Razorpay for better rates and local payment methods
        if user.country == 'IN' or user.country == 'India':
            return PaymentGateway.RAZORPAY if self.razorpay_available else PaymentGateway.STRIPE
        
        # International users can use either, but Stripe has better global coverage
        return PaymentGateway.STRIPE if self.stripe_available else PaymentGateway.RAZORPAY
    
    def get_available_gateways(self) -> List[Dict[str, Any]]:
        """Get list of available payment gateways"""
        gateways = []
        
        if self.razorpay_available:
            gateways.append({
                'id': 'razorpay',
                'name': 'Razorpay',
                'description': 'Best for Indian customers',
                'currency': 'INR',
                'fees': '2% domestic, 3% international',
                'payment_methods': ['Cards', 'UPI', 'Net Banking', 'Wallets', 'EMI'],
                'countries': ['India'],
                'recommended_for': 'Indian customers'
            })
        
        if self.stripe_available:
            gateways.append({
                'id': 'stripe',
                'name': 'Stripe',
                'description': 'Global payment processing',
                'currency': 'USD',
                'fees': '2.9% + $0.30 per transaction',
                'payment_methods': ['Cards', 'Digital Wallets', 'Bank Transfers'],
                'countries': ['Global (except India)'],
                'recommended_for': 'International customers'
            })
        
        return gateways
    
    def create_customer(self, user: User, gateway: PaymentGateway = None) -> Optional[Dict[str, Any]]:
        """Create customer in the specified payment gateway"""
        if not gateway:
            gateway = self.get_recommended_gateway(user)
        
        if gateway == PaymentGateway.RAZORPAY and self.razorpay_available:
            return razorpay_service.create_customer(user)
        elif gateway == PaymentGateway.STRIPE and self.stripe_available:
            return razorpay_service  # Using Razorpay instead of Stripe.create_customer(user)
        else:
            logger.error(f"Gateway {gateway} not available")
            return None
    
    def create_subscription(self, customer_id: str, plan_type: PlanType, 
                          billing_cycle: str = 'monthly', gateway: PaymentGateway = None) -> Optional[Dict[str, Any]]:
        """Create subscription in the specified payment gateway"""
        if not gateway:
            gateway = self.default_gateway
        
        if gateway == PaymentGateway.RAZORPAY and self.razorpay_available:
            # First create the plan, then the subscription
            plan = razorpay_service.create_subscription_plan(plan_type, billing_cycle)
            if plan:
                return razorpay_service.create_subscription(customer_id, plan['id'])
        elif gateway == PaymentGateway.STRIPE and self.stripe_available:
            return razorpay_service  # Using Razorpay instead of Stripe.create_subscription(customer_id, plan_type, billing_cycle)
        
        return None
    
    def create_payment_link(self, amount: float, description: str, customer_email: str, 
                          plan_type: PlanType, gateway: PaymentGateway = None) -> Optional[Dict[str, Any]]:
        """Create payment link in the specified gateway"""
        if not gateway:
            gateway = self.default_gateway
        
        if gateway == PaymentGateway.RAZORPAY and self.razorpay_available:
            # Convert amount to paisa (INR)
            amount_paisa = int(amount * 100)
            return razorpay_service.create_payment_link(amount_paisa, description, customer_email, plan_type)
        elif gateway == PaymentGateway.STRIPE and self.stripe_available:
            # Convert amount to cents (USD)
            amount_cents = int(amount * 100)
            return razorpay_service  # Using Razorpay instead of Stripe.create_payment_link(amount_cents, description, customer_email, plan_type)
        
        return None
    
    def get_pricing_for_gateway(self, plan_type: PlanType, gateway: PaymentGateway, 
                              billing_cycle: str = 'monthly') -> Dict[str, Any]:
        """Get pricing information for specific gateway"""
        if gateway == PaymentGateway.RAZORPAY:
            # Indian pricing in INR
            pricing = {
                PlanType.FREE: {'monthly': 0, 'annual': 0},
                PlanType.PROFESSIONAL: {'monthly': 1499, 'annual': 14990},  # ₹1499/month
                PlanType.BUSINESS: {'monthly': 7999, 'annual': 79990},      # ₹7999/month  
                PlanType.ENTERPRISE: {'monthly': 39999, 'annual': 399990}   # ₹39999/month
            }
            
            return {
                'amount': pricing[plan_type][billing_cycle],
                'currency': 'INR',
                'symbol': '₹',
                'gateway': 'razorpay',
                'fees': '2% (domestic) + GST',
                'payment_methods': razorpay_service.get_payment_methods()
            }
        
        elif gateway == PaymentGateway.STRIPE:
            # International pricing in USD
            pricing = {
                PlanType.FREE: {'monthly': 0, 'annual': 0},
                PlanType.PROFESSIONAL: {'monthly': 19, 'annual': 190},
                PlanType.BUSINESS: {'monthly': 99, 'annual': 990},
                PlanType.ENTERPRISE: {'monthly': 500, 'annual': 5000}
            }
            
            return {
                'amount': pricing[plan_type][billing_cycle],
                'currency': 'USD',
                'symbol': '$',
                'gateway': 'stripe',
                'fees': '2.9% + $0.30',
                'payment_methods': [
                    {'type': 'card', 'name': 'Credit/Debit Cards', 'icon': '💳'},
                    {'type': 'wallet', 'name': 'Digital Wallets', 'icon': '📱'}
                ]
            }
        
        return {}
    
    def handle_webhook(self, gateway: PaymentGateway, payload: Dict[str, Any], 
                      signature: str = None) -> Dict[str, Any]:
        """Handle webhook from specified gateway"""
        if gateway == PaymentGateway.RAZORPAY and self.razorpay_available:
            return razorpay_service.handle_webhook(payload)
        elif gateway == PaymentGateway.STRIPE and self.stripe_available:
            return razorpay_service  # Using Razorpay instead of Stripe.handle_webhook(payload, signature)
        
        return {'status': 'error', 'message': 'Gateway not available'}

# Global instance
payment_gateway = PaymentGatewayManager()