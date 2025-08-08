"""
Enhanced Razorpay Payment Service with Better Error Handling
"""

import os
import json
import logging
import hmac
import hashlib
import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Razorpay SDK with fallback
try:
    import razorpay
    print("Razorpay SDK import success")
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False
    st.warning("⚠️ Razorpay SDK not installed. Run: pip install razorpay")

try:
    from auth.models import User, PlanType
    from database.connection import get_db
except ImportError:
    # Fallback for testing
    User = None
    PlanType = None
    get_db = None


# Fallback service for when SDK is not available
try:
    from billing.fallback_razorpay_service import fallback_razorpay_service
    FALLBACK_AVAILABLE = True
except ImportError:
    FALLBACK_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedRazorpayService:
    """Enhanced Razorpay service with better configuration handling"""
    
    def __init__(self):
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize Razorpay client with multiple configuration sources"""
        # Try multiple sources for API keys
        self.key_id = self._get_api_key_id()
        self.key_secret = self._get_api_key_secret()
        self.webhook_secret = os.getenv('RAZORPAY_WEBHOOK_SECRET')
        
        # Initialize client
        if not self.key_id or not self.key_secret:
            logger.warning("Razorpay credentials not found in any configuration source")
            self.client = None
            self.status = "credentials_missing"
        elif not RAZORPAY_AVAILABLE:
            logger.warning("Razorpay SDK not available")
            self.client = None
            self.status = "sdk_missing"
        else:
            try:
                self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
                # Test the connection
                self._test_connection()
                logger.info("Razorpay client initialized successfully")
                self.status = "connected"
            except Exception as e:
                logger.error(f"Failed to initialize Razorpay client: {e}")
                self.client = None
                self.status = "connection_failed"
    
    def _get_api_key_id(self) -> Optional[str]:
        """Get API key ID from multiple sources"""
        # Try environment variables first
        key_id = os.getenv('RAZORPAY_KEY_ID')
        if key_id:
            return key_id
        
        # Try Streamlit secrets
        try:
            if hasattr(st, 'secrets') and 'RAZORPAY_KEY_ID' in st.secrets:
                return st.secrets['RAZORPAY_KEY_ID']
        except Exception:
            pass
        
        # Try .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
            return os.getenv('RAZORPAY_KEY_ID')
        except ImportError:
            pass
        
        return None
    
    def _get_api_key_secret(self) -> Optional[str]:
        """Get API key secret from multiple sources"""
        # Try environment variables first
        key_secret = os.getenv('RAZORPAY_KEY_SECRET')
        if key_secret:
            return key_secret
        
        # Try Streamlit secrets
        try:
            if hasattr(st, 'secrets') and 'RAZORPAY_KEY_SECRET' in st.secrets:
                return st.secrets['RAZORPAY_KEY_SECRET']
        except Exception:
            pass
        
        # Try .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
            return os.getenv('RAZORPAY_KEY_SECRET')
        except ImportError:
            pass
        
        return None
    
    def _test_connection(self):
        """Test Razorpay connection"""
        if self.client:
            try:
                # Try to fetch payment methods (lightweight API call)
                self.client.payment.all({'count': 1})
                return True
            except Exception as e:
                logger.warning(f"Razorpay connection test failed: {e}")
                return False
        return False
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get detailed status information for debugging"""
        return {
            'status': self.status,
            'key_id_present': bool(self.key_id),
            'key_secret_present': bool(self.key_secret),
            'sdk_available': RAZORPAY_AVAILABLE,
            'client_initialized': self.client is not None,
            'key_id_preview': self.key_id[:12] + "..." if self.key_id else None
        }
    
    def render_status_debug(self):
        """Render status debug information in Streamlit"""
        status_info = self.get_status_info()
        
        if self.status == "connected":
            st.success("✅ Razorpay payment system is properly configured")
        else:
            st.error("❌ Razorpay payment system configuration issue")
            
            with st.expander("🔧 Debug Information"):
                st.json(status_info)
                
                if self.status == "credentials_missing":
                    st.markdown("""
                    **Fix Required**: Add Razorpay API credentials
                    
                    **For Streamlit Cloud:**
                    1. Go to your app settings
                    2. Add secrets:
                       - `RAZORPAY_KEY_ID` = your key ID
                       - `RAZORPAY_KEY_SECRET` = your key secret
                    
                    **For Local Development:**
                    1. Add to `.env` file:
                       ```
                       RAZORPAY_KEY_ID=your_key_id
                       RAZORPAY_KEY_SECRET=your_key_secret
                       ```
                    """)
                elif self.status == "sdk_missing":
                    st.markdown("""
                    **Fix Required**: Razorpay SDK Missing
                    
                    **For Streamlit Cloud:**
                    1. The `razorpay` package should be in `requirements.txt`
                    2. If still missing, try restarting your app
                    3. Check the app logs for installation errors
                    
                    **For Local Development:**
                    ```bash
                    pip install razorpay>=1.3.0
                    ```
                    
                    **Current Status:**
                    - Requirements.txt includes: `razorpay>=1.3.0`
                    - This should install automatically on Streamlit Cloud
                    - If issue persists, contact Streamlit support
                    """)
    
    def create_payment_link(self, amount: int, description: str, 
                          customer_email: str, plan_type: PlanType) -> Optional[Dict[str, Any]]:
        """Create a payment link with enhanced error handling"""
        if not self.client:
            logger.error(f"Razorpay client not available. Status: {self.status}")
            return None
        
        try:
            payment_link_data = {
                'amount': amount,  # Amount in paisa
                'currency': 'INR',
                'accept_partial': False,
                'description': description,
                'customer': {
                    'email': customer_email
                },
                'notify': {
                    'sms': True,
                    'email': True
                },
                'reminder_enable': True,
                'notes': {
                    'plan_type': plan_type.value,
                    'product': 'resume_analyzer'
                },
                'callback_url': f"{os.getenv('APP_URL', 'https://resume-jd-analyze.streamlit.app')}/payment/success",
                'callback_method': 'get'
            }
            
            payment_link = self.client.payment_link.create(payment_link_data)
            logger.info(f"Created payment link: {payment_link['id']}")
            return payment_link
            
        except Exception as e:
            logger.error(f"Failed to create payment link: {e}")
            return None
    
    def create_customer(self, user: User) -> Optional[Dict[str, Any]]:
        """Create a Razorpay customer with enhanced error handling"""
        if not self.client:
            logger.error(f"Razorpay client not available. Status: {self.status}")
            return None
        
        try:
            customer_data = {
                'name': f"{getattr(user, 'first_name', 'User')} {getattr(user, 'last_name', '')}".strip(),
                'email': user.email,
                'notes': {
                    'user_id': str(user.id),
                    'company': getattr(user, 'company_name', '') or '',
                    'role': getattr(user, 'role', 'user').value if hasattr(getattr(user, 'role', None), 'value') else 'user'
                }
            }
            
            # Add phone if available
            if hasattr(user, 'phone') and user.phone:
                customer_data['contact'] = user.phone
            
            customer = self.client.customer.create(customer_data)
            logger.info(f"Created Razorpay customer: {customer['id']}")
            return customer
            
        except Exception as e:
            logger.error(f"Failed to create Razorpay customer: {e}")
            return None

# Global instance with fallback
enhanced_razorpay_service = EnhancedRazorpayService()

# Use fallback if SDK is not available
if enhanced_razorpay_service.status == 'sdk_missing' and FALLBACK_AVAILABLE:
    enhanced_razorpay_service = fallback_razorpay_service

# Backward compatibility
razorpay_service = enhanced_razorpay_service
