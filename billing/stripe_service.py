"""
Stripe service fallback - redirects to Razorpay
This file exists only to prevent import errors
"""

import logging
logger = logging.getLogger(__name__)

class StripeServiceFallback:
    """Fallback class that redirects to Razorpay"""
    
    def __init__(self):
        logger.warning("Stripe.__spec__ called - consider using Razorpay equivalent")
    
    def __getattr__(self, name):
        logger.warning("Stripe.__spec__ called - consider using Razorpay equivalent")
        return lambda *args, **kwargs: None

# Create fallback instance
stripe_service = StripeServiceFallback()

# Module-level fallback
class StripeFallback:
    def __getattr__(self, name):
        logger.warning("Stripe.__spec__ called - consider using Razorpay equivalent")
        return StripeServiceFallback()

# Replace stripe module
import sys
sys.modules['stripe'] = StripeFallback()