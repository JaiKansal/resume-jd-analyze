#!/usr/bin/env python3
"""
Emergency database fix for timestamp column issues
Run this if the app is still having timestamp errors
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_engagement_events_table():
    """Fix the engagement_events table to have the correct columns"""
    try:
        conn = sqlite3.connect('data/app.db')
        cursor = conn.cursor()
        
        # Check if timestamp column exists
        cursor.execute("PRAGMA table_info(engagement_events)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'timestamp' not in columns:
            logger.info("Adding timestamp column to engagement_events...")
            cursor.execute("ALTER TABLE engagement_events ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
            logger.info("✅ Added timestamp column")
        else:
            logger.info("✅ timestamp column already exists")
        
        # Also ensure analytics_events table exists with correct schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_events (
                id TEXT PRIMARY KEY,
                event_name TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                page_path TEXT,
                parameters TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON analytics_events(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_events_event_name ON analytics_events(event_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_events_created_at ON analytics_events(created_at)")
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Database schema fixed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database fix failed: {e}")
        return False

if __name__ == "__main__":
    fix_engagement_events_table()
