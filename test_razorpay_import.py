#!/usr/bin/env python3
"""
Test Razorpay import and installation
"""

print("🔍 Testing Razorpay import...")

try:
    import razorpay
    print("✅ Razorpay SDK imported successfully")
    print(f"Version: {razorpay.__version__ if hasattr(razorpay, '__version__') else 'Unknown'}")
    
    # Test client creation
    try:
        client = razorpay.Client(auth=("test_key", "test_secret"))
        print("✅ Razorpay client can be created")
    except Exception as e:
        print(f"⚠️ Client creation issue: {e}")
        
except ImportError as e:
    print(f"❌ Razorpay SDK import failed: {e}")
    print("💡 This means the package is not installed or not available")

print("\n🔍 Checking fallback service...")
try:
    from billing.fallback_razorpay_service import fallback_razorpay_service
    status = fallback_razorpay_service.get_status_info()
    print("✅ Fallback service available")
    print(f"Status: {status}")
except Exception as e:
    print(f"❌ Fallback service issue: {e}")

print("\n📦 Checking requirements.txt...")
try:
    with open('requirements.txt', 'r') as f:
        content = f.read()
        if 'razorpay' in content:
            print("✅ razorpay found in requirements.txt")
            for line in content.split('\n'):
                if 'razorpay' in line.lower():
                    print(f"   {line}")
        else:
            print("❌ razorpay not found in requirements.txt")
except Exception as e:
    print(f"❌ Could not read requirements.txt: {e}")