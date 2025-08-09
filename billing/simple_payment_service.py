"""
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
