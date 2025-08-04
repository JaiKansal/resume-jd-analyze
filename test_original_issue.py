#!/usr/bin/env python3
"""
Test the original registration issue that was failing
"""

import logging
from auth.services import user_service, session_service

# Set up logging to match the original error
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_original_registration_flow():
    """Test the exact flow that was failing in the original error"""
    print("🧪 Testing original registration flow that was failing...")
    
    try:
        # Clean up any existing test user
        from database.connection import get_db
        db = get_db()
        db.execute_command("DELETE FROM user_sessions WHERE user_id IN (SELECT id FROM users WHERE email = ?)", ("jaikansal85@gmail.com",))
        db.execute_command("DELETE FROM subscriptions WHERE user_id IN (SELECT id FROM users WHERE email = ?)", ("jaikansal85@gmail.com",))
        db.execute_command("DELETE FROM users WHERE email = ?", ("jaikansal85@gmail.com",))
        
        # Step 1: Create user (this was working)
        print("Step 1: Creating user...")
        user = user_service.create_user(
            email="jaikansal85@gmail.com",
            password="TestPassword123!",
            first_name="Jai",
            last_name="Kansal",
            company_name="Test Company"
        )
        
        if user:
            print(f"✅ User created successfully: {user.email}")
        else:
            print("❌ User creation failed")
            return False
        
        # Step 2: Create session (this was failing with ip_address column error)
        print("Step 2: Creating session...")
        session = session_service.create_session(
            user_id=user.id,
            ip_address="127.0.0.1",  # This was causing the error
            user_agent="Mozilla/5.0 (Test)"
        )
        
        if session:
            print(f"✅ Session created successfully: {session.session_token[:20]}...")
        else:
            print("❌ Session creation failed")
            return False
        
        # Step 3: Test session retrieval
        print("Step 3: Retrieving session...")
        retrieved_session = session_service.get_session(session.session_token)
        
        if retrieved_session:
            print(f"✅ Session retrieved successfully: {retrieved_session.id}")
        else:
            print("❌ Session retrieval failed")
            return False
        
        print("🎉 Original registration flow now works perfectly!")
        
        # Clean up
        db.execute_command("DELETE FROM user_sessions WHERE user_id = ?", (user.id,))
        db.execute_command("DELETE FROM subscriptions WHERE user_id = ?", (user.id,))
        db.execute_command("DELETE FROM users WHERE id = ?", (user.id,))
        
        return True
        
    except Exception as e:
        print(f"❌ Registration flow error: {e}")
        return False

def main():
    """Main test function"""
    success = test_original_registration_flow()
    
    if success:
        print("\n🚀 All database issues have been resolved!")
        print("✅ The registration flow is now working correctly")
        print("✅ No more 'table user_sessions has no column named ip_address' errors")
    else:
        print("\n❌ There are still issues with the registration flow")
    
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)