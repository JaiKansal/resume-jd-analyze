"""
App patch to handle Razorpay installation issues
Add this to the top of your app.py file
"""

import streamlit as st
import sys
import importlib

def ensure_payment_system():
    """Ensure payment system is available"""
    try:
        # Try to import the enhanced service
        from billing.enhanced_razorpay_service import enhanced_razorpay_service
        
        # Check if it's working
        status_info = enhanced_razorpay_service.get_status_info()
        
        if status_info['status'] == 'sdk_missing':
            # Try fallback service
            try:
                from billing.fallback_razorpay_service import fallback_razorpay_service
                st.sidebar.info("💡 Using fallback payment system (Direct API)")
                return fallback_razorpay_service
            except ImportError:
                st.sidebar.error("❌ Payment system unavailable")
                return None
        
        return enhanced_razorpay_service
        
    except Exception as e:
        st.sidebar.error(f"❌ Payment system error: {e}")
        return None

# Use this instead of importing enhanced_razorpay_service directly
payment_service = ensure_payment_system()
