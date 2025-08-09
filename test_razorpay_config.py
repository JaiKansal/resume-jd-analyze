#!/usr/bin/env python3
"""
Test Razorpay configuration in Streamlit Cloud
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_razorpay_config():
    """Test Razorpay configuration"""
    logger.info("🧪 Testing Razorpay configuration...")
    
    # Test environment variables
    env_key_id = os.getenv('RAZORPAY_KEY_ID')
    env_key_secret = os.getenv('RAZORPAY_KEY_SECRET')
    
    print(f"Environment variables:")
    print(f"  RAZORPAY_KEY_ID: {'✅ Set' if env_key_id else '❌ Missing'}")
    print(f"  RAZORPAY_KEY_SECRET: {'✅ Set' if env_key_secret else '❌ Missing'}")
    
    # Test Streamlit secrets
    try:
        import streamlit as st
        print(f"\nStreamlit secrets:")
        
        if hasattr(st, 'secrets'):
            secrets_key_id = st.secrets.get('RAZORPAY_KEY_ID')
            secrets_key_secret = st.secrets.get('RAZORPAY_KEY_SECRET')
            
            print(f"  RAZORPAY_KEY_ID: {'✅ Set' if secrets_key_id else '❌ Missing'}")
            print(f"  RAZORPAY_KEY_SECRET: {'✅ Set' if secrets_key_secret else '❌ Missing'}")
            
            # Show available secrets (without values)
            try:
                available_secrets = list(st.secrets.keys())
                print(f"  Available secrets: {available_secrets}")
            except:
                print("  Could not list available secrets")
        else:
            print("  ❌ st.secrets not available")
    except ImportError:
        print("  ❌ Streamlit not available")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test Razorpay SDK
    try:
        import razorpay
        print(f"\nRazorpay SDK: ✅ Available")
    except ImportError:
        print(f"\nRazorpay SDK: ❌ Not installed")
    
    # Test enhanced service
    try:
        from billing.enhanced_razorpay_service import enhanced_razorpay_service
        print(f"\nEnhanced Razorpay Service:")
        print(f"  Status: {enhanced_razorpay_service.status}")
        print(f"  Client initialized: {'✅' if enhanced_razorpay_service.client else '❌'}")
    except Exception as e:
        print(f"\nEnhanced Razorpay Service: ❌ Error - {e}")

if __name__ == "__main__":
    test_razorpay_config()
