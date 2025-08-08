#!/usr/bin/env python3
"""
Fix analysis_sessions table by adding missing team_id column
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

def fix_analysis_sessions_table():
    """Add missing team_id column to analysis_sessions table"""
    database_url = get_database_url()
    if not database_url:
        logger.error("❌ DATABASE_URL not found")
        return False
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        logger.info("🔧 Fixing analysis_sessions table...")
        
        # Check current columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'analysis_sessions'
        """)
        existing_columns = [row['column_name'] for row in cursor.fetchall()]
        logger.info(f"Existing columns: {existing_columns}")
        
        # Add missing team_id column
        if 'team_id' not in existing_columns:
            try:
                cursor.execute("ALTER TABLE analysis_sessions ADD COLUMN team_id TEXT")
                logger.info("✅ Added team_id column")
            except Exception as e:
                logger.warning(f"⚠️ Could not add team_id column: {e}")
        else:
            logger.info("✅ team_id column already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify final structure
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'analysis_sessions'
            ORDER BY ordinal_position
        """)
        final_columns = [row['column_name'] for row in cursor.fetchall()]
        logger.info(f"Final columns: {final_columns}")
        
        cursor.close()
        conn.close()
        
        logger.info("🎉 analysis_sessions table fixed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix analysis_sessions table: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("🚀 Fixing analysis_sessions table...")
    success = fix_analysis_sessions_table()
    if success:
        logger.info("✅ Table fix completed successfully!")
    else:
        logger.error("❌ Table fix failed!")