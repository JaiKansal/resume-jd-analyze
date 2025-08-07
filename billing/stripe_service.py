"""
Stripe service fallback - redirects to Razorpay
You use Razorpay, not Stripe, so this is just a compatibility layer
"""

import logging
from billing.razorpay_service import razorpay_service

logger = logging.getLogger(__name__)

class StripeServiceFallback:
    """Fallback that redirects Stripe calls to Razorpay"""
    
    def __init__(self):
        logger.warning("Stripe service fallback active - redirecting to Razorpay")
        self.razorpay = razorpay_service
    
    def create_subscription(self, *args, **kwargs):
        """Redirect to Razorpay"""
        logger.info("Redirecting Stripe subscription to Razorpay")
        return self.razorpay.create_subscription(*args, **kwargs)
    
    def cancel_subscription(self, *args, **kwargs):
        """Redirect to Razorpay"""
        logger.info("Redirecting Stripe cancellation to Razorpay")
        return self.razorpay.cancel_subscription(*args, **kwargs)
    
    def create_payment_intent(self, *args, **kwargs):
        """Redirect to Razorpay order creation"""
        logger.info("Redirecting Stripe payment intent to Razorpay order")
        return self.razorpay.create_order(*args, **kwargs)
    
    def verify_webhook(self, *args, **kwargs):
        """Redirect to Razorpay webhook verification"""
        logger.info("Redirecting Stripe webhook to Razorpay")
        return self.razorpay.verify_webhook(*args, **kwargs)
    
    def __getattr__(self, name):
        """Redirect any other calls to Razorpay"""
        logger.info(f"Redirecting Stripe method '{name}' to Razorpay")
        return getattr(self.razorpay, name, lambda *args, **kwargs: None)

# Create the fallback instance
stripe_service = StripeServiceFallback()

# Also create a stripe module fallback for imports
class StripeFallback:
    """Fallback for stripe module imports"""
    
    def __init__(self):
        logger.warning("Stripe module fallback active - you should use Razorpay instead")
    
    def __getattr__(self, name):
        logger.warning(f"Stripe.{name} called - consider using Razorpay equivalent")
        return lambda *args, **kwargs: {"error": "Use Razorpay instead of Stripe"}

# Make stripe module available
import sys
sys.modules['stripe'] = StripeFallback()
