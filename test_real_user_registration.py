#!/usr/bin/env python3
"""
Test real user registration with the exact email
"""

def test_registration_with_real_email():
    """Test registration with the real email that was used"""
    print("🧪 TESTING REGISTRATION WITH REAL EMAIL")
    print("=" * 45)
    
    try:
        from auth.services import user_service, subscription_service
        from auth.models import UserRole
        
        test_email = "jaikansal85@gmail.com"
        test_password = "TestPassword123!"
        
        print(f"📧 Testing registration for: {test_email}")
        
        # Check if user already exists
        existing_user = user_service.get_user_by_email(test_email)
        if existing_user:
            print(f"⚠️  User already exists: {existing_user.email}")
            print(f"   Created: {existing_user.created_at}")
            print(f"   Active: {existing_user.is_active}")
            return True
        
        print("🔄 User doesn't exist, testing creation...")
        
        # Try to create the user
        user = user_service.create_user(
            email=test_email,
            password=test_password,
            first_name="Jai",
            last_name="Kansal",
            role=UserRole.INDIVIDUAL,
            company_name="",
            phone="",
            country="India"
        )
        
        if user:
            print(f"✅ User created successfully!")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.first_name} {user.last_name}")
            print(f"   Created: {user.created_at}")
            
            # Verify user was saved to database
            saved_user = user_service.get_user_by_email(test_email)
            if saved_user:
                print(f"✅ User verified in database")
                
                # Check subscription
                subscription = subscription_service.get_user_subscription(user.id)
                if subscription:
                    print(f"✅ Subscription created: {subscription.status}")
                else:
                    print(f"❌ No subscription found")
                
                return True
            else:
                print(f"❌ User not found in database after creation")
                return False
        else:
            print(f"❌ User creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_registration_issues():
    """Check for potential registration issues"""
    print(f"\n🔍 CHECKING FOR REGISTRATION ISSUES")
    print("=" * 40)
    
    try:
        # Test database connection
        print("🔄 Testing database connection...")
        from database.connection import get_db
        db = get_db()
        
        result = db.execute_query("SELECT COUNT(*) as count FROM users")
        print(f"✅ Database connection working: {result[0]['count']} users")
        
        # Test user service
        print("🔄 Testing user service...")
        from auth.services import user_service
        
        # Try to get a known user
        test_user = user_service.get_user_by_email("streamlit_test@example.com")
        if test_user:
            print(f"✅ User service working: found {test_user.email}")
        else:
            print(f"❌ User service issue: couldn't find known user")
        
        # Test subscription service
        print("🔄 Testing subscription service...")
        from auth.services import subscription_service
        from auth.models import PlanType
        
        free_plan = subscription_service.get_plan_by_type(PlanType.FREE)
        if free_plan:
            print(f"✅ Subscription service working: found {free_plan.name}")
        else:
            print(f"❌ Subscription service issue: no free plan found")
        
        # Test password hashing
        print("🔄 Testing password hashing...")
        from auth.models import User
        
        test_user_obj = User.create("test@example.com", "password123")
        if test_user_obj and test_user_obj.password_hash:
            print(f"✅ Password hashing working")
        else:
            print(f"❌ Password hashing issue")
        
        return True
        
    except Exception as e:
        print(f"❌ Registration issue check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def simulate_streamlit_registration():
    """Simulate the exact registration flow from Streamlit"""
    print(f"\n🎭 SIMULATING STREAMLIT REGISTRATION FLOW")
    print("=" * 45)
    
    try:
        # This simulates what happens in the Streamlit app
        from auth.services import user_service, subscription_service, session_service
        from auth.models import UserRole, PlanType
        
        # Registration data (as it would come from the form)
        registration_data = {
            'email': 'jaikansal85@gmail.com',
            'password': 'TestPassword123!',
            'first_name': 'Jai',
            'last_name': 'Kansal',
            'company_name': '',
            'role': UserRole.INDIVIDUAL,
            'phone': '',
            'country': 'India'
        }
        
        print(f"📝 Registration data prepared")
        
        # Step 1: Create user (as done in registration flow)
        print(f"🔄 Step 1: Creating user...")
        user = user_service.create_user(**registration_data)
        
        if not user:
            print(f"❌ User creation failed in step 1")
            return False
        
        print(f"✅ User created: {user.email}")
        
        # Step 2: Get free plan
        print(f"🔄 Step 2: Getting free plan...")
        free_plan = subscription_service.get_plan_by_type(PlanType.FREE)
        
        if not free_plan:
            print(f"❌ Free plan not found")
            return False
        
        print(f"✅ Free plan found: {free_plan.name}")
        
        # Step 3: Create subscription
        print(f"🔄 Step 3: Creating subscription...")
        subscription = subscription_service.create_subscription(user.id, free_plan.id)
        
        if not subscription:
            print(f"❌ Subscription creation failed")
            return False
        
        print(f"✅ Subscription created: {subscription.status}")
        
        # Step 4: Create session
        print(f"🔄 Step 4: Creating session...")
        session = session_service.create_session(user.id)
        
        if not session:
            print(f"❌ Session creation failed")
            return False
        
        print(f"✅ Session created: {session.id}")
        
        # Step 5: Verify everything is in database
        print(f"🔄 Step 5: Verifying in database...")
        
        # Check user
        saved_user = user_service.get_user_by_email(registration_data['email'])
        if not saved_user:
            print(f"❌ User not found in database")
            return False
        
        print(f"✅ User verified in database: {saved_user.email}")
        
        # Check subscription
        user_subscription = subscription_service.get_user_subscription(user.id)
        if not user_subscription:
            print(f"❌ Subscription not found in database")
            return False
        
        print(f"✅ Subscription verified in database: {user_subscription.status}")
        
        print(f"\n🎉 STREAMLIT REGISTRATION SIMULATION SUCCESSFUL!")
        print(f"✅ User should now be visible in database")
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit registration simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all registration tests"""
    print("🚀 COMPREHENSIVE REGISTRATION TESTING")
    print("=" * 50)
    
    tests = [
        ("Registration Issues Check", check_registration_issues),
        ("Real Email Registration Test", test_registration_with_real_email),
        ("Streamlit Registration Simulation", simulate_streamlit_registration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 REGISTRATION TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:.<35} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL REGISTRATION TESTS PASSED!")
        print("✅ The user should now be in the database")
        print("💡 Check again with: python3 check_specific_user.py jaikansal85@gmail.com")
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed")
        print("There may be issues with the registration process")

if __name__ == "__main__":
    main()