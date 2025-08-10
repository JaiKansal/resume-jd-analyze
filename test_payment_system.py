#!/usr/bin/env python3
"""
Test Razorpay payment functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_payment_services():
    """Test all payment services"""
    print("🧪 Testing Razorpay payment services...")
    
    # Test 1: SDK Import
    print("\n1. Testing Razorpay SDK import...")
    try:
        import razorpay
        print("✅ Razorpay SDK imported successfully")
        sdk_available = True
    except ImportError as e:
        print(f"❌ Razorpay SDK import failed: {e}")
        sdk_available = False
    
    # Test 2: Fallback Service
    print("\n2. Testing fallback service...")
    try:
        from billing.fallback_razorpay_service import fallback_razorpay_service
        status = fallback_razorpay_service.get_status_info()
        print(f"✅ Fallback service available - Status: {status['status']}")
        fallback_available = True
    except Exception as e:
        print(f"❌ Fallback service failed: {e}")
        fallback_available = False
    
    # Test 3: Enhanced Service
    print("\n3. Testing enhanced service...")
    try:
        from billing.enhanced_razorpay_service import enhanced_razorpay_service
        status = enhanced_razorpay_service.get_status_info()
        print(f"✅ Enhanced service available - Status: {status['status']}")
        enhanced_available = True
    except Exception as e:
        print(f"❌ Enhanced service failed: {e}")
        enhanced_available = False
    
    # Test 4: App Import
    print("\n4. Testing app.py import...")
    try:
        # This simulates what app.py does
        enhanced_razorpay_service = None
        
        # Try fallback first
        if fallback_available:
            from billing.fallback_razorpay_service import fallback_razorpay_service
            enhanced_razorpay_service = fallback_razorpay_service
            print("✅ App would use fallback service")
        elif enhanced_available:
            from billing.enhanced_razorpay_service import enhanced_razorpay_service
            print("✅ App would use enhanced service")
        else:
            print("❌ App would have no payment service")
            
        app_service_available = enhanced_razorpay_service is not None
    except Exception as e:
        print(f"❌ App import simulation failed: {e}")
        app_service_available = False
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"SDK Available: {'✅' if sdk_available else '❌'}")
    print(f"Fallback Available: {'✅' if fallback_available else '❌'}")
    print(f"Enhanced Available: {'✅' if enhanced_available else '❌'}")
    print(f"App Service Available: {'✅' if app_service_available else '❌'}")
    
    if app_service_available:
        print("\n🎉 Payment system should work in Streamlit Cloud!")
    else:
        print("\n❌ Payment system needs fixing!")
    
    return app_service_available

if __name__ == "__main__":
    success = test_payment_services()
    sys.exit(0 if success else 1)
