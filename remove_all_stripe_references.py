#!/usr/bin/env python3
"""
Remove all Stripe references and clean up payment system
"""

import os
import glob

def clean_payment_gateway():
    """Clean up payment gateway to remove all Stripe references"""
    
    with open('billing/payment_gateway.py', 'r') as f:
        content = f.read()
    
    # Create a clean payment gateway with only Razorpay
    clean_content = '''"""
Payment Gateway Manager - Razorpay Only
Handles Razorpay payment processing for Indian market
"""

import logging
from enum import Enum
from typing import Dict, Any, List, Optional

from auth.models import User, PlanType
from billing.razorpay_service import razorpay_service

logger = logging.getLogger(__name__)

class PaymentGateway(Enum):
    RAZORPAY = "razorpay"

class PaymentGatewayManager:
    """Manages payment gateway operations - Razorpay only"""
    
    def __init__(self):
        # Check if Razorpay is available
        self.razorpay_available = razorpay_service.client is not None
        self.default_gateway = PaymentGateway.RAZORPAY if self.razorpay_available else None
        
        if not self.razorpay_available:
            logger.warning("No payment gateways available - Razorpay not configured")
    
    def get_recommended_gateway(self, user: User) -> Optional[PaymentGateway]:
        """Get recommended payment gateway (always Razorpay for Indian market)"""
        return PaymentGateway.RAZORPAY if self.razorpay_available else None
    
    def get_available_gateways(self) -> List[Dict[str, Any]]:
        """Get list of available payment gateways"""
        gateways = []
        
        if self.razorpay_available:
            gateways.append({
                'id': 'razorpay',
                'name': 'Razorpay',
                'logo': 'https://razorpay.com/assets/razorpay-logo.svg',
                'description': 'Indian payment processing',
                'currency': 'INR',
                'payment_methods': [
                    'UPI', 'Cards', 'Net Banking', 'Wallets', 'EMI'
                ],
                'fees': '2% + GST'
            })
        
        return gateways
    
    def create_customer(self, user: User, gateway: PaymentGateway = None) -> Dict[str, Any]:
        """Create customer in payment gateway"""
        gateway = gateway or self.default_gateway
        
        if gateway == PaymentGateway.RAZORPAY and self.razorpay_available:
            return razorpay_service.create_customer(user)
        
        return {'ok': False, 'code': 'no_gateway', 'message': 'No available payment gateway'}
    
    def create_subscription(self, customer_id: str, plan_type: PlanType, billing_cycle: str = 'monthly', gateway: PaymentGateway = None):
        """Create subscription"""
        gateway = gateway or self.default_gateway
        
        if gateway == PaymentGateway.RAZORPAY and self.razorpay_available:
            plan = razorpay_service.get_plan_by_type(plan_type, billing_cycle)
            if plan:
                return razorpay_service.create_subscription(customer_id, plan['id'])
        
        return None
    
    def create_payment_link(self, amount: float, description: str, customer_email: str, plan_type: PlanType, gateway: PaymentGateway = None):
        """Create payment link"""
        gateway = gateway or self.default_gateway
        
        if gateway == PaymentGateway.RAZORPAY and self.razorpay_available:
            # Convert amount to paisa (INR)
            amount_paisa = int(amount * 100)
            return razorpay_service.create_payment_link(amount_paisa, description, customer_email, plan_type)
        
        return None
    
    def get_pricing_info(self, plan_type: PlanType, gateway: PaymentGateway = None) -> Dict[str, Any]:
        """Get pricing information for a plan"""
        gateway = gateway or self.default_gateway
        
        if gateway == PaymentGateway.RAZORPAY:
            # Indian pricing in INR
            pricing = {
                PlanType.FREE: {'monthly': 0, 'annual': 0},
                PlanType.PROFESSIONAL: {'monthly': 1499, 'annual': 14990},
                PlanType.BUSINESS: {'monthly': 7999, 'annual': 79990},
                PlanType.ENTERPRISE: {'monthly': 39999, 'annual': 399990}
            }
            
            return {
                'pricing': pricing.get(plan_type, {}),
                'currency': 'INR',
                'symbol': '₹',
                'gateway': 'razorpay',
                'fees': '2% + GST',
                'payment_methods': [
                    'UPI', 'Credit/Debit Cards', 'Net Banking', 
                    'Wallets', 'EMI', 'Bank Transfer'
                ]
            }
        
        return {}
    
    def handle_webhook(self, raw_body: bytes, headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle webhook from payment gateway"""
        if self.razorpay_available:
            return razorpay_service.handle_webhook(raw_body, headers)
        
        return {'status': 'error', 'message': 'Gateway not available'}

# Global instance
payment_gateway_manager = PaymentGatewayManager()
'''
    
    with open('billing/payment_gateway.py', 'w') as f:
        f.write(clean_content)
    
    print("✅ Cleaned payment gateway manager")

