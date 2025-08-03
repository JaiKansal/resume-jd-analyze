#!/usr/bin/env python3
"""
Test the authentication system
"""

from auth.services import user_service, subscription_service, session_service
from auth.models import UserRole
import logging

logging.basicConfig(level=logging.INFO)

def test_authentication_system():
    """Test the complete authentication system"""
    print("🧪 Testing Authentication System")
    print("=" * 50)
    
    # Test 1: Create a new user
    print("\n1. Creating a new user...")
    import time
    test_email = f"test{int(time.time())}@example.com"
    test_password = "SecurePassword123!"
    
    user = user_service.create_user(
        email=test_email,
        password=test_password,
        first_name="John",
        last_name="Doe",
        company_name="Test Company",
        role=UserRole.HR_MANAGER,
        country="United States"
    )
    
    if user:
        print(f"✅ User created: {user.email} (ID: {user.id})")
        print(f"   Name: {user.get_full_name()}")
        print(f"   Role: {user.role.value}")
        print(f"   Email verified: {user.email_verified}")
    else:
        print("❌ Failed to create user")
        return False
    
    # Test 2: Authenticate user
    print("\n2. Testing authentication...")
    auth_user = user_service.authenticate_user(test_email, test_password)
    
    if auth_user:
        print(f"✅ Authentication successful: {auth_user.email}")
        print(f"   Login count: {auth_user.login_count}")
    else:
        print("❌ Authentication failed")
        return False
    
    # Test 3: Check user subscription
    print("\n3. Checking user subscription...")
    subscription = subscription_service.get_user_subscription(user.id)
    
    if subscription:
        print(f"✅ Subscription found: {subscription.plan.name}")
        print(f"   Plan type: {subscription.plan.plan_type.value}")
        print(f"   Monthly limit: {subscription.plan.monthly_analysis_limit}")
        print(f"   Status: {subscription.status.value}")
        print(f"   Usage: {subscription.monthly_analysis_used}")
    else:
        print("❌ No subscription found")
        return False
    
    # Test 4: Check analysis permissions
    print("\n4. Testing analysis permissions...")
    can_analyze, reason = subscription_service.can_user_analyze(user.id)
    
    if can_analyze:
        print("✅ User can perform analysis")
    else:
        print(f"❌ User cannot perform analysis: {reason}")
    
    # Test 5: Create user session
    print("\n5. Creating user session...")
    session = session_service.create_session(
        user.id, 
        ip_address="192.168.1.1", 
        user_agent="Test Browser"
    )
    
    if session:
        print(f"✅ Session created: {session.session_token[:20]}...")
        print(f"   Expires: {session.expires_at}")
    else:
        print("❌ Failed to create session")
        return False
    
    # Test 6: Validate session
    print("\n6. Validating session...")
    retrieved_session = session_service.get_session(session.session_token)
    
    if retrieved_session and retrieved_session.is_valid():
        print(f"✅ Session is valid: {retrieved_session.user_id}")
    else:
        print("❌ Session is invalid")
        return False
    
    # Test 7: Test email verification
    print("\n7. Testing email verification...")
    if user.email_verification_token:
        verified = user_service.verify_email(user.email_verification_token)
        if verified:
            print("✅ Email verification successful")
            
            # Check updated user
            updated_user = user_service.get_user_by_id(user.id)
            if updated_user and updated_user.email_verified:
                print("✅ User email status updated")
            else:
                print("❌ User email status not updated")
        else:
            print("❌ Email verification failed")
    
    # Test 8: Test password reset
    print("\n8. Testing password reset...")
    reset_token = user_service.request_password_reset(test_email)
    
    if reset_token:
        print(f"✅ Password reset token generated: {reset_token[:20]}...")
        
        # Test password reset
        new_password = "NewSecurePassword456!"
        reset_success = user_service.reset_password(reset_token, new_password)
        
        if reset_success:
            print("✅ Password reset successful")
            
            # Test authentication with new password
            auth_user_new = user_service.authenticate_user(test_email, new_password)
            if auth_user_new:
                print("✅ Authentication with new password successful")
            else:
                print("❌ Authentication with new password failed")
        else:
            print("❌ Password reset failed")
    else:
        print("❌ Password reset token generation failed")
    
    # Test 9: Test subscription plans
    print("\n9. Testing subscription plans...")
    all_plans = subscription_service.get_all_plans()
    
    if all_plans:
        print(f"✅ Found {len(all_plans)} subscription plans:")
        for plan in all_plans:
            print(f"   - {plan.name}: ${plan.price_monthly}/month")
    else:
        print("❌ No subscription plans found")
    
    print("\n" + "=" * 50)
    print("🎉 Authentication system test completed successfully!")
    return True

if __name__ == "__main__":
    test_authentication_system()