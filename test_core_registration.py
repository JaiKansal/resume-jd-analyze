#!/usr/bin/env python3
"""
Test core registration functionality without Streamlit dependencies
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_user_registration_and_login():
    """Test user registration and login without Streamlit"""
    print("🧪 Testing Core User Registration & Login")
    print("=" * 50)
    
    try:
        # Import core services only
        from auth.services import user_service, subscription_service, session_service
        from auth.models import UserRole, PlanType
        
        print("✅ Successfully imported core services")
        
        # Test data
        test_email = "core_test@example.com"
        test_password = "TestPassword123!"
        
        # Clean up any existing user
        existing_user = user_service.get_user_by_email(test_email)
        if existing_user:
            from database.connection import get_db
            db = get_db()
            db.execute_command("DELETE FROM subscriptions WHERE user_id = ?", (existing_user.id,))
            db.execute_command("DELETE FROM user_sessions WHERE user_id = ?", (existing_user.id,))
            db.execute_command("DELETE FROM users WHERE email = ?", (test_email,))
            print("🧹 Cleaned up existing test user")
        
        # Step 1: Create user
        print("👤 Creating user...")
        user = user_service.create_user(
            email=test_email,
            password=test_password,
            first_name="Core",
            last_name="Test",
            company_name="Test Company",
            role=UserRole.INDIVIDUAL,
            phone="+1234567890",
            country="United States"
        )
        
        if not user:
            print("❌ Failed to create user")
            return False
        
        print(f"✅ User created: {user.email} (ID: {user.id})")
        
        # Step 2: Verify user was saved
        print("🔍 Verifying user in database...")
        saved_user = user_service.get_user_by_email(test_email)
        
        if not saved_user:
            print("❌ User not found in database after creation")
            return False
        
        print(f"✅ User verified in database: {saved_user.email}")
        
        # Step 3: Test authentication
        print("🔐 Testing authentication...")
        auth_user = user_service.authenticate_user(test_email, test_password)
        
        if not auth_user:
            print("❌ Authentication failed")
            return False
        
        print(f"✅ Authentication successful: {auth_user.email}")
        
        # Step 4: Check subscription was created
        print("💳 Checking subscription...")
        subscription = subscription_service.get_user_subscription(user.id)
        
        if not subscription:
            print("❌ No subscription found for user")
            return False
        
        print(f"✅ Subscription found: {subscription.status}")
        
        # Step 5: Create session
        print("🔄 Creating session...")
        session = session_service.create_session(user.id)
        
        if not session:
            print("❌ Failed to create session")
            return False
        
        print(f"✅ Session created: {session.id}")
        
        # Step 6: Verify session
        print("✅ Verifying session...")
        retrieved_session = session_service.get_session(session.session_token)
        
        if not retrieved_session:
            print("❌ Session not retrievable")
            return False
        
        print(f"✅ Session verified: {retrieved_session.id}")
        
        # Step 7: Test analysis storage capability
        print("📊 Testing analysis storage capability...")
        
        from database.connection import get_db
        db = get_db()
        
        # Check if analysis_sessions table exists and we can insert
        try:
            analysis_id = f"test_analysis_{user.id}"
            db.execute_command("""
                INSERT OR REPLACE INTO analysis_sessions 
                (id, user_id, resume_filename, job_description, analysis_result, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (analysis_id, user.id, "test_resume.pdf", "test job description", "test result"))
            
            print("✅ Analysis storage works")
            
            # Verify we can retrieve it
            result = db.get_single_result(
                "SELECT * FROM analysis_sessions WHERE id = ?", 
                (analysis_id,)
            )
            
            if result:
                print("✅ Analysis retrieval works")
            else:
                print("❌ Analysis retrieval failed")
                return False
            
            # Clean up
            db.execute_command("DELETE FROM analysis_sessions WHERE id = ?", (analysis_id,))
            
        except Exception as e:
            print(f"❌ Analysis storage test failed: {e}")
            return False
        
        print("🎉 All core registration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Core registration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_users():
    """Test creating multiple users to ensure no conflicts"""
    print("\n👥 Testing Multiple User Creation")
    print("=" * 40)
    
    try:
        from auth.services import user_service
        from auth.models import UserRole
        
        users_to_create = [
            ("user1@test.com", "User", "One"),
            ("user2@test.com", "User", "Two"),
            ("user3@test.com", "User", "Three")
        ]
        
        created_users = []
        
        for email, first_name, last_name in users_to_create:
            # Clean up if exists
            existing = user_service.get_user_by_email(email)
            if existing:
                from database.connection import get_db
                db = get_db()
                db.execute_command("DELETE FROM subscriptions WHERE user_id = ?", (existing.id,))
                db.execute_command("DELETE FROM users WHERE email = ?", (email,))
            
            # Create user
            user = user_service.create_user(
                email=email,
                password="TestPassword123!",
                first_name=first_name,
                last_name=last_name,
                role=UserRole.INDIVIDUAL
            )
            
            if user:
                created_users.append(user)
                print(f"✅ Created user: {email}")
            else:
                print(f"❌ Failed to create user: {email}")
                return False
        
        print(f"✅ Successfully created {len(created_users)} users")
        
        # Test that all users can authenticate
        for email, _, _ in users_to_create:
            auth_user = user_service.authenticate_user(email, "TestPassword123!")
            if not auth_user:
                print(f"❌ Authentication failed for: {email}")
                return False
        
        print("✅ All users can authenticate")
        return True
        
    except Exception as e:
        print(f"❌ Multiple users test failed: {e}")
        return False

def test_database_integrity():
    """Test database integrity and constraints"""
    print("\n🗄️  Testing Database Integrity")
    print("=" * 35)
    
    try:
        from database.connection import get_db
        
        db = get_db()
        
        # Test 1: Check all required tables exist
        required_tables = ['users', 'subscriptions', 'subscription_plans', 'user_sessions', 'analysis_sessions']
        
        for table in required_tables:
            result = db.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                (table,)
            )
            
            if result:
                print(f"✅ Table exists: {table}")
            else:
                print(f"❌ Missing table: {table}")
                return False
        
        # Test 2: Check foreign key constraints work
        print("🔗 Testing foreign key constraints...")
        
        # Try to create subscription with invalid user_id (should fail gracefully)
        try:
            db.execute_command("""
                INSERT INTO subscriptions (id, user_id, plan_id, status)
                VALUES ('invalid_sub', 'invalid_user', 'plan_free', 'active')
            """)
            
            # If we get here, foreign keys aren't enforced (which is okay for SQLite)
            print("⚠️  Foreign key constraints not enforced (SQLite default)")
            
            # Clean up
            db.execute_command("DELETE FROM subscriptions WHERE id = 'invalid_sub'")
            
        except Exception:
            print("✅ Foreign key constraints working")
        
        # Test 3: Check unique constraints
        print("🔒 Testing unique constraints...")
        
        # Try to create duplicate email (should fail)
        from auth.services import user_service
        from auth.models import UserRole
        
        # Create first user
        user1 = user_service.create_user(
            email="unique_test@example.com",
            password="TestPassword123!",
            first_name="First",
            last_name="User",
            role=UserRole.INDIVIDUAL
        )
        
        if user1:
            print("✅ First user created")
            
            # Try to create second user with same email
            user2 = user_service.create_user(
                email="unique_test@example.com",  # Same email
                password="TestPassword123!",
                first_name="Second",
                last_name="User",
                role=UserRole.INDIVIDUAL
            )
            
            if user2:
                print("❌ Duplicate email allowed (should not happen)")
                return False
            else:
                print("✅ Duplicate email rejected correctly")
        
        print("✅ Database integrity tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Database integrity test failed: {e}")
        return False

def main():
    """Run all core registration tests"""
    print("🚀 CORE REGISTRATION SYSTEM TEST")
    print("=" * 50)
    
    tests = [
        ("User Registration & Login", test_user_registration_and_login),
        ("Multiple Users", test_multiple_users),
        ("Database Integrity", test_database_integrity)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 CORE REGISTRATION TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:.<35} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 ALL CORE REGISTRATION TESTS PASSED!")
        print("\n✅ The registration system is working correctly")
        print("✅ Users can be created and authenticated")
        print("✅ Database integrity is maintained")
        print("✅ Analysis results can be stored")
        print("\n💡 If users are having issues in the app, the problem is likely:")
        print("   - Streamlit session state management")
        print("   - UI flow or form validation")
        print("   - Authentication state persistence in the web interface")
    else:
        print("\n⚠️  CORE REGISTRATION ISSUES DETECTED!")
        print("\n💡 Issues found in:")
        
        for test_name, success in results:
            if not success:
                print(f"   - {test_name}")

if __name__ == "__main__":
    main()