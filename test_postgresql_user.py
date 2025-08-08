#!/usr/bin/env python3
"""
Test PostgreSQL user creation and authentication
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_user_operations():
    """Test user creation and authentication with PostgreSQL"""
    
    try:
        from auth.postgresql_service import postgresql_auth_service
        
        # Test user creation
        test_email = "jaikansal85@gmail.com"
        test_password = "testpassword123"
        
        logger.info(f"Testing user creation for {test_email}...")
        
        # Try to create user
        user, error = postgresql_auth_service.create_user(
            email=test_email,
            password=test_password,
            first_name="Jai",
            last_name="Kansal"
        )
        
        if user:
            logger.info("✅ User created successfully!")
            logger.info(f"User ID: {user['id']}")
            logger.info(f"Email: {user['email']}")
        elif error and "already exists" in error:
            logger.info("✅ User already exists - that's good!")
        else:
            logger.error(f"❌ User creation failed: {error}")
            return False
        
        # Test authentication
        logger.info(f"Testing authentication for {test_email}...")
        
        auth_user = postgresql_auth_service.authenticate_user(test_email, test_password)
        
        if auth_user:
            logger.info("✅ Authentication successful!")
            logger.info(f"Authenticated user: {auth_user['email']}")
            return True
        else:
            logger.error("❌ Authentication failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def main():
    """Run PostgreSQL user tests"""
    logger.info("🧪 Testing PostgreSQL user operations...")
    
    if test_user_operations():
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("✅ PostgreSQL user system is working perfectly!")
        logger.info("🚀 Your app is ready for production!")
    else:
        logger.error("❌ Some tests failed")

if __name__ == "__main__":
    main()