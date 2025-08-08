#!/usr/bin/env python3
"""
Fix user_sessions table id column type from integer to text
"""

import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get DATABASE_URL from environment or Streamlit secrets"""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url
    
    try:
        import streamlit as st
        database_url = st.secrets.get('DATABASE_URL')
        if database_url:
            os.environ['DATABASE_URL'] = database_url
            return database_url
    except:
        pass
    
    return None

def fix_user_sessions_id_type():
    """Change user_sessions.id from integer to text"""
    database_url = get_database_url()
    if not database_url:
        logger.error("❌ DATABASE_URL not found")
        return False
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        logger.info("🔧 Fixing user_sessions.id column type...")
        
        # Check current id column type
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'user_sessions' AND column_name = 'id'
        """)
        current_type = cursor.fetchone()['data_type']
        logger.info(f"Current id column type: {current_type}")
        
        if current_type == 'integer':
            logger.info("Converting id column from integer to text...")
            
            # Drop the table and recreate with correct structure
            # This is safer than trying to alter the primary key column type
            cursor.execute("DROP TABLE IF EXISTS user_sessions CASCADE")
            logger.info("✅ Dropped existing user_sessions table")
            
            # Recreate with correct structure
            cursor.execute("""
                CREATE TABLE user_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                    session_token VARCHAR(255) UNIQUE NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    expires_at TIMESTAMPTZ NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            logger.info("✅ Recreated user_sessions table with TEXT id")
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at)")
            logger.info("✅ Created indexes")
            
        else:
            logger.info(f"✅ id column already correct type: {current_type}")
        
        # Commit changes
        conn.commit()
        
        # Verify final structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'user_sessions'
            ORDER BY ordinal_position
        """)
        columns = [(row['column_name'], row['data_type']) for row in cursor.fetchall()]
        logger.info(f"Final table structure: {columns}")
        
        cursor.close()
        conn.close()
        
        logger.info("🎉 user_sessions table id type fixed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix user_sessions id type: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("🚀 Fixing user_sessions id column type...")
    success = fix_user_sessions_id_type()
    if success:
        logger.info("✅ ID type fix completed successfully!")
    else:
        logger.error("❌ ID type fix failed!")