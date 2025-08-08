#!/usr/bin/env python3
"""
Test registration debugging to identify the issue
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set environment variables
os.environ.setdefault('PYTHONPATH', str(project_root))

# Set up DATABASE_URL from environment or secrets
if not os.getenv('DATABASE_URL'):
    try:
        import streamlit as st
        database_url = st.secrets.get('DATABASE_URL')
        if database_url:
            os.environ['DATABASE_URL'] = database_url
    except:
        pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_user_creation():
    """Test user creation to debug registration issues"""
    try:
        from auth.registration import get_auth_service
        from auth.models import UserRole
        
        logger.info("🧪 Testing user creation...")
        
        auth_service = get_auth_service()
        logger.info(f"Auth service: {type(auth_service)}")
        
        # Test creating a new user
        test_email = "test_registration@example.com"
        
        logger.info(f"Creating user: {test_email}")
        
        user = auth_service.create_user(
            email=test_email,
            password="testpassword123",
            first_name="Test",
            last_name="User",
            company_name="Test Company",
            role=UserRole.INDIVIDUAL,
            phone="+1234567890",
            country="United States"
        )
        
        if user:
            logger.info(f"✅ User created successfully: {user.email}")
            logger.info(f"User ID: {user.id}")
            logger.info(f"User role: {user.role}")
            return True
        else:
            logger.error("❌ User creation returned None")
            return False
            
    except Exception as e:
        logger.error(f"❌ User creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_subscription_creation():
    """Test subscription creation"""
    try:
        from billing.subscription_service import subscription_service
        
        logger.info("🧪 Testing subscription creation...")
        
        # Test creating a subscription for free plan
        subscription = subscription_service.create_subscription(
            user_id="test_user_id",
            plan_id="plan_free"
        )
        
        if subscription:
            logger.info(f"✅ Subscription created successfully: {subscription.id}")
            return True
        else:
            logger.error("❌ Subscription creation returned None")
            return False
            
    except Exception as e:
        logger.error(f"❌ Subscription creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("🚀 Debugging registration issues...")
    
    user_success = test_user_creation()
    subscription_success = test_subscription_creation()
    
    if user_success and subscription_success:
        logger.info("🎉 All registration components working!")
    else:
        logger.error("❌ Registration issues found!")
        if not user_success:
            logger.error("- User creation failed")
        if not subscription_success:
            logger.error("- Subscription creation failed")