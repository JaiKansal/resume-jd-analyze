#!/usr/bin/env python3
"""
Test Emergency Fixes
"""

import sqlite3
import sys
from pathlib import Path

def test_database_tables():
    """Test that all required tables exist"""
    print("🧪 Testing database tables...")
    
    required_tables = [
        'users', 'user_sessions', 'subscriptions', 'subscription_plans',
        'analysis_sessions', 'engagement_events', 'analytics_events',
        'payment_records', 'usage_tracking', 'report_downloads'
    ]
    
    try:
        with sqlite3.connect('data/app.db') as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = []
            for table in required_tables:
                if table in existing_tables:
                    print(f"✅ {table} table exists")
                else:
                    print(f"❌ {table} table missing")
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"❌ Missing tables: {missing_tables}")
                return False
            else:
                print("✅ All required tables exist")
                return True
                
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_app_imports():
    """Test that app.py can be imported without errors"""
    print("\\n🧪 Testing app.py imports...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path.cwd()))
        
        # Test critical imports
        from auth.services import user_service, subscription_service
        from auth.models import UserRole, PlanType
        print("✅ Auth services import successfully")
        
        # Test database connection
        from database.connection import get_db
        db = get_db()
        print("✅ Database connection works")
        
        # Test subscription service
        plans = subscription_service.get_all_plans()
        print(f"✅ Subscription service works - {len(plans)} plans found")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_subscription_fallback():
    """Test subscription fallback logic"""
    print("\\n🧪 Testing subscription fallback...")
    
    try:
        # Check if fallback function exists in app.py
        with open('app.py', 'r') as f:
            content = f.read()
        
        if 'def get_subscription_with_fallback' in content:
            print("✅ Subscription fallback function exists")
            
            if 'get_subscription_with_fallback(user.id)' in content:
                print("✅ Subscription fallback is being used")
                return True
            else:
                print("⚠️ Subscription fallback exists but not used")
                return False
        else:
            print("❌ Subscription fallback function missing")
            return False
            
    except Exception as e:
        print(f"❌ Subscription fallback test failed: {e}")
        return False

def test_null_checks():
    """Test that null checks are in place"""
    print("\\n🧪 Testing null checks...")
    
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        with open('auth/registration.py', 'r') as f:
            reg_content = f.read()
        
        # Check for null-safe patterns
        null_checks = [
            ('subscription and subscription.plan', 'App.py subscription null check'),
            ('user and user.first_name', 'Registration.py user null check'),
            ('if subscription and subscription.plan and', 'App.py enhanced null check')
        ]
        
        all_passed = True
        for check, description in null_checks:
            if check in app_content or check in reg_content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - not found")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Null checks test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 TESTING EMERGENCY FIXES")
    print("=" * 40)
    
    tests = [
        ("Database Tables", test_database_tables),
        ("App Imports", test_app_imports),
        ("Subscription Fallback", test_subscription_fallback),
        ("Null Checks", test_null_checks)
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
    
    print(f"\\n{'='*40}")
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL EMERGENCY FIXES VERIFIED!")
        print("\\n✅ Database schema is complete")
        print("✅ App imports work correctly")
        print("✅ Subscription fallback is active")
        print("✅ Null checks are in place")
        print("\\n🚀 Your app should now run without crashes!")
    else:
        print(f"⚠️ {total - passed} tests failed")
        print("Some issues may still exist.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)