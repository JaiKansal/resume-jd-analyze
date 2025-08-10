"""
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

# Export with expected name for compatibility
payment_gateway = payment_gateway_manager
