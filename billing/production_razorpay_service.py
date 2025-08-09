"""
Production-Ready Enhanced Razorpay Payment Service
Implements all security best practices and error handling
"""

import os
import json
import logging
import hmac
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Safe Razorpay SDK import
try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False
    try:
        import streamlit as st
        st.warning("⚠️ Razorpay SDK not installed. Run: pip install razorpay")
    except Exception:
        pass  # Don't fail if Streamlit not available

# Safe imports
try:
    from auth.models import User, PlanType
    from database.connection import get_db
except ImportError:
    User = None
    PlanType = None
    get_db = None

logger = logging.getLogger(__name__)

class ProductionRazorpayService:
    """Production-ready Razorpay service with comprehensive error handling"""
    
    def __init__(self):
        self.initialize_client()
    
    def _error(self, code: str, message: str, detail: Any = None):
        """Return structured error response"""
        logger.error(f"{code}: {message} | {detail}")
        return {
            'ok': False,
            'code': code,
            'message': message,
            'detail': str(detail) if detail else None
        }
    
    def initialize_client(self):
        """Initialize Razorpay client with multiple configuration sources"""
        # Debug secrets access (only in debug mode)
        if os.getenv('DEBUG_SECRETS') == '1':
            self._debug_secrets_access()
        
        # Get API credentials
        self.key_id = self._get_api_key_id()
        self.key_secret = self._get_api_key_secret()
        self.webhook_secret = os.getenv('RAZORPAY_WEBHOOK_SECRET')
        
        # Initialize client
        if not self.key_id or not self.key_secret:
            logger.error("❌ Razorpay credentials not found")
            self.client = None
            self.status = "credentials_missing"
        elif not RAZORPAY_AVAILABLE:
            logger.warning("Razorpay SDK not available")
            self.client = None
            self.status = "sdk_missing"
        else:
            try:
                self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
                logger.info("✅ Razorpay client created successfully")
                
                # Test connection (non-blocking)
                if self._test_connection():
                    logger.info("✅ Razorpay connection test passed")
                else:
                    logger.warning("⚠️ Connection test failed, but client available")
                
                self.status = "connected"
                    
            except Exception as e:
                logger.error(f"❌ Failed to initialize Razorpay client: {e}")
                self.client = None
                self.status = "connection_failed"
    
    def _get_api_key_id(self) -> Optional[str]:
        """Get API key ID from multiple sources"""
        # Environment variables
        key_id = os.getenv('RAZORPAY_KEY_ID')
        if key_id:
            return key_id
        
        # Streamlit secrets
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'RAZORPAY_KEY_ID' in st.secrets:
                return st.secrets['RAZORPAY_KEY_ID']
        except Exception:
            pass
        
        return None
    
    def _get_api_key_secret(self) -> Optional[str]:
        """Get API key secret from multiple sources"""
        # Environment variables
        key_secret = os.getenv('RAZORPAY_KEY_SECRET')
        if key_secret:
            return key_secret
        
        # Streamlit secrets
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'RAZORPAY_KEY_SECRET' in st.secrets:
                return st.secrets['RAZORPAY_KEY_SECRET']
        except Exception:
            pass
        
        return None
    
    def _debug_secrets_access(self):
        """Debug secrets access (only in debug mode)"""
        logger.info("🔍 Debugging Razorpay secrets access...")
        
        # Check environment variables
        env_key_id = os.getenv('RAZORPAY_KEY_ID')
        env_key_secret = os.getenv('RAZORPAY_KEY_SECRET')
        logger.info(f"Environment RAZORPAY_KEY_ID: {'✅ Found' if env_key_id else '❌ Missing'}")
        logger.info(f"Environment RAZORPAY_KEY_SECRET: {'✅ Found' if env_key_secret else '❌ Missing'}")
        
        # Check Streamlit secrets
        try:
            import streamlit as st
            if hasattr(st, 'secrets'):
                secrets_key_id = st.secrets.get('RAZORPAY_KEY_ID')
                secrets_key_secret = st.secrets.get('RAZORPAY_KEY_SECRET')
                logger.info(f"Streamlit secrets RAZORPAY_KEY_ID: {'✅ Found' if secrets_key_id else '❌ Missing'}")
                logger.info(f"Streamlit secrets RAZORPAY_KEY_SECRET: {'✅ Found' if secrets_key_secret else '❌ Missing'}")
        except Exception as e:
            logger.error(f"❌ Error accessing Streamlit secrets: {e}")
    
    def _test_connection(self):
        """Test Razorpay connection with lightweight API call"""
        if self.client:
            try:
                # Use a lightweight API call
                self.client.order.all({'count': 1})
                return True
            except Exception as e:
                logger.warning(f"Connection test failed (client may still work): {e}")
                return False
        return False
    
    def create_payment_link(self, amount: int, description: str, customer_email: str, plan_type: PlanType):
        """Create a payment link with comprehensive validation"""
        if not self.client:
            return self._error('client_unavailable', f"Razorpay client not available. Status: {self.status}")
        
        # Validation
        if not isinstance(amount, int) or amount <= 0:
            return self._error('invalid_amount', 'Amount (in paisa) must be a positive integer')
        
        if not customer_email or '@' not in customer_email:
            return self._error('invalid_email', 'Valid customer_email required')
        
        try:
            data = {
                'amount': amount,
                'currency': 'INR',
                'accept_partial': False,
                'description': description[:255] if description else '',
                'customer': {'email': customer_email},
                'notify': {'sms': False, 'email': True},
                'reminder_enable': True,
                'notes': {
                    'plan_type': getattr(plan_type, 'value', str(plan_type)),
                    'product': 'resume_analyzer'
                },
                'callback_url': os.getenv('PAYMENT_CALLBACK_URL') or f"{os.getenv('APP_URL', '')}/api/razorpay/callback",
                'callback_method': 'get'
            }
            
            pl = self.client.payment_link.create(data)
            logger.info(f"Created payment link: {pl.get('id')}")
            return {'ok': True, 'payment_link': pl}
            
        except Exception as e:
            if 'BadRequestError' in str(type(e)):
                return self._error('bad_request', 'Razorpay rejected request', e)
            else:
                return self._error('create_payment_link_failed', 'Unexpected error', e)
    
    def get_payment_methods(self):
        """Get available payment methods"""
        return [
            {'type': 'upi', 'name': 'UPI'},
            {'type': 'card', 'name': 'Credit/Debit Cards'},
            {'type': 'netbanking', 'name': 'Net Banking'},
            {'type': 'wallet', 'name': 'Wallets'},
            {'type': 'emi', 'name': 'EMI'}
        ]
    
    def verify_webhook_signature(self, body: bytes, signature: str) -> bool:
        """Verify webhook signature for security"""
        secret = (self.webhook_secret or os.getenv('RAZORPAY_WEBHOOK_SECRET') or '').encode()
        if not secret:
            logger.error("Webhook secret not configured")
            return False
        
        try:
            digest = hmac.new(secret, body, hashlib.sha256).hexdigest()
            return hmac.compare_digest(digest, signature or '')
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return False
    
    def handle_webhook(self, raw_body: bytes, headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle webhook events securely"""
        signature = headers.get('X-Razorpay-Signature') or headers.get('x-razorpay-signature')
        
        if not self.verify_webhook_signature(raw_body, signature):
            return {'status': 'error', 'message': 'invalid_signature'}
        
        try:
            payload = json.loads(raw_body.decode('utf-8'))
        except Exception:
            return {'status': 'error', 'message': 'invalid_json'}
        
        event = payload.get('event')
        data = payload.get('payload', {})
        logger.info(f"Webhook event: {event}")
        
        # TODO: Update database based on event
        # payment_link.paid, subscription.activated, etc.
        
        return {'status': 'ok', 'event': event}
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get detailed status information for debugging"""
        return {
            'status': self.status,
            'key_id_present': bool(self.key_id),
            'key_secret_present': bool(self.key_secret),
            'sdk_available': RAZORPAY_AVAILABLE,
            'client_initialized': self.client is not None,
            'key_id_preview': self.key_id[:6] + "..." if self.key_id else None  # Only first 6 chars
        }
    
    def reinitialize(self):
        """Reinitialize the Razorpay client"""
        logger.info("🔄 Reinitializing Razorpay client...")
        self.initialize_client()
        return self.status == "connected"

# Global service instance
production_razorpay_service = ProductionRazorpayService()
