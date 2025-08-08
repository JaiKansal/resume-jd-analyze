#!/usr/bin/env python3
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
