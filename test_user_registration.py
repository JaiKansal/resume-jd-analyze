#!/usr/bin/env python3
"""
Test user registration to identify where the issue is
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_user_creation():
    """Test creating a user to see where it fails"""
    print("🧪 Testing User Registration Process")
    print("=" * 50)
    
    try:
        # Import services
        from auth.services import user_service
        from auth.models import UserRole
        
        print("✅ Successfully imported auth services")
        
        # Test data
        test_email = "test_registration@example.com"
        test_password = "TestPassword123!"
        
        print(f"📧 Testing with email: {test_email}")
        
        # Check if user already exists
        existing_user = user_service.get_user_by_email(test_email)
        if existing_user:
            print("⚠️  User already exists, deleting first...")
            # Delete existing user for clean test
            from database.connection import get_db
            db = get_db()
            db.execute_command("DELETE FROM users WHERE email = ?", (test_email,))
            print("✅ Existing user deleted")
        
        # Try to create user
        print("🔄 Creating new user...")
        user = user_service.create_user(
            email=test_email,
            password=test_password,
            first_name="Test",
            last_name="User",
            company_name="Test Company",
            role=UserRole.INDIVIDUAL,
            phone="+1234567890",
            country="United States"
        )
        
        if user:
            print("✅ User created successfully!")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.first_name} {user.last_name}")
            print(f"   Role: {user.role}")
            
            # Verify user was saved to database
            print("🔍 Verifying user in database...")
            saved_user = user_service.get_user_by_email(test_email)
            
            if saved_user:
                print("✅ User successfully saved to database!")
                print(f"   Retrieved ID: {saved_user.id}")
                print(f"   Retrieved Email: {saved_user.email}")
                
                # Test authentication
                print("🔐 Testing authentication...")
                auth_user = user_service.authenticate_user(test_email, test_password)
                
                if auth_user:
                    print("✅ Authentication successful!")
                    return True
                else:
                    print("❌ Authentication failed!")
                    return False
            else:
                print("❌ User not found in database after creation!")
                return False
        else:
            print("❌ User creation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during user creation test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test basic database connection"""
    print("\n🔗 Testing Database Connection")
    print("=" * 30)
    
    try:
        from database.connection import get_db
        db = get_db()
        
        # Test basic query
        result = db.execute_query("SELECT COUNT(*) as count FROM users")
        print(f"✅ Database connection successful")
        print(f"   Current user count: {result[0]['count']}")
        
        # Test table structure
        print("🏗️  Checking table structure...")
        schema = db.execute_query("PRAGMA table_info(users)")
        
        print("   Users table columns:")
        for col in schema:
            print(f"     - {col['name']} ({col['type']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_subscription_creation():
    """Test subscription creation for new users"""
    print("\n💳 Testing Subscription Creation")
    print("=" * 35)
    
    try:
        from auth.services import subscription_service
        from auth.models import PlanType
        
        # Get free plan
        free_plan = subscription_service.get_plan_by_type(PlanType.FREE)
        
        if free_plan:
            print(f"✅ Free plan found: {free_plan.name}")
            print(f"   Plan ID: {free_plan.id}")
            print(f"   Monthly limit: {free_plan.monthly_analysis_limit}")
            return True
        else:
            print("❌ Free plan not found!")
            
            # Check if any plans exist
            all_plans = subscription_service.get_all_plans()
            print(f"   Available plans: {len(all_plans)}")
            
            if not all_plans:
                print("⚠️  No subscription plans found in database!")
                print("   Run: python3 init_subscription_plans.py")
            
            return False
            
    except Exception as e:
        print(f"❌ Subscription test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 COMPREHENSIVE USER REGISTRATION TEST")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Subscription Plans", test_subscription_creation),
        ("User Creation", test_user_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! User registration should work correctly.")
    else:
        print("⚠️  Some tests failed. User registration may have issues.")
        print("\n💡 Recommended fixes:")
        
        for test_name, success in results:
            if not success:
                if test_name == "Database Connection":
                    print("   - Check database file permissions")
                    print("   - Run: python3 database/complete_database_fix.py")
                elif test_name == "Subscription Plans":
                    print("   - Initialize subscription plans")
                    print("   - Run: python3 init_subscription_plans.py")
                elif test_name == "User Creation":
                    print("   - Check auth services and models")
                    print("   - Verify database schema matches models")

if __name__ == "__main__":
    main()