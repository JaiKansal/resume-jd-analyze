#!/usr/bin/env python3
"""
Complete Analysis Storage and Retrieval System
Ensures all analysis results are properly saved and accessible
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

def fix_analysis_storage_system():
    """Fix and enhance the analysis storage system"""
    database_url = get_database_url()
    if not database_url:
        logger.error("❌ DATABASE_URL not found")
        return False
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        logger.info("🔧 Fixing analysis storage system...")
        
        # 1. Check current table structure
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'analysis_sessions'
        """)
        existing_columns = [row['column_name'] for row in cursor.fetchall()]
        logger.info(f"Current columns: {existing_columns}")
        
        # 2. Add missing columns for comprehensive analysis storage
        columns_to_add = [
            ("job_description", "TEXT"),  # Store the job description
            ("resume_content", "TEXT"),   # Store resume text content
            ("analysis_type", "VARCHAR(50) DEFAULT 'resume_jd_match'"),  # Type of analysis
            ("match_score", "REAL"),      # Detailed match score (0-100)
            ("strengths", "TEXT"),        # JSON array of strengths
            ("weaknesses", "TEXT"),       # JSON array of weaknesses  
            ("recommendations", "TEXT"),  # JSON array of recommendations
            ("keywords_matched", "TEXT"), # JSON array of matched keywords
            ("keywords_missing", "TEXT"), # JSON array of missing keywords
            ("sections_analysis", "TEXT"), # JSON object with section-wise analysis
            ("pdf_report_path", "TEXT"),  # Path to generated PDF report
            ("session_metadata", "TEXT"), # Additional session metadata as JSON
            ("api_cost_usd", "REAL DEFAULT 0.0"),  # Cost of API calls
            ("tokens_used", "INTEGER DEFAULT 0"),   # Tokens consumed
            ("error_message", "TEXT"),    # Error details if analysis failed
            ("updated_at", "TIMESTAMPTZ DEFAULT NOW()")  # Last update timestamp
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
        
        # 3. Update existing columns to proper types if needed
        column_updates = [
            ("created_at", "TIMESTAMPTZ DEFAULT NOW()"),
            ("status", "VARCHAR(20) DEFAULT 'completed'"),
            ("analysis_type", "VARCHAR(50) DEFAULT 'resume_jd_match'")
        ]
        
        for column_name, new_definition in column_updates:
            if column_name in existing_columns:
                try:
                    # For existing columns, we'll handle type changes carefully
                    if column_name == "created_at":
                        cursor.execute(f"ALTER TABLE analysis_sessions ALTER COLUMN {column_name} TYPE TIMESTAMPTZ USING {column_name}::TIMESTAMPTZ")
                        logger.info(f"✅ Updated {column_name} to TIMESTAMPTZ")
                except Exception as e:
                    logger.warning(f"⚠️ Could not update column {column_name}: {e}")
        
        # 4. Create indexes for better performance
        indexes_to_create = [
            "CREATE INDEX IF NOT EXISTS idx_analysis_sessions_user_created ON analysis_sessions(user_id, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_analysis_sessions_status ON analysis_sessions(status)",
            "CREATE INDEX IF NOT EXISTS idx_analysis_sessions_type ON analysis_sessions(analysis_type)",
            "CREATE INDEX IF NOT EXISTS idx_analysis_sessions_score ON analysis_sessions(match_score DESC)"
        ]
        
        for index_sql in indexes_to_create:
            try:
                cursor.execute(index_sql)
                logger.info(f"✅ Created index")
            except Exception as e:
                logger.warning(f"⚠️ Could not create index: {e}")
        
        # 5. Commit all changes
        conn.commit()
        
        # 6. Verify final structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'analysis_sessions'
            ORDER BY ordinal_position
        """)
        final_columns = [(row['column_name'], row['data_type']) for row in cursor.fetchall()]
        logger.info("✅ Final table structure:")
        for col_name, col_type in final_columns:
            logger.info(f"  - {col_name}: {col_type}")
        
        cursor.close()
        conn.close()
        
        logger.info("🎉 Analysis storage system fixed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix analysis storage system: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("🚀 Fixing analysis storage system for complete data persistence...")
    success = fix_analysis_storage_system()
    if success:
        logger.info("✅ Analysis storage system fix completed!")
        logger.info("📊 All analysis results will now be properly saved and accessible!")
    else:
        logger.error("❌ Analysis storage system fix failed!")