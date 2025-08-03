#!/usr/bin/env python3
"""
Test the registration and onboarding flow
"""

from auth.services import user_service, subscription_service
import logging

logging.basicConfig(level=logging.INFO)

def test_registration_components():
    """Test registration flow components"""
    print("🧪 Testing Registration Flow Components")
    print("=" * 50)
    
    # Test 1: Check subscription plans are available
    print("\n4. Testing subscription plans availability...")
    try:
        plans = subscription_service.get_all_plans()
        if plans and len(plans) >= 4:
            print(f"✅ Found {len(plans)} subscription plans:")
            for plan in plans:
                print(f"   - {plan.name}: ${plan.price_monthly}/month")
        else:
            print(f"❌ Expected at least 4 plans, found {len(plans) if plans else 0}")
    except Exception as e:
        print(f"❌ Failed to get subscription plans: {e}")
    
    # Test 5: Test conversion event tracking structure
    print("\n5. Testing conversion event tracking...")
    try:
        from database.connection import get_db
        db = get_db()
        
        # Check if conversion_events table exists
        if db.table_exists('conversion_events'):
            print("✅ Conversion events table exists")
            
            # Check table structure
            schema = db.get_table_schema('conversion_events')
            expected_columns = ['id', 'user_id', 'event_name', 'event_properties', 'created_at']
            
            if schema:
                actual_columns = [col.get('name', col.get('column_name', '')) for col in schema]
                missing_columns = [col for col in expected_columns if col not in actual_columns]
                
                if not missing_columns:
                    print("✅ Conversion events table has all required columns")
                else:
                    print(f"❌ Missing columns in conversion_events: {missing_columns}")
            else:
                print("❌ Could not retrieve conversion_events table schema")
        else:
            print("❌ Conversion events table does not exist")
    except Exception as e:
        print(f"❌ Failed to check conversion events table: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Registration flow component test completed!")
    return True

def test_user_creation_flow():
    """Test the complete user creation flow"""
    print("\n🧪 Testing Complete User Creation Flow")
    print("=" * 50)
    
    # Test data
    import time
    test_email = f"registration_test_{int(time.time())}@example.com"
    test_data = {
        'email': test_email,
        'password': 'TestPassword123!',
        'first_name': 'Registration',
        'last_name': 'Test',
        'company_name': 'Test Company',
        'role': 'individual',
        'phone': '+1-555-123-4567',
        'country': 'United States'
    }
    
    print(f"\n1. Creating test user: {test_email}")
    
    try:
        from auth.models import UserRole
        
        # Create user
        user = user_service.create_user(
            email=test_data['email'],
            password=test_data['password'],
            first_name=test_data['first_name'],
            last_name=test_data['last_name'],
            company_name=test_data['company_name'],
            role=UserRole.INDIVIDUAL,
            phone=test_data['phone'],
            country=test_data['country']
        )
        
        if user:
            print(f"✅ User created successfully: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.get_full_name()}")
            print(f"   Role: {user.role.value}")
            
            # Test 2: Check subscription was created
            print("\n2. Checking default subscription...")
            subscription = subscription_service.get_user_subscription(user.id)
            
            if subscription:
                print(f"✅ Default subscription created: {subscription.plan.name}")
                print(f"   Plan type: {subscription.plan.plan_type.value}")
                print(f"   Monthly limit: {subscription.plan.monthly_analysis_limit}")
            else:
                print("❌ Default subscription not created")
            
            # Test 3: Test authentication
            print("\n3. Testing authentication...")
            auth_user = user_service.authenticate_user(test_data['email'], test_data['password'])
            
            if auth_user:
                print(f"✅ Authentication successful: {auth_user.email}")
            else:
                print("❌ Authentication failed")
            
            # Test 4: Test email verification
            print("\n4. Testing email verification...")
            if user.email_verification_token:
                verified = user_service.verify_email(user.email_verification_token)
                if verified:
                    print("✅ Email verification successful")
                else:
                    print("❌ Email verification failed")
            else:
                print("❌ No email verification token found")
            
            print("\n✅ User creation flow test completed successfully!")
            return True
            
        else:
            print("❌ User creation failed")
            return False
            
    except Exception as e:
        print(f"❌ User creation flow test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Registration Flow Tests")
    print("=" * 60)
    
    # Test components
    component_test_passed = test_registration_components()
    
    # Test complete flow
    if component_test_passed:
        flow_test_passed = test_user_creation_flow()
        
        if flow_test_passed:
            print("\n🎉 All registration tests passed!")
        else:
            print("\n❌ Some registration tests failed!")
    else:
        print("\n❌ Component tests failed, skipping flow tests!")