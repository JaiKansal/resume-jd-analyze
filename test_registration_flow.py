#!/usr/bin/env python3
"""
Test the complete registration flow to identify issues
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_complete_registration_flow():
    """Test the complete registration flow"""
    print("🧪 Testing Complete Registration Flow")
    print("=" * 50)
    
    try:
        # Import required modules
        from auth.services import user_service, subscription_service, session_service
        from auth.models import UserRole, PlanType
        from auth.registration import RegistrationFlow
        
        print("✅ Successfully imported all modules")
        
        # Test data
        test_email = "flow_test@example.com"
        test_password = "TestPassword123!"
        
        # Clean up any existing user
        existing_user = user_service.get_user_by_email(test_email)
        if existing_user:
            from database.connection import get_db
            db = get_db()
            db.execute_command("DELETE FROM subscriptions WHERE user_id = ?", (existing_user.id,))
            db.execute_command("DELETE FROM users WHERE email = ?", (test_email,))
            print("🧹 Cleaned up existing test user")
        
        # Step 1: Create user (simulating registration form submission)
        print("📝 Step 1: Creating user account...")
        user = user_service.create_user(
            email=test_email,
            password=test_password,
            first_name="Flow",
            last_name="Test",
            company_name="Test Company",
            role=UserRole.INDIVIDUAL,
            phone="+1234567890",
            country="United States"
        )
        
        if not user:
            print("❌ Failed to create user")
            return False
        
        print(f"✅ User created: {user.email}")
        
        # Step 2: Get free plan (simulating plan selection)
        print("💳 Step 2: Getting free plan...")
        free_plan = subscription_service.get_plan_by_type(PlanType.FREE)
        
        if not free_plan:
            print("❌ Free plan not found")
            return False
        
        print(f"✅ Free plan found: {free_plan.name}")
        
        # Step 3: Create subscription (simulating subscription creation)
        print("🔗 Step 3: Creating subscription...")
        subscription = subscription_service.create_subscription(user.id, free_plan.id)
        
        if not subscription:
            print("❌ Failed to create subscription")
            return False
        
        print(f"✅ Subscription created: {subscription.status}")
        
        # Step 4: Create session (simulating login)
        print("🔐 Step 4: Creating user session...")
        session = session_service.create_session(user.id)
        
        if not session:
            print("❌ Failed to create session")
            return False
        
        print(f"✅ Session created: {session.id}")
        
        # Step 5: Verify complete user setup
        print("🔍 Step 5: Verifying complete setup...")
        
        # Check user exists and is active
        saved_user = user_service.get_user_by_email(test_email)
        if not saved_user or not saved_user.is_active:
            print("❌ User not properly saved or inactive")
            return False
        
        # Check subscription exists and is active
        user_subscription = subscription_service.get_user_subscription(user.id)
        if not user_subscription or user_subscription.status != 'active':
            print("❌ Subscription not properly created or inactive")
            return False
        
        # Check authentication works
        auth_user = user_service.authenticate_user(test_email, test_password)
        if not auth_user:
            print("❌ Authentication failed")
            return False
        
        print("✅ Complete registration flow successful!")
        print(f"   User ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Subscription: {user_subscription.status}")
        print(f"   Plan: {free_plan.name}")
        print(f"   Usage: {user_subscription.monthly_analysis_used}/{free_plan.monthly_analysis_limit}")
        
        return True
        
    except Exception as e:
        print(f"❌ Registration flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_persistence():
    """Test if sessions persist correctly"""
    print("\n🔄 Testing Session Persistence")
    print("=" * 35)
    
    try:
        from auth.services import session_service, user_service
        
        # Get a test user
        test_user = user_service.get_user_by_email("flow_test@example.com")
        if not test_user:
            print("❌ No test user found")
            return False
        
        # Create session
        session = session_service.create_session(test_user.id)
        if not session:
            print("❌ Failed to create session")
            return False
        
        print(f"✅ Session created: {session.id}")
        
        # Verify session can be retrieved
        retrieved_session = session_service.get_session(session.id)
        if not retrieved_session:
            print("❌ Session not retrievable")
            return False
        
        print(f"✅ Session retrieved: {retrieved_session.id}")
        
        # Check if session is valid
        is_valid = session_service.is_session_valid(session.id)
        if not is_valid:
            print("❌ Session not valid")
            return False
        
        print("✅ Session is valid")
        return True
        
    except Exception as e:
        print(f"❌ Session persistence test failed: {e}")
        return False

def test_data_persistence():
    """Test if user data persists correctly"""
    print("\n💾 Testing Data Persistence")
    print("=" * 30)
    
    try:
        from auth.services import user_service, subscription_service
        
        # Get test user
        test_user = user_service.get_user_by_email("flow_test@example.com")
        if not test_user:
            print("❌ Test user not found")
            return False
        
        print(f"✅ User persisted: {test_user.email}")
        
        # Check subscription
        subscription = subscription_service.get_user_subscription(test_user.id)
        if not subscription:
            print("❌ Subscription not persisted")
            return False
        
        print(f"✅ Subscription persisted: {subscription.status}")
        
        # Test analysis storage (simulate saving analysis result)
        print("📊 Testing analysis result storage...")
        
        # This would normally be done through the analysis storage service
        # For now, just check if the user can have analysis results stored
        from database.connection import get_db
        db = get_db()
        
        # Check if we can store a mock analysis
        try:
            analysis_id = "test_analysis_123"
            db.execute_command("""
                INSERT OR REPLACE INTO analysis_sessions 
                (id, user_id, resume_filename, job_description, analysis_result, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (analysis_id, test_user.id, "test_resume.pdf", "test job description", "test result"))
            
            print("✅ Analysis result storage works")
            
            # Clean up
            db.execute_command("DELETE FROM analysis_sessions WHERE id = ?", (analysis_id,))
            
        except Exception as e:
            print(f"❌ Analysis storage failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Data persistence test failed: {e}")
        return False

def main():
    """Run all registration flow tests"""
    print("🚀 COMPREHENSIVE REGISTRATION FLOW TEST")
    print("=" * 60)
    
    tests = [
        ("Complete Registration Flow", test_complete_registration_flow),
        ("Session Persistence", test_session_persistence),
        ("Data Persistence", test_data_persistence)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 REGISTRATION FLOW TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All registration flow tests passed!")
        print("\n✅ User registration should work correctly in the app")
        print("✅ Users should be able to login again")
        print("✅ Analysis results should be saved")
    else:
        print("⚠️  Some registration flow tests failed.")
        print("\n💡 This indicates issues with:")
        
        for test_name, success in results:
            if not success:
                if "Registration Flow" in test_name:
                    print("   - User account creation process")
                    print("   - Subscription setup")
                elif "Session Persistence" in test_name:
                    print("   - User session management")
                    print("   - Login persistence")
                elif "Data Persistence" in test_name:
                    print("   - Analysis result storage")
                    print("   - User data retention")

if __name__ == "__main__":
    main()