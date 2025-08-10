#!/usr/bin/env python3
"""
Complete Razorpay fix for Streamlit Cloud deployment
Ensures payment system works properly without SDK issues
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_requirements():
    """Ensure razorpay is properly specified in requirements.txt"""
    logger.info("📦 Updating requirements.txt for Razorpay...")
    
    with open('requirements.txt', 'r') as f:
        lines = f.readlines()
    
    # Check if razorpay is already there
    has_razorpay = any('razorpay' in line.lower() for line in lines)
    
    if not has_razorpay:
        # Add razorpay
        lines.append('razorpay>=1.3.0\n')
        logger.info("Added razorpay>=1.3.0 to requirements.txt")
    else:
        logger.info("razorpay already in requirements.txt")
    
    # Write back
    with open('requirements.txt', 'w') as f:
        f.writelines(lines)
    
    logger.info("✅ Requirements.txt updated")

def create_streamlit_secrets_template():
    """Create a template for Streamlit secrets"""
    logger.info("🔐 Creating Streamlit secrets template...")
    
    secrets_template = """# Streamlit Cloud Secrets Template
# Add these to your Streamlit Cloud app settings

[secrets]
DATABASE_URL = "your_postgresql_database_url"
RAZORPAY_KEY_ID = "rzp_live_your_key_id_here"
RAZORPAY_KEY_SECRET = "your_razorpay_key_secret_here"

# Optional
RAZORPAY_WEBHOOK_SECRET = "your_webhook_secret_here"
"""
    
    with open('.streamlit/secrets_template.toml', 'w') as f:
        f.write(secrets_template)
    
    logger.info("✅ Created .streamlit/secrets_template.toml")

def test_razorpay_import():
    """Test if Razorpay can be imported"""
    logger.info("🧪 Testing Razorpay import...")
    
    try:
        import razorpay
        logger.info("✅ Razorpay SDK can be imported")
        return True
    except ImportError as e:
        logger.error(f"❌ Razorpay SDK import failed: {e}")
        return False

def test_fallback_service():
    """Test if fallback service works"""
    logger.info("🧪 Testing fallback Razorpay service...")
    
    try:
        from billing.fallback_razorpay_service import fallback_razorpay_service
        status = fallback_razorpay_service.get_status_info()
        logger.info(f"✅ Fallback service available - Status: {status['status']}")
        return True
    except Exception as e:
        logger.error(f"❌ Fallback service failed: {e}")
        return False

def create_payment_test_script():
    """Create a script to test payment functionality"""
    logger.info("🧪 Creating payment test script...")
    
    test_script = '''#!/usr/bin/env python3
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
    print("\\n1. Testing Razorpay SDK import...")
    try:
        import razorpay
        print("✅ Razorpay SDK imported successfully")
        sdk_available = True
    except ImportError as e:
        print(f"❌ Razorpay SDK import failed: {e}")
        sdk_available = False
    
    # Test 2: Fallback Service
    print("\\n2. Testing fallback service...")
    try:
        from billing.fallback_razorpay_service import fallback_razorpay_service
        status = fallback_razorpay_service.get_status_info()
        print(f"✅ Fallback service available - Status: {status['status']}")
        fallback_available = True
    except Exception as e:
        print(f"❌ Fallback service failed: {e}")
        fallback_available = False
    
    # Test 3: Enhanced Service
    print("\\n3. Testing enhanced service...")
    try:
        from billing.enhanced_razorpay_service import enhanced_razorpay_service
        status = enhanced_razorpay_service.get_status_info()
        print(f"✅ Enhanced service available - Status: {status['status']}")
        enhanced_available = True
    except Exception as e:
        print(f"❌ Enhanced service failed: {e}")
        enhanced_available = False
    
    # Test 4: App Import
    print("\\n4. Testing app.py import...")
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
    print("\\n📊 Test Summary:")
    print(f"SDK Available: {'✅' if sdk_available else '❌'}")
    print(f"Fallback Available: {'✅' if fallback_available else '❌'}")
    print(f"Enhanced Available: {'✅' if enhanced_available else '❌'}")
    print(f"App Service Available: {'✅' if app_service_available else '❌'}")
    
    if app_service_available:
        print("\\n🎉 Payment system should work in Streamlit Cloud!")
    else:
        print("\\n❌ Payment system needs fixing!")
    
    return app_service_available

if __name__ == "__main__":
    success = test_payment_services()
    sys.exit(0 if success else 1)
'''
    
    with open('test_payment_system.py', 'w') as f:
        f.write(test_script)
    
    os.chmod('test_payment_system.py', 0o755)
    logger.info("✅ Created test_payment_system.py")

def main():
    """Run all fixes"""
    logger.info("🚀 Starting Razorpay Streamlit Cloud fixes...")
    
    try:
        update_requirements()
        create_streamlit_secrets_template()
        create_payment_test_script()
        
        # Test current setup
        sdk_works = test_razorpay_import()
        fallback_works = test_fallback_service()
        
        logger.info("\\n🎉 Razorpay fixes completed!")
        logger.info("\\n📋 What was done:")
        logger.info("1. ✅ Updated requirements.txt")
        logger.info("2. ✅ Created secrets template")
        logger.info("3. ✅ Created payment test script")
        logger.info("4. ✅ Tested current setup")
        
        logger.info("\\n📊 Current Status:")
        logger.info(f"SDK Import: {'✅' if sdk_works else '❌'}")
        logger.info(f"Fallback Service: {'✅' if fallback_works else '❌'}")
        
        if fallback_works:
            logger.info("\\n🚀 Payment system should work on Streamlit Cloud!")
            logger.info("💡 The fallback service uses direct API calls and doesn't need the SDK")
        else:
            logger.warning("\\n⚠️ Payment system may have issues")
        
        logger.info("\\n🧪 Run 'python3 test_payment_system.py' to test everything")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Fix failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)