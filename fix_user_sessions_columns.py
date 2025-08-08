#!/usr/bin/env python3
"""
Fix user_sessions table to add missing columns
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

def fix_user_sessions_table():
    """Add missing columns to user_sessions table"""
    database_url = get_database_url()
    if not database_url:
        logger.error("❌ DATABASE_URL not found")
        return False
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        logger.info("🔧 Fixing user_sessions table columns...")
        
        # Check current table structure
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user_sessions'
        """)
        existing_columns = [row['column_name'] for row in cursor.fetchall()]
        logger.info(f"Existing columns: {existing_columns}")
        
        # Add missing columns if they don't exist
        columns_to_add = [
            ("ip_address", "TEXT"),
            ("user_agent", "TEXT"),
            ("is_active", "BOOLEAN DEFAULT TRUE")
        ]
        
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                try:
                    alter_query = f"ALTER TABLE user_sessions ADD COLUMN {column_name} {column_type}"
                    cursor.execute(alter_query)
                    logger.info(f"✅ Added column: {column_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not add column {column_name}: {e}")
            else:
                logger.info(f"✅ Column {column_name} already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify final structure
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user_sessions'
            ORDER BY ordinal_position
        """)
        final_columns = [row['column_name'] for row in cursor.fetchall()]
        logger.info(f"Final columns: {final_columns}")
        
        cursor.close()
        conn.close()
        
        logger.info("🎉 user_sessions table fixed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix user_sessions table: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("🚀 Fixing user_sessions table columns...")
    success = fix_user_sessions_table()
    if success:
        logger.info("✅ Table fix completed successfully!")
    else:
        logger.error("❌ Table fix failed!")