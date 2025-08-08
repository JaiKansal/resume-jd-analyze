#!/usr/bin/env python3
"""
Debug user creation to see what's failing
"""

import os
import logging
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set DATABASE_URL from environment or simulate Streamlit secrets
if not os.getenv('DATABASE_URL'):
    # Simulate what happens in Streamlit Cloud
    database_url = "postgresql://neondb_owner:npg_password@ep-host.us-east-2.aws.neon.tech/neondb?sslmode=require"
    os.environ['DATABASE_URL'] = database_url
    print(f"✅ DATABASE_URL set from simulated secrets")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_postgresql_service():
    """Test PostgreSQL service directly"""
    try:
        from auth.postgresql_service import postgresql_auth_service
        
        logger.info("🧪 Testing PostgreSQL service...")
        logger.info(f"Service configured: {postgresql_auth_service.is_postgresql}")
        logger.info(f"Database URL exists: {bool(postgresql_auth_service.database_url)}")
        
        if not postgresql_auth_service.is_postgresql:
            logger.error("❌ PostgreSQL service not configured properly")
            return False
        
        # Test user creation
        test_email = f"debug_test_{os.urandom(4).hex()}@example.com"
        logger.info(f"Creating test user: {test_email}")
        
        user = postgresql_auth_service.create_user(
            email=test_email,
            password="testpassword123",
            first_name="Debug",
            last_name="Test",
            company_name="Test Company",
            role="individual",
            phone="+1234567890",
            country="United States"
        )
        
        if user:
            logger.info(f"✅ User created successfully!")
            logger.info(f"User ID: {user.id}")
            logger.info(f"User email: {user.email}")
            logger.info(f"User type: {type(user)}")
            return True
        else:
            logger.error("❌ User creation returned None")
            return False
            
    except Exception as e:
        logger.error(f"❌ PostgreSQL service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_auth_service_selection():
    """Test which auth service is being selected"""
    try:
        from auth.registration import get_auth_service
        
        logger.info("🧪 Testing auth service selection...")
        
        auth_service = get_auth_service()
        logger.info(f"Selected auth service: {type(auth_service)}")
        
        if hasattr(auth_service, 'is_postgresql'):
            logger.info(f"Is PostgreSQL: {auth_service.is_postgresql}")
        
        return auth_service
        
    except Exception as e:
        logger.error(f"❌ Auth service selection failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    logger.info("🚀 Debugging user creation issues...")
    
    # Test PostgreSQL service directly
    postgresql_success = test_postgresql_service()
    
    # Test auth service selection
    auth_service = test_auth_service_selection()
    
    if postgresql_success:
        logger.info("🎉 PostgreSQL service working!")
    else:
        logger.error("❌ PostgreSQL service issues found!")
    
    if auth_service:
        logger.info("🎉 Auth service selection working!")
    else:
        logger.error("❌ Auth service selection issues found!")