def remove_stripe_files():
    """Remove Stripe-specific files"""
    
    stripe_files = [
        'billing/stripe_service.py',
        'test_stripe_integration.py',
        'billing/webhook_handler.py'
    ]
    
    for file_path in stripe_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ Removed {file_path}")
        else:
            print(f"⚠️ {file_path} not found")

def clean_upgrade_flow():
    """Clean upgrade flow to remove Stripe references"""
    
    if not os.path.exists('billing/upgrade_flow.py'):
        print("⚠️ upgrade_flow.py not found")
        return
    
    with open('billing/upgrade_flow.py', 'r') as f:
        content = f.read()
    
    # Remove Stripe imports and references
    content = content.replace("from billing.stripe_service import stripe_service", "# Stripe removed - using Razorpay only")
    content = content.replace("STRIPE_AVAILABLE = True", "STRIPE_AVAILABLE = False")
    content = content.replace("stripe_service", "razorpay_service")
    
    with open('billing/upgrade_flow.py', 'w') as f:
        f.write(content)
    
    print("✅ Cleaned upgrade flow")

def update_app_imports():
    """Update app.py to remove any Stripe imports"""
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Remove any Stripe imports
    lines = content.split('\n')
    clean_lines = []
    
    for line in lines:
        if 'stripe' not in line.lower() or 'streamlit' in line.lower():
            clean_lines.append(line)
        else:
            clean_lines.append(f"# Removed Stripe reference: {line}")
    
    with open('app.py', 'w') as f:
        f.write('\n'.join(clean_lines))
    
    print("✅ Cleaned app.py imports")

def create_simple_payment_service():
    """Create a simple payment service that uses only the fallback"""
    
    simple_service = '''"""
Simple Payment Service - Fallback Only
For when Razorpay SDK is not available
"""

import logging

logger = logging.getLogger(__name__)

class SimplePaymentService:
    """Simple payment service that always uses fallback"""
    
    def __init__(self):
        self.status = "fallback_mode"
        self.client = None
    
    def create_payment_link(self, *args, **kwargs):
        """Always return fallback response"""
        return {
            'ok': False,
            'code': 'sdk_unavailable',
            'message': 'Razorpay SDK not available - using free tier only'
        }
    
    def create_customer(self, *args, **kwargs):
        """Always return fallback response"""
        return {
            'ok': False,
            'code': 'sdk_unavailable',
            'message': 'Payment system not available'
        }
    
    def handle_webhook(self, *args, **kwargs):
        """Always return fallback response"""
        return {
            'status': 'error',
            'message': 'Payment system not available'
        }

# Global instance
simple_payment_service = SimplePaymentService()
'''
    
    with open('billing/simple_payment_service.py', 'w') as f:
        f.write(simple_service)
    
    print("✅ Created simple payment service")

if __name__ == "__main__":
    print("🚀 Removing all Stripe references and cleaning payment system...")
    
    clean_payment_gateway()
    remove_stripe_files()
    clean_upgrade_flow()
    update_app_imports()
    create_simple_payment_service()
    
    print("\n🎉 All Stripe references removed!")
    print("\n📋 What was cleaned:")
    print("1. ✅ Payment gateway manager - Razorpay only")
    print("2. ✅ Removed Stripe service files")
    print("3. ✅ Cleaned upgrade flow")
    print("4. ✅ Updated app imports")
    print("5. ✅ Created simple fallback service")
    print("\n🚀 Payment system is now Stripe-free!")