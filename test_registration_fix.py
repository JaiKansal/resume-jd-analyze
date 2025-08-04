#!/usr/bin/env python3
"""
Test the registration flow to ensure all database issues are fixed
"""

import logging
from auth.services import user_service, subscription_service, session_service
from auth.models import UserRole

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_user_creation():
    """Test user creation"""
    print("🧪 Testing user creation...")
    
    try:
        # Create a test user
        user = user_service.create_user(
            email="test_fix@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="User",
            company_name="Test Company",
            role=UserRole.INDIVIDUAL,
            phone="+1234567890",
            country="United States"
        )
        
        if user:
            print(f"✅ User created successfully: {user.email}")
            return user
        else:
            print("❌ User creation failed")
            return None
            
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return None

def test_session_creation(user):
    """Test session creation with ip_address and user_agent"""
    print("🧪 Testing session creation...")
    
    try:
        # Create a session with ip_address and user_agent
        session = session_service.create_session(
            user_id=user.id,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0 (Test Browser)"
        )
        
        if session:
            print(f"✅ Session created successfully: {session.session_token[:20]}...")
            return session
        else:
            print("❌ Session creation failed")
            return None
            
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return None

def test_subscription_retrieval(user):
    """Test subscription retrieval"""
    print("🧪 Testing subscription retrieval...")
    
    try:
        # Get user subscription
        subscription = subscription_service.get_user_subscription(user.id)
        
        if subscription:
            print(f"✅ Subscription retrieved successfully: {subscription.plan.name}")
            return subscription
        else:
            print("❌ Subscription retrieval failed")
            return None
            
    except Exception as e:
        print(f"❌ Subscription retrieval error: {e}")
        return None

def test_authentication(user):
    """Test user authentication"""
    print("🧪 Testing user authentication...")
    
    try:
        # Authenticate user
        authenticated_user = user_service.authenticate_user(
            email=user.email,
            password="TestPassword123!"
        )
        
        if authenticated_user:
            print(f"✅ User authenticated successfully: {authenticated_user.email}")
            return authenticated_user
        else:
            print("❌ User authentication failed")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def cleanup_test_user():
    """Clean up test user"""
    print("🧹 Cleaning up test user...")
    
    try:
        from database.connection import get_db
        db = get_db()
        
        # Delete test user and related data
        db.execute_command("DELETE FROM user_sessions WHERE user_id IN (SELECT id FROM users WHERE email = ?)", ("test_fix@example.com",))
        db.execute_command("DELETE FROM subscriptions WHERE user_id IN (SELECT id FROM users WHERE email = ?)", ("test_fix@example.com",))
        db.execute_command("DELETE FROM users WHERE email = ?", ("test_fix@example.com",))
        
        print("✅ Test user cleaned up")
        
    except Exception as e:
        print(f"❌ Cleanup error: {e}")

def main():
    """Main test function"""
    print("🚀 Starting registration flow tests...")
    
    # Clean up any existing test user first
    cleanup_test_user()
    
    # Test user creation
    user = test_user_creation()
    if not user:
        print("❌ Cannot continue tests without user")
        return False
    
    # Test session creation
    session = test_session_creation(user)
    if not session:
        print("❌ Session creation failed")
        cleanup_test_user()
        return False
    
    # Test subscription retrieval
    subscription = test_subscription_retrieval(user)
    if not subscription:
        print("❌ Subscription retrieval failed")
        cleanup_test_user()
        return False
    
    # Test authentication
    authenticated_user = test_authentication(user)
    if not authenticated_user:
        print("❌ Authentication failed")
        cleanup_test_user()
        return False
    
    # Clean up
    cleanup_test_user()
    
    print("🎉 All registration flow tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)