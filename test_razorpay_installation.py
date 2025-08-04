#!/usr/bin/env python3
"""
Test Razorpay Installation
"""

def test_razorpay_import():
    """Test if Razorpay can be imported"""
    print("🧪 Testing Razorpay SDK installation...")
    
    try:
        import razorpay
        print(f"✅ Razorpay SDK imported successfully")
        print(f"✅ Version: {razorpay.__version__ if hasattr(razorpay, '__version__') else 'Unknown'}")
        
        # Test client creation
        try:
            client = razorpay.Client(auth=("test_key", "test_secret"))
            print("✅ Razorpay client can be created")
            return True
        except Exception as e:
            print(f"⚠️ Razorpay client creation failed: {e}")
            print("✅ But SDK is installed correctly")
            return True
            
    except ImportError as e:
        print(f"❌ Razorpay SDK not available: {e}")
        print("\n💡 To fix this:")
        print("1. For local development: pip install razorpay>=1.3.0")
        print("2. For Streamlit Cloud: Add 'razorpay>=1.3.0' to requirements.txt")
        print("3. Restart your Streamlit app")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_enhanced_service():
    """Test the enhanced Razorpay service"""
    print("\n🧪 Testing Enhanced Razorpay Service...")
    
    try:
        from billing.enhanced_razorpay_service import enhanced_razorpay_service
        
        status_info = enhanced_razorpay_service.get_status_info()
        print(f"Status: {status_info['status']}")
        print(f"SDK Available: {status_info['sdk_available']}")
        print(f"Key ID Present: {status_info['key_id_present']}")
        print(f"Key Secret Present: {status_info['key_secret_present']}")
        
        if status_info['status'] == 'connected':
            print("✅ Enhanced Razorpay service is fully functional")
            return True
        elif status_info['status'] == 'sdk_missing':
            print("❌ SDK is missing - this should be fixed by requirements.txt")
            return False
        elif status_info['status'] == 'credentials_missing':
            print("⚠️ SDK available but credentials missing (expected in testing)")
            return True
        else:
            print(f"⚠️ Service status: {status_info['status']}")
            return False
            
    except ImportError as e:
        print(f"❌ Enhanced service not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 RAZORPAY INSTALLATION TEST")
    print("=" * 40)
    
    tests = [
        ("Razorpay Import", test_razorpay_import),
        ("Enhanced Service", test_enhanced_service)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n{'='*40}")
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 RAZORPAY IS PROPERLY INSTALLED!")
        print("\n✅ SDK can be imported")
        print("✅ Enhanced service works")
        print("✅ Payment system should work")
    else:
        print(f"⚠️ {total - passed} tests failed")
        print("\n💡 Next steps:")
        print("1. Check that 'razorpay>=1.3.0' is in requirements.txt")
        print("2. Restart your Streamlit Cloud app")
        print("3. Check app logs for installation errors")
    
    return passed == total

if __name__ == "__main__":
    main()