#!/usr/bin/env python3
"""
Debug Razorpay secrets configuration in Streamlit Cloud
"""

import os
import logging
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_razorpay_configuration():
    """Debug Razorpay configuration step by step"""
    
    st.title("🔍 Razorpay Configuration Debug")
    
    # Check environment variables
    st.subheader("1. Environment Variables")
    env_key_id = os.getenv('RAZORPAY_KEY_ID')
    env_key_secret = os.getenv('RAZORPAY_KEY_SECRET')
    
    st.write(f"**RAZORPAY_KEY_ID (env):** {'✅ Found' if env_key_id else '❌ Missing'}")
    st.write(f"**RAZORPAY_KEY_SECRET (env):** {'✅ Found' if env_key_secret else '❌ Missing'}")
    
    if env_key_id:
        st.write(f"**Key ID Preview:** {env_key_id[:12]}...")
    
    # Check Streamlit secrets
    st.subheader("2. Streamlit Secrets")
    try:
        if hasattr(st, 'secrets'):
            secrets_key_id = st.secrets.get('RAZORPAY_KEY_ID')
            secrets_key_secret = st.secrets.get('RAZORPAY_KEY_SECRET')
            
            st.write(f"**RAZORPAY_KEY_ID (secrets):** {'✅ Found' if secrets_key_id else '❌ Missing'}")
            st.write(f"**RAZORPAY_KEY_SECRET (secrets):** {'✅ Found' if secrets_key_secret else '❌ Missing'}")
            
            if secrets_key_id:
                st.write(f"**Key ID Preview:** {secrets_key_id[:12]}...")
            
            # Show available secrets
            try:
                available_secrets = list(st.secrets.keys())
                st.write(f"**Available secrets:** {available_secrets}")
            except:
                st.write("**Available secrets:** Could not list")
        else:
            st.error("❌ st.secrets not available")
    except Exception as e:
        st.error(f"❌ Error accessing secrets: {e}")
    
    # Check Razorpay SDK
    st.subheader("3. Razorpay SDK")
    try:
        import razorpay
        st.success("✅ Razorpay SDK available")
    except ImportError:
        st.error("❌ Razorpay SDK not installed")
    
    # Test enhanced service
    st.subheader("4. Enhanced Razorpay Service")
    try:
        from billing.enhanced_razorpay_service import enhanced_razorpay_service
        
        status_info = enhanced_razorpay_service.get_status_info()
        
        st.write(f"**Status:** {status_info['status']}")
        st.write(f"**Key ID Present:** {'✅' if status_info['key_id_present'] else '❌'}")
        st.write(f"**Key Secret Present:** {'✅' if status_info['key_secret_present'] else '❌'}")
        st.write(f"**SDK Available:** {'✅' if status_info['sdk_available'] else '❌'}")
        st.write(f"**Client Initialized:** {'✅' if status_info['client_initialized'] else '❌'}")
        
        if status_info['key_id_preview']:
            st.write(f"**Key ID Preview:** {status_info['key_id_preview']}")
        
        # Try to reinitialize
        if st.button("🔄 Reinitialize Razorpay Service"):
            with st.spinner("Reinitializing..."):
                success = enhanced_razorpay_service.reinitialize()
                if success:
                    st.success("✅ Reinitalization successful!")
                else:
                    st.error("❌ Reinitalization failed")
                st.rerun()
                
    except Exception as e:
        st.error(f"❌ Error with enhanced service: {e}")
    
    # Test payment service selection
    st.subheader("5. Payment Service Selection")
    try:
        from billing.payment_fallback import get_payment_service
        
        payment_service = get_payment_service()
        service_type = type(payment_service).__name__
        
        st.write(f"**Selected Service:** {service_type}")
        
        if hasattr(payment_service, 'status'):
            st.write(f"**Service Status:** {payment_service.status}")
        
        if service_type == "EnhancedRazorpayService":
            st.success("✅ Razorpay service is being used!")
        else:
            st.warning("⚠️ Fallback service is being used")
            
    except Exception as e:
        st.error(f"❌ Error testing payment service: {e}")

if __name__ == "__main__":
    debug_razorpay_configuration()