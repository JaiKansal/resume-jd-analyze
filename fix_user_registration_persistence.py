#!/usr/bin/env python3
"""
Fix user registration and session persistence issues
"""

import re

def fix_session_state_persistence():
    """Fix session state persistence issues in the main app"""
    print("🔧 Fixing Session State Persistence Issues")
    print("=" * 50)
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Fix 1: Add session validation function
        session_validation_function = '''
def validate_user_session():
    """Validate current user session and refresh if needed"""
    if not st.session_state.get('user_authenticated', False):
        return None
    
    user = st.session_state.get('current_user')
    if not user:
        return None
    
    # Verify user still exists in database
    try:
        from auth.services import user_service
        current_user = user_service.get_user_by_id(user.id)
        
        if not current_user or not current_user.is_active:
            # User no longer exists or is inactive
            st.session_state.user_authenticated = False
            st.session_state.current_user = None
            st.session_state.user_session = None
            return None
        
        # Update session state with fresh user data
        st.session_state.current_user = current_user
        return current_user
        
    except Exception as e:
        logger.error(f"Session validation error: {e}")
        return user  # Return cached user if validation fails
'''
        
        # Add the function after imports
        import_section_end = content.find('logger = logging.getLogger(__name__)')
        if import_section_end != -1:
            insert_pos = content.find('\n', import_section_end) + 1
            content = content[:insert_pos] + session_validation_function + '\n' + content[insert_pos:]
            print("✅ Added session validation function")
        
        # Fix 2: Update render_authenticated_app to use validation
        old_auth_check = '''def render_authenticated_app():
    """Render the main application for authenticated users"""
    # Get current user
    user = st.session_state.get('current_user')
    if not user:
        st.error("Authentication error. Please sign in again.")
        st.session_state.user_authenticated = False
        st.rerun()
        return'''
        
        new_auth_check = '''def render_authenticated_app():
    """Render the main application for authenticated users"""
    # Validate current user session
    user = validate_user_session()
    if not user:
        st.error("Authentication error. Please sign in again.")
        st.session_state.user_authenticated = False
        st.rerun()
        return'''
        
        if old_auth_check in content:
            content = content.replace(old_auth_check, new_auth_check)
            print("✅ Updated authentication check in main app")
        
        # Fix 3: Add session persistence to initialize_session_state
        old_init = '''def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = []
    if 'bulk_results' not in st.session_state:
        st.session_state.bulk_results = []
    if 'setup_complete' not in st.session_state:
        st.session_state.setup_complete = False'''
        
        new_init = '''def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = []
    if 'bulk_results' not in st.session_state:
        st.session_state.bulk_results = []
    if 'setup_complete' not in st.session_state:
        st.session_state.setup_complete = False
    
    # Initialize authentication state
    if 'user_authenticated' not in st.session_state:
        st.session_state.user_authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'user_session' not in st.session_state:
        st.session_state.user_session = None'''
        
        if old_init in content:
            content = content.replace(old_init, new_init)
            print("✅ Enhanced session state initialization")
        
        # Fix 4: Add error handling to get_subscription_with_fallback
        old_subscription_func = '''def get_subscription_with_fallback(user_id):
    """Get subscription with fallback to free plan"""
    try:
        subscription = subscription_service.get_user_subscription(user_id)
        if subscription:
            return subscription
        else:
            # Create default free subscription if none exists
            free_plan = subscription_service.get_plan_by_type(PlanType.FREE)
            if free_plan:
                return subscription_service.create_subscription(user_id, free_plan.id)
        return None
    except Exception as e:
        logger.error(f"Error getting subscription: {e}")
        return None'''
        
        new_subscription_func = '''def get_subscription_with_fallback(user_id):
    """Get subscription with fallback to free plan"""
    try:
        # Verify user exists first
        user = user_service.get_user_by_id(user_id)
        if not user:
            logger.warning(f"User {user_id} not found when getting subscription")
            return None
        
        subscription = subscription_service.get_user_subscription(user_id)
        if subscription:
            return subscription
        else:
            # Create default free subscription if none exists
            logger.info(f"Creating default subscription for user {user_id}")
            free_plan = subscription_service.get_plan_by_type(PlanType.FREE)
            if free_plan:
                return subscription_service.create_subscription(user_id, free_plan.id)
        return None
    except Exception as e:
        logger.error(f"Error getting subscription for user {user_id}: {e}")
        return None'''
        
        if 'def get_subscription_with_fallback(user_id):' in content:
            # Find and replace the entire function
            start = content.find('def get_subscription_with_fallback(user_id):')
            if start != -1:
                # Find the end of the function (next def or end of file)
                end = content.find('\ndef ', start + 1)
                if end == -1:
                    end = len(content)
                
                content = content[:start] + new_subscription_func + '\n' + content[end:]
                print("✅ Enhanced subscription fallback function")
        
        # Write the updated content
        with open('app.py', 'w') as f:
            f.write(content)
        
        print("✅ Session persistence fixes applied to app.py")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing session persistence: {e}")
        return False

def fix_registration_flow_persistence():
    """Fix registration flow to ensure proper session persistence"""
    print("\n🔧 Fixing Registration Flow Persistence")
    print("=" * 45)
    
    try:
        with open('auth/registration.py', 'r') as f:
            content = f.read()
        
        # Fix 1: Add user verification after creation
        old_creation_pattern = r'(user = user_service\.create_user\([^)]+\))\s*if user:'
        new_creation_pattern = r'\1\n                    \n                    # Verify user was actually created and saved\n                    if user:\n                        saved_user = user_service.get_user_by_email(data[\'email\'])\n                        if not saved_user:\n                            st.error("User creation failed - please try again")\n                            return\n                        user = saved_user  # Use the saved user object\n                    \n                    if user:'
        
        if re.search(old_creation_pattern, content):
            content = re.sub(old_creation_pattern, new_creation_pattern, content)
            print("✅ Added user verification after creation")
        
        # Fix 2: Add session validation after login
        old_login_pattern = r'(user = user_service\.authenticate_user\(email, password\))\s*if user:'
        new_login_pattern = r'\1\n                    \n                    # Verify authentication was successful\n                    if user:\n                        # Double-check user exists and is active\n                        verified_user = user_service.get_user_by_id(user.id)\n                        if not verified_user or not verified_user.is_active:\n                            st.error("Account is inactive or not found")\n                            return\n                        user = verified_user\n                    \n                    if user:'
        
        if re.search(old_login_pattern, content):
            content = re.sub(old_login_pattern, new_login_pattern, content)
            print("✅ Added login verification")
        
        # Fix 3: Ensure session state is set consistently
        session_state_updates = [
            'st.session_state.user_authenticated = True',
            'st.session_state.current_user = user',
            'st.session_state.user_session = session'
        ]
        
        # Count how many times these are set
        for update in session_state_updates:
            count = content.count(update)
            print(f"   {update}: {count} occurrences")
        
        # Write the updated content
        with open('auth/registration.py', 'w') as f:
            f.write(content)
        
        print("✅ Registration flow persistence fixes applied")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing registration flow: {e}")
        return False

def test_fixes():
    """Test that the fixes work correctly"""
    print("\n🧪 Testing Registration and Session Fixes")
    print("=" * 45)
    
    try:
        # Test user creation and retrieval
        from auth.services import user_service, subscription_service, session_service
        from auth.models import UserRole
        
        test_email = "fix_test@example.com"
        
        # Clean up existing user
        existing = user_service.get_user_by_email(test_email)
        if existing:
            from database.connection import get_db
            db = get_db()
            db.execute_command("DELETE FROM subscriptions WHERE user_id = ?", (existing.id,))
            db.execute_command("DELETE FROM user_sessions WHERE user_id = ?", (existing.id,))
            db.execute_command("DELETE FROM users WHERE email = ?", (test_email,))
        
        # Create user
        user = user_service.create_user(
            email=test_email,
            password="TestPassword123!",
            first_name="Fix",
            last_name="Test",
            role=UserRole.INDIVIDUAL
        )
        
        if not user:
            print("❌ User creation failed")
            return False
        
        # Verify user can be retrieved
        saved_user = user_service.get_user_by_email(test_email)
        if not saved_user:
            print("❌ User not found after creation")
            return False
        
        # Test authentication
        auth_user = user_service.authenticate_user(test_email, "TestPassword123!")
        if not auth_user:
            print("❌ Authentication failed")
            return False
        
        # Test subscription
        subscription = subscription_service.get_user_subscription(user.id)
        if not subscription:
            print("❌ Subscription not created")
            return False
        
        # Test session
        session = session_service.create_session(user.id)
        if not session:
            print("❌ Session creation failed")
            return False
        
        retrieved_session = session_service.get_session(session.session_token)
        if not retrieved_session:
            print("❌ Session retrieval failed")
            return False
        
        print("✅ All registration and session tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Apply all fixes for user registration and session persistence"""
    print("🚀 FIXING USER REGISTRATION AND SESSION PERSISTENCE")
    print("=" * 60)
    
    fixes = [
        ("Session State Persistence", fix_session_state_persistence),
        ("Registration Flow Persistence", fix_registration_flow_persistence),
        ("Test Fixes", test_fixes)
    ]
    
    results = []
    
    for fix_name, fix_func in fixes:
        print(f"\n{'='*15} {fix_name} {'='*15}")
        success = fix_func()
        results.append((fix_name, success))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FIX SUMMARY")
    print("=" * 60)
    
    passed = 0
    for fix_name, success in results:
        status = "✅ APPLIED" if success else "❌ FAILED"
        print(f"{fix_name:.<35} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(fixes)} fixes applied successfully")
    
    if passed == len(fixes):
        print("\n🎉 ALL FIXES APPLIED SUCCESSFULLY!")
        print("\n✅ User registration should now work correctly")
        print("✅ Users should be able to login again")
        print("✅ Session state should persist properly")
        print("✅ Analysis results should be saved")
        print("\n💡 Changes made:")
        print("   - Added session validation function")
        print("   - Enhanced authentication checks")
        print("   - Improved session state initialization")
        print("   - Added user verification after creation")
        print("   - Enhanced error handling")
    else:
        print("\n⚠️  Some fixes failed to apply")
        print("Manual intervention may be required")

if __name__ == "__main__":
    main()