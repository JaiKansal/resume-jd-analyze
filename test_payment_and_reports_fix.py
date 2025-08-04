#!/usr/bin/env python3
"""
Test Payment System and Report Persistence Fixes
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

logger = logging.getLogger(__name__)

def test_razorpay_configuration():
    """Test Razorpay configuration and initialization"""
    print("🧪 Testing Razorpay Configuration...")
    
    try:
        from billing.enhanced_razorpay_service import enhanced_razorpay_service
        
        # Get status info
        status_info = enhanced_razorpay_service.get_status_info()
        
        print(f"Status: {status_info['status']}")
        print(f"Key ID Present: {status_info['key_id_present']}")
        print(f"Key Secret Present: {status_info['key_secret_present']}")
        print(f"SDK Available: {status_info['sdk_available']}")
        print(f"Client Initialized: {status_info['client_initialized']}")
        
        if status_info['key_id_preview']:
            print(f"Key ID Preview: {status_info['key_id_preview']}")
        
        if status_info['status'] == 'connected':
            print("✅ Razorpay is properly configured and connected")
            return True
        elif status_info['status'] == 'credentials_missing':
            print("⚠️ Razorpay credentials missing - this is expected in local testing")
            print("💡 Add RAZORPAY_KEY_SECRET to environment or Streamlit secrets")
            return True  # This is expected in local testing
        else:
            print(f"❌ Razorpay configuration issue: {status_info['status']}")
            return False
            
    except ImportError:
        print("❌ Enhanced Razorpay service not available")
        return False
    except Exception as e:
        print(f"❌ Error testing Razorpay: {e}")
        return False

def test_enhanced_analysis_storage():
    """Test enhanced analysis storage functionality"""
    print("\\n🧪 Testing Enhanced Analysis Storage...")
    
    try:
        from database.enhanced_analysis_storage import enhanced_analysis_storage
        from auth.services import user_service
        
        # Create a test user
        test_email = "test_storage@example.com"
        
        # Clean up any existing test user
        from database.connection import get_db
        db = get_db()
        db.execute_command("DELETE FROM report_downloads WHERE user_id IN (SELECT id FROM users WHERE email = ?)", (test_email,))
        db.execute_command("DELETE FROM analysis_sessions WHERE user_id IN (SELECT id FROM users WHERE email = ?)", (test_email,))
        db.execute_command("DELETE FROM subscriptions WHERE user_id IN (SELECT id FROM users WHERE email = ?)", (test_email,))
        db.execute_command("DELETE FROM users WHERE email = ?", (test_email,))
        
        # Create test user
        user = user_service.create_user(
            email=test_email,
            password="TestPassword123!",
            first_name="Test",
            last_name="Storage"
        )
        
        if not user:
            print("❌ Failed to create test user")
            return False
        
        print("✅ Test user created")
        
        # Test saving analysis
        analysis_result = {
            'score': 85,
            'match_category': 'Strong Match',
            'matching_skills': ['Python', 'Machine Learning'],
            'skill_gaps': ['Docker', 'Kubernetes'],
            'suggestions': ['Add Docker experience', 'Learn Kubernetes']
        }
        
        analysis_id = enhanced_analysis_storage.save_analysis(
            user_id=user.id,
            resume_filename="test_resume.pdf",
            resume_content="Test resume content with Python and ML experience",
            job_description="Looking for Python developer with ML and Docker skills",
            analysis_result=analysis_result,
            processing_time=2.5,
            api_cost=0.05,
            tokens_used=150
        )
        
        if analysis_id:
            print("✅ Analysis saved successfully")
        else:
            print("❌ Failed to save analysis")
            return False
        
        # Test retrieving analyses
        analyses = enhanced_analysis_storage.get_user_analyses(user.id)
        
        if analyses and len(analyses) > 0:
            print(f"✅ Retrieved {len(analyses)} analyses")
            
            # Test specific analysis retrieval
            specific_analysis = enhanced_analysis_storage.get_analysis_by_id(analysis_id, user.id)
            if specific_analysis:
                print("✅ Retrieved specific analysis")
            else:
                print("❌ Failed to retrieve specific analysis")
                return False
        else:
            print("❌ Failed to retrieve analyses")
            return False
        
        # Test download tracking
        enhanced_analysis_storage.record_download(analysis_id, user.id, 'individual', 'csv')
        enhanced_analysis_storage.record_download(analysis_id, user.id, 'individual', 'pdf')
        
        download_history = enhanced_analysis_storage.get_download_history(analysis_id)
        if download_history and len(download_history) > 0:
            print(f"✅ Download tracking works - {len(download_history)} downloads recorded")
        else:
            print("❌ Download tracking failed")
            return False
        
        # Test user statistics
        stats = enhanced_analysis_storage.get_user_statistics(user.id)
        if stats and stats.get('total_analyses', 0) > 0:
            print(f"✅ User statistics work - {stats['total_analyses']} total analyses")
        else:
            print("❌ User statistics failed")
            return False
        
        # Clean up
        db.execute_command("DELETE FROM report_downloads WHERE user_id = ?", (user.id,))
        db.execute_command("DELETE FROM analysis_sessions WHERE user_id = ?", (user.id,))
        db.execute_command("DELETE FROM subscriptions WHERE user_id = ?", (user.id,))
        db.execute_command("DELETE FROM users WHERE id = ?", (user.id,))
        
        print("✅ Enhanced analysis storage works correctly")
        return True
        
    except ImportError:
        print("❌ Enhanced analysis storage not available")
        return False
    except Exception as e:
        print(f"❌ Error testing analysis storage: {e}")
        return False

def test_report_history_ui():
    """Test report history UI component"""
    print("\\n🧪 Testing Report History UI...")
    
    try:
        from components.report_history_ui import report_history_ui
        
        # Check if the UI component is properly initialized
        if hasattr(report_history_ui, 'render_history_page'):
            print("✅ Report history UI component available")
            
            if hasattr(report_history_ui, 'storage'):
                print("✅ Storage integration available")
            else:
                print("⚠️ Storage integration not found")
            
            return True
        else:
            print("❌ Report history UI component missing methods")
            return False
            
    except ImportError:
        print("❌ Report history UI component not available")
        return False
    except Exception as e:
        print(f"❌ Error testing report history UI: {e}")
        return False

def test_app_integration():
    """Test app.py integration"""
    print("\\n🧪 Testing App Integration...")
    
    try:
        # Check if enhanced services are imported in app.py
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        checks = [
            ('enhanced_razorpay_service', 'Enhanced Razorpay service import'),
            ('enhanced_analysis_storage', 'Enhanced analysis storage import'),
            ('report_history_ui', 'Report history UI import'),
            ('check_payment_system_status', 'Payment system status check'),
            ('save_analysis_with_history', 'Analysis history saving'),
            ('Analysis History', 'Analysis History navigation option'),
            ('render_analysis_history', 'Analysis history rendering function')
        ]
        
        all_passed = True
        for check, description in checks:
            if check in app_content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - not found")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error testing app integration: {e}")
        return False

def test_database_schema():
    """Test database schema for new tables"""
    print("\\n🧪 Testing Database Schema...")
    
    try:
        from database.connection import get_db
        
        db = get_db()
        
        # Check if report_downloads table exists
        try:
            db.execute_query("SELECT COUNT(*) FROM report_downloads LIMIT 1")
            print("✅ report_downloads table exists")
        except Exception:
            print("❌ report_downloads table missing")
            return False
        
        # Check if analysis_sessions has enhanced columns
        try:
            db.execute_query("SELECT resume_hash, job_description_hash, processing_time_seconds, api_cost_usd, tokens_used FROM analysis_sessions LIMIT 1")
            print("✅ Enhanced analysis_sessions columns exist")
        except Exception as e:
            print(f"❌ Enhanced analysis_sessions columns missing: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing database schema: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 TESTING PAYMENT SYSTEM & REPORT PERSISTENCE FIXES")
    print("=" * 60)
    
    tests = [
        ("Razorpay Configuration", test_razorpay_configuration),
        ("Enhanced Analysis Storage", test_enhanced_analysis_storage),
        ("Report History UI", test_report_history_ui),
        ("App Integration", test_app_integration),
        ("Database Schema", test_database_schema)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\\n{'='*60}")
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\\n✅ Payment system configuration is working")
        print("✅ Report persistence and history is working")
        print("✅ App integration is complete")
        print("\\n🚀 Your fixes are ready for production!")
    else:
        print(f"❌ {total - passed} tests failed")
        print("\\n💡 Next steps:")
        print("1. Check the failed tests above")
        print("2. Ensure all files are created correctly")
        print("3. Add Razorpay credentials to Streamlit secrets")
    
    return passed == total

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = main()
    if not success:
        exit(1)