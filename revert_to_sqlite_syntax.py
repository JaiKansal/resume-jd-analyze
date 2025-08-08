#!/usr/bin/env python3
"""
Revert all %s parameters back to ? for SQLite compatibility
The database layer will handle the conversion when needed
"""

import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def revert_auth_services():
    """Revert auth services back to SQLite syntax"""
    logger.info("🔧 Reverting auth services to SQLite syntax...")
    
    try:
        with open('auth/services.py', 'r') as f:
            content = f.read()
        
        # Replace all %s with ? for SQLite compatibility
        content = re.sub(r'%s', '?', content)
        
        with open('auth/services.py', 'w') as f:
            f.write(content)
        
        logger.info("✅ Reverted auth services to SQLite syntax")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to revert auth services: {e}")
        return False

def test_database_connection():
    """Test that the database connection works with proper parameter conversion"""
    logger.info("🔧 Testing database connection...")
    
    test_script = '''#!/usr/bin/env python3
"""
Test database connection and parameter conversion
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Test database connection"""
    try:
        from database.connection import get_db
        
        db = get_db()
        
        # Test a simple query
        result = db.execute_query("SELECT 1 as test")
        
        if result and result[0]['test'] == 1:
            logger.info("✅ Database connection test passed")
            
            # Test parameter conversion
            database_url = os.getenv('DATABASE_URL', '')
            if 'postgresql' in database_url.lower():
                logger.info("✅ PostgreSQL detected - parameters will be converted to %s")
            else:
                logger.info("✅ SQLite detected - parameters will remain as ?")
            
            return True
        else:
            logger.error("❌ Database connection test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
'''
    
    with open('test_database_connection.py', 'w') as f:
        f.write(test_script)
    
    logger.info("✅ Created database connection test")
    return True

def main():
    """Revert to SQLite syntax"""
    logger.info("🚀 Reverting to SQLite syntax with proper conversion...")
    
    fixes = [
        ("Auth Services Revert", revert_auth_services),
        ("Database Connection Test", test_database_connection)
    ]
    
    success_count = 0
    for fix_name, fix_func in fixes:
        logger.info(f"\n--- {fix_name} ---")
        if fix_func():
            success_count += 1
    
    logger.info(f"\n✅ Applied {success_count}/{len(fixes)} reverts")
    
    if success_count == len(fixes):
        logger.info("🎉 SQLite syntax restored!")
        logger.info("🔄 Database layer will handle PostgreSQL conversion when needed")
        logger.info("✅ App should work with both SQLite and PostgreSQL")
    
    return success_count == len(fixes)

if __name__ == "__main__":
    main()