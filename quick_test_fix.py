#!/usr/bin/env python3
"""
Quick fix to test your app immediately
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_database_for_testing():
    """Clear the database so you can test with fresh registration"""
    
    try:
        conn = sqlite3.connect('data/app.db')
        cursor = conn.cursor()
        
        # Check current users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        logger.info(f"📊 Current users in database: {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT email FROM users ORDER BY created_at DESC LIMIT 3")
            recent_users = cursor.fetchall()
            logger.info("Recent users:")
            for email, in recent_users:
                logger.info(f"  - {email}")
        
        # Clear all user data for fresh testing
        logger.info("🧹 Clearing all user data for fresh testing...")
        
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM analysis_sessions") 
        cursor.execute("DELETE FROM subscriptions")
        cursor.execute("DELETE FROM engagement_events")
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Database cleared successfully!")
        logger.info("🎯 You can now register with any email address")
        logger.info("💡 This is temporary - set up PostgreSQL for permanent solution")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to clear database: {e}")
        return False

if __name__ == "__main__":
    logger.info("🧪 Quick Test Fix - Clear Database")
    logger.info("=" * 50)
    
    if clear_database_for_testing():
        logger.info("\n🎉 SUCCESS!")
        logger.info("✅ Database cleared - you can now test registration")
        logger.info("🔄 Commit and push this change to apply on Streamlit Cloud")
    else:
        logger.error("\n❌ FAILED!")
        logger.error("Check the error messages above")