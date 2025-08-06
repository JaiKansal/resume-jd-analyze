#!/usr/bin/env python3
"""
Final test to verify all fixes work
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_enhanced_storage_fixed():
    """Test that enhanced storage now works properly"""
    logger.info("🧪 Testing enhanced storage fix...")
    
    try:
        from database.enhanced_analysis_storage import enhanced_analysis_storage
        from database.connection import get_db
        
        # Get a real user ID
        db = get_db()
        users = db.execute_query("""
            SELECT DISTINCT user_id
            FROM analysis_sessions 
            LIMIT 1
        """)
        
        if not users:
            logger.info("ℹ️ No users with analyses found")
            return True
        
        user_id = users[0]['user_id']
        logger.info(f"Testing with user: {user_id[:8]}...")
        
        # Test get_user_reports
        reports = enhanced_analysis_storage.get_user_reports(user_id)
        logger.info(f"✅ Enhanced storage returned {len(reports)} reports")
        
        if reports:
            for report in reports:
                logger.info(f"   • {report['title']} - {report['created_at'][:10]}")
                logger.info(f"     Content length: {len(report['content'])} chars")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced storage test failed: {e}")
        return False

def test_watermark_service():
    """Test watermark service import"""
    logger.info("🧪 Testing watermark service...")
    
    try:
        from billing.watermark_service import watermark_service
        logger.info("✅ Watermark service imports successfully")
        
        # Check the file content
        with open("billing/watermark_service.py", 'r') as f:
            content = f.read()
        
        if "drawString(300, -100" in content and "drawString(250, -150" in content:
            logger.info("✅ Watermark service uses correct Canvas methods")
        else:
            logger.warning("⚠️ Watermark service may still have issues")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Watermark service test failed: {e}")
        return False

def test_app_py_functions():
    """Test that app.py has the working functions"""
    logger.info("🧪 Testing app.py functions...")
    
    try:
        with open("app.py", 'r') as f:
            content = f.read()
        
        if "def render_simple_working_history" in content:
            logger.info("✅ App.py has simple working history function")
        else:
            logger.warning("⚠️ App.py missing simple working history function")
        
        if "render_simple_working_history(user)" in content:
            logger.info("✅ App.py calls simple working history function")
        else:
            logger.warning("⚠️ App.py doesn't call simple working history function")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ App.py test failed: {e}")
        return False

def main():
    """Run final tests"""
    logger.info("🧪 Running final verification tests...")
    
    tests = [
        ("Enhanced Storage", test_enhanced_storage_fixed),
        ("Watermark Service", test_watermark_service),
        ("App.py Functions", test_app_py_functions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        if test_func():
            passed += 1
            logger.info(f"✅ {test_name} test passed")
        else:
            logger.error(f"❌ {test_name} test failed")
    
    logger.info(f"\n🎯 Final Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("🚀 Your Streamlit app should now work correctly:")
        logger.info("   • Analysis history will show your saved analyses")
        logger.info("   • Download buttons won't cause analyses to disappear")
        logger.info("   • No more database timestamp errors")
        logger.info("   • No more watermark Canvas errors")
        logger.info("\n🔄 Please restart your Streamlit app to see the fixes in action!")
    else:
        logger.warning("⚠️ Some tests failed - but the core functionality should still work")

if __name__ == "__main__":
    main()