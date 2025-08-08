#!/usr/bin/env python3
"""
Fix analytics columns in analysis_sessions table
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

def fix_analytics_columns():
    """Add missing columns needed by analytics service"""
    database_url = get_database_url()
    if not database_url:
        logger.error("❌ DATABASE_URL not found")
        return False
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        logger.info("🔧 Fixing analytics columns...")
        
        # Check current columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'analysis_sessions'
        """)
        existing_columns = [row['column_name'] for row in cursor.fetchall()]
        logger.info(f"Current columns: {existing_columns}")
        
        # Add missing columns that analytics service expects
        columns_to_add = [
            ("resume_count", "INTEGER DEFAULT 1"),  # Number of resumes analyzed
            ("job_description_count", "INTEGER DEFAULT 1"),  # Number of job descriptions
            ("session_type", "VARCHAR(50) DEFAULT 'single'"),  # Type of analysis session
            ("metadata", "TEXT")  # Session metadata as JSON
        ]
        
        for column_name, column_definition in columns_to_add:
            if column_name not in existing_columns:
                try:
                    alter_query = f"ALTER TABLE analysis_sessions ADD COLUMN {column_name} {column_definition}"
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
            WHERE table_name = 'analysis_sessions'
            ORDER BY ordinal_position
        """)
        final_columns = [row['column_name'] for row in cursor.fetchall()]
        logger.info(f"Final columns: {final_columns}")
        
        cursor.close()
        conn.close()
        
        logger.info("🎉 Analytics columns fixed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix analytics columns: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("🚀 Fixing analytics columns...")
    success = fix_analytics_columns()
    if success:
        logger.info("✅ Analytics columns fix completed!")
    else:
        logger.error("❌ Analytics columns fix failed!")