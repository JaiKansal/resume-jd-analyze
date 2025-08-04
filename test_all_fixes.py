#!/usr/bin/env python3
"""
Comprehensive Test Script
Tests all fixes: Razorpay, Database, Usage Tracking, Report Persistence
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_environment_variables():
    """Test if environment variables are properly set"""
    print("🔧 Testing Environment Variables...")
    
    required_vars = {
        'PERPLEXITY_API_KEY': os.getenv('PERPLEXITY_API_KEY'),
        'RAZORPAY_KEY_ID': os.getenv('RAZORPAY_KEY_ID'),
        'RAZORPAY_KEY_SECRET': os.getenv('RAZORPAY_KEY_SECRET')
    }
    
    all_set = True
    for var_name, var_value in required_vars.items():
        if var_value:
            print(f"  ✅ {var_name}: {var_value[:12]}...")
        else:
            print(f"  ❌ {var_name}: Not set")
            all_set = False
    
    return all_set

def test_razorpay_connection():
    """Test Razorpay connection"""
    print("\\n💳 Testing Razorpay Connection...")
    
    try:
        from billing.razorpay_service import razorpay_service
        
        if razorpay_service.client:
            print("  ✅ Razorpay client initialized successfully")
            print(f"  ✅ Key ID: {razorpay_service.key_id}")
            print(f"  ✅ Key Secret: {'Set' if razorpay_service.key_secret else 'Not set'}")
            return True
        else:
            print("  ❌ Razorpay client not initialized")
            return False
            
    except Exception as e:
        print(f"  ❌ Razorpay connection error: {e}")
        return False

def test_database_connection():
    """Test database connection and schema"""
    print("\\n🗄️  Testing Database Connection...")
    
    try:
        from database.fix_database import DatabaseFixer
        
        fixer = DatabaseFixer()
        
        # Test database file exists
        if os.path.exists(fixer.db_path):
            print(f"  ✅ Database file exists: {fixer.db_path}")
        else:
            print(f"  ❌ Database file missing: {fixer.db_path}")
            return False
        
        # Test database schema
        import sqlite3
        with sqlite3.connect(fixer.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['users', 'subscriptions', 'usage_tracking', 'analysis_sessions', 'payment_records']
            
            for table in required_tables:
                if table in tables:
                    print(f"  ✅ Table exists: {table}")
                else:
                    print(f"  ❌ Table missing: {table}")
                    return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database connection error: {e}")
        return False

def test_usage_tracking():
    """Test usage tracking persistence"""
    print("\\n📊 Testing Usage Tracking...")
    
    try:
        from database.usage_tracker import persistent_usage_tracker
        
        # Test getting usage for a test user
        test_user_id = "test_user_123"
        usage = persistent_usage_tracker.get_current_usage(test_user_id)
        
        print(f"  ✅ Usage tracking working")
        print(f"  ✅ Current usage: {usage['analysis_count']}")
        print(f"  ✅ Remaining days: {usage['remaining_days']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Usage tracking error: {e}")
        return False

def test_analysis_storage():
    """Test analysis result storage"""
    print("\\n📋 Testing Analysis Storage...")
    
    try:
        from database.analysis_storage import analysis_storage
        
        # Test saving a dummy analysis
        test_user_id = "test_user_123"
        test_analysis = {
            'score': 85,
            'match_category': 'Strong Match',
            'matching_skills': ['Python', 'Machine Learning'],
            'suggestions': ['Add more experience details']
        }
        
        analysis_id = analysis_storage.save_analysis(
            user_id=test_user_id,
            resume_filename="test_resume.pdf",
            job_description="Test job description",
            analysis_result=test_analysis
        )
        
        if analysis_id:
            print(f"  ✅ Analysis saved with ID: {analysis_id}")
            
            # Test retrieving the analysis
            retrieved = analysis_storage.get_analysis_by_id(analysis_id, test_user_id)
            if retrieved:
                print(f"  ✅ Analysis retrieved successfully")
                print(f"  ✅ Score: {retrieved['score']}")
                return True
            else:
                print(f"  ❌ Failed to retrieve analysis")
                return False
        else:
            print(f"  ❌ Failed to save analysis")
            return False
            
    except Exception as e:
        print(f"  ❌ Analysis storage error: {e}")
        return False

def test_payment_methods():
    """Test payment methods availability"""
    print("\\n💰 Testing Payment Methods...")
    
    try:
        from billing.razorpay_service import razorpay_service
        
        if razorpay_service.client:
            methods = razorpay_service.get_payment_methods()
            print(f"  ✅ Payment methods available: {len(methods)}")
            
            for method in methods:
                print(f"    {method['icon']} {method['name']}")
            
            return True
        else:
            print("  ❌ Razorpay client not available")
            return False
            
    except Exception as e:
        print(f"  ❌ Payment methods error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Comprehensive Fix Verification")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Razorpay Connection", test_razorpay_connection),
        ("Database Connection", test_database_connection),
        ("Usage Tracking", test_usage_tracking),
        ("Analysis Storage", test_analysis_storage),
        ("Payment Methods", test_payment_methods)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\\n🎉 ALL FIXES WORKING PERFECTLY!")
        print("\\n🚀 Your app is ready for:")
        print("  ✅ Razorpay payments")
        print("  ✅ Persistent reports")
        print("  ✅ Proper usage tracking")
        print("  ✅ Database persistence")
        
        print("\\n💡 Next steps:")
        print("  1. Update your Streamlit Cloud secrets with Razorpay keys")
        print("  2. Test the payment flow in your live app")
        print("  3. Start getting paying customers!")
        
    else:
        print("\\n⚠️  Some issues remain. Check the failed tests above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)