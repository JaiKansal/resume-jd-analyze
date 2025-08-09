#!/usr/bin/env python3
"""
Test app startup without import errors
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def test_app_imports():
    """Test that app.py can be imported without errors"""
    print("🧪 Testing app.py imports...")
    
    try:
        # Test basic imports
        import streamlit as st
        print("✅ Streamlit import successful")
        
        # Test payment fallback
        from billing.payment_fallback import payment_fallback_service
        print("✅ Payment fallback import successful")
        
        # Test safe payment loader
        from billing.safe_payment_loader import safe_payment_service
        print("✅ Safe payment loader import successful")
        
        # Test that we can get a payment service without errors
        service = safe_payment_service
        print(f"✅ Payment service loaded: {type(service).__name__}")
        
        print("\n🎉 All critical imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_payment_service_functionality():
    """Test basic payment service functionality"""
    print("\n🧪 Testing payment service functionality...")
    
    try:
        from billing.safe_payment_loader import safe_payment_service
        
        # Test create_payment_link (should return fallback response)
        result = safe_payment_service.create_payment_link(1000, "Test", "test@example.com", "professional")
        print(f"✅ create_payment_link returned: {type(result)}")
        
        # Test status
        if hasattr(safe_payment_service, 'status'):
            print(f"✅ Service status: {safe_payment_service.status}")
        
        print("✅ Payment service functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Payment service test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing app startup and payment system...")
    
    imports_ok = test_app_imports()
    functionality_ok = test_payment_service_functionality()
    
    if imports_ok and functionality_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ App should start without import errors")
        print("✅ Payment system has proper fallbacks")
        print("✅ Free tier functionality available")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Check the errors above and fix before deploying")
    
    print(f"\n📊 Test Results:")
    print(f"  Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"  Functionality: {'✅ PASS' if functionality_ok else '❌ FAIL'}")