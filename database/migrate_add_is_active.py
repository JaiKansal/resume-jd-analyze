"""
Database Migration: Add is_active column to users table
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def add_is_active_column():
    """Add is_active column to users table if it doesn't exist"""
    try:
        db_path = 'data/app.db'
        
        if not Path(db_path).exists():
            logger.info("Database doesn't exist, skipping migration")
            return True
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if is_active column exists
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'is_active' not in columns:
                # Add is_active column
                cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
                
                # Update all existing users to be active
                cursor.execute("UPDATE users SET is_active = TRUE WHERE is_active IS NULL")
                
                conn.commit()
                logger.info("Added is_active column to users table")
            else:
                logger.info("is_active column already exists")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to add is_active column: {e}")
        return False

if __name__ == "__main__":
    add_is_active_column()