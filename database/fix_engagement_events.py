#!/usr/bin/env python3
"""
Fix the missing engagement_events table and parameters column
"""

import sqlite3
import os
from pathlib import Path

def fix_engagement_events_table():
    """Add the missing engagement_events table"""
    
    # Database path
    db_path = Path("data/app.db")
    
    if not db_path.exists():
        print("❌ Database not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if engagement_events table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='engagement_events'
        """)
        
        if cursor.fetchone():
            print("✅ engagement_events table already exists")
            
            # Check if parameters column exists
            cursor.execute("PRAGMA table_info(engagement_events)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'parameters' not in columns:
                print("🔧 Adding missing parameters column...")
                cursor.execute("""
                    ALTER TABLE engagement_events 
                    ADD COLUMN parameters TEXT
                """)
                print("✅ Parameters column added")
            else:
                print("✅ Parameters column already exists")
        else:
            print("🔧 Creating engagement_events table...")
            cursor.execute("""
                CREATE TABLE engagement_events (
                    id TEXT PRIMARY KEY,
                    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                    event_type VARCHAR(50) NOT NULL,
                    parameters TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ engagement_events table created")
        
        conn.commit()
        conn.close()
        
        print("🎉 Database fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    fix_engagement_events_table()