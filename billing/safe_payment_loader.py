"""
Safe Payment Service Loader
Loads payment services without causing import errors
"""

import logging

logger = logging.getLogger(__name__)

def get_safe_payment_service():
    """Safely get a payment service without import errors"""
    try:
        # Try to import razorpay SDK first
        import razorpay
        
        # Try production service
        try:
            from billing.production_razorpay_service import production_razorpay_service
            if production_razorpay_service.status == "connected":
                return production_razorpay_service
        except Exception:
            pass
        
        # Try enhanced service
        try:
            from billing.enhanced_razorpay_service import enhanced_razorpay_service
            if enhanced_razorpay_service.status == "connected":
                return enhanced_razorpay_service
        except Exception:
            pass
            
    except ImportError:
        logger.info("Razorpay SDK not available")
    
    # Always fall back to the payment fallback service
    try:
        from billing.payment_fallback import payment_fallback_service
        return payment_fallback_service
    except Exception:
        # Create minimal fallback
        class MinimalFallback:
            def __init__(self):
                self.status = "fallback_mode"
            
            def create_payment_link(self, *args, **kwargs):
                return {'ok': False, 'code': 'unavailable', 'message': 'Payment system not available'}
        
        return MinimalFallback()

# Global safe loader
safe_payment_service = get_safe_payment_service()
