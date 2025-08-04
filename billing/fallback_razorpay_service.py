"""
Fallback Payment Service - Works without Razorpay SDK using direct API calls
"""

import requests
import json
import base64
import hmac
import hashlib
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    # Mock streamlit for testing
    import types
    st = types.ModuleType('streamlit')
    st.secrets = {}
    st.success = lambda x: print(f"SUCCESS: {x}")
    st.error = lambda x: print(f"ERROR: {x}")
    st.info = lambda x: print(f"INFO: {x}")
    st.warning = lambda x: print(f"WARNING: {x}")
    st.markdown = lambda x: print(f"MARKDOWN: {x}")
    st.json = lambda x: print(f"JSON: {x}")
    st.expander = lambda x: types.SimpleNamespace(__enter__=lambda: None, __exit__=lambda *args: None)
    STREAMLIT_AVAILABLE = False
from typing import Dict, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)

class FallbackRazorpayService:
    """Fallback Razorpay service using direct API calls"""
    
    def __init__(self):
        self.key_id = self._get_key_id()
        self.key_secret = self._get_key_secret()
        self.base_url = "https://api.razorpay.com/v1"
        
        # Check if we have credentials
        if self.key_id and self.key_secret:
            self.status = "connected"
            self.client_available = True
        else:
            self.status = "credentials_missing"
            self.client_available = False
    
    def _get_key_id(self):
        """Get API key ID from multiple sources"""
        # Try environment variables
        key_id = os.getenv('RAZORPAY_KEY_ID')
        if key_id:
            return key_id
        
        # Try Streamlit secrets
        try:
            if hasattr(st, 'secrets') and 'RAZORPAY_KEY_ID' in st.secrets:
                return st.secrets['RAZORPAY_KEY_ID']
        except:
            pass
        
        return None
    
    def _get_key_secret(self):
        """Get API key secret from multiple sources"""
        # Try environment variables
        key_secret = os.getenv('RAZORPAY_KEY_SECRET')
        if key_secret:
            return key_secret
        
        # Try Streamlit secrets
        try:
            if hasattr(st, 'secrets') and 'RAZORPAY_KEY_SECRET' in st.secrets:
                return st.secrets['RAZORPAY_KEY_SECRET']
        except:
            pass
        
        return None
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Make authenticated request to Razorpay API"""
        if not self.key_id or not self.key_secret:
            return None
        
        url = f"{self.base_url}/{endpoint}"
        
        # Create basic auth header
        auth_string = f"{self.key_id}:{self.key_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Razorpay API request failed: {e}")
            return None
    
    def create_payment_link(self, amount: int, description: str, 
                          customer_email: str, plan_type: str) -> Optional[Dict[str, Any]]:
        """Create payment link using direct API call"""
        if not self.client_available:
            return None
        
        data = {
            'amount': amount,
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
                'plan_type': plan_type,
                'product': 'resume_analyzer'
            },
            'callback_url': f"{os.getenv('APP_URL', 'https://resume-jd-analyze.streamlit.app')}/payment/success",
            'callback_method': 'get'
        }
        
        result = self._make_request('POST', 'payment_links', data)
        if result:
            logger.info(f"Created payment link: {result.get('id')}")
        
        return result
    
    def create_customer(self, user_email: str, user_name: str = None) -> Optional[Dict[str, Any]]:
        """Create customer using direct API call"""
        if not self.client_available:
            return None
        
        data = {
            'email': user_email,
            'name': user_name or 'Customer'
        }
        
        result = self._make_request('POST', 'customers', data)
        if result:
            logger.info(f"Created customer: {result.get('id')}")
        
        return result
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get status information"""
        return {
            'status': self.status,
            'key_id_present': bool(self.key_id),
            'key_secret_present': bool(self.key_secret),
            'sdk_available': False,  # We're not using SDK
            'api_available': self.client_available,
            'client_initialized': self.client_available,
            'key_id_preview': self.key_id[:12] + "..." if self.key_id else None,
            'fallback_mode': True
        }
    
    def render_status_debug(self):
        """Render status debug information"""
        status_info = self.get_status_info()
        
        if self.status == "connected":
            st.success("✅ Razorpay payment system is working (Fallback Mode)")
            st.info("💡 Using direct API calls instead of SDK")
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
                       - `RAZORPAY_KEY_ID` = rzp_live_gBOm5l3scvXYjP
                       - `RAZORPAY_KEY_SECRET` = your_secret_key
                    """)

# Global fallback instance
fallback_razorpay_service = FallbackRazorpayService()
