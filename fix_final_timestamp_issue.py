#!/usr/bin/env python3
"""
Fix the final timestamp column issue in Google Analytics
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_google_analytics_timestamp():
    """Fix the timestamp column issue in Google Analytics"""
    logger.info("🔧 Fixing Google Analytics timestamp column issue...")
    
    try:
        with open('analytics/google_analytics.py', 'r') as f:
            content = f.read()
        
        # Replace the problematic CREATE TABLE statement
        old_create_table = '''CREATE TABLE IF NOT EXISTS analytics_events (
            id TEXT PRIMARY KEY,
            event_name TEXT NOT NULL,
            user_id TEXT,
            session_id TEXT,
            page_path TEXT,
            parameters TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''
        
        new_create_table = '''CREATE TABLE IF NOT EXISTS analytics_events (
            id TEXT PRIMARY KEY,
            event_name TEXT NOT NULL,
            user_id TEXT,
            session_id TEXT,
            page_path TEXT,
            parameters TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''
        
        # Replace the problematic index creation
        old_index = 'CREATE INDEX IF NOT EXISTS idx_analytics_events_timestamp ON analytics_events(timestamp)'
        new_index = 'CREATE INDEX IF NOT EXISTS idx_analytics_events_created_at ON analytics_events(created_at)'
        
        # Apply fixes
        content = content.replace(old_create_table, new_create_table)
        content = content.replace(old_index, new_index)
        
        # Also fix any INSERT statements that use timestamp
        content = content.replace('timestamp)', 'created_at)')
        content = content.replace('?, ?)', '?, ?)')
        
        with open('analytics/google_analytics.py', 'w') as f:
            f.write(content)
        
        logger.info("✅ Fixed Google Analytics timestamp column issue")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix Google Analytics: {e}")
        return False

def fix_user_engagement_timestamp():
    """Fix any remaining timestamp issues in user engagement"""
    logger.info("🔧 Checking user engagement for timestamp issues...")
    
    try:
        with open('analytics/user_engagement.py', 'r') as f:
            content = f.read()
        
        # Ensure all queries use created_at instead of timestamp
        if 'timestamp' in content and 'created_at' not in content.replace('timestamp', ''):
            content = content.replace('timestamp', 'created_at')
            
            with open('analytics/user_engagement.py', 'w') as f:
                f.write(content)
            
            logger.info("✅ Fixed user engagement timestamp references")
        else:
            logger.info("✅ User engagement already uses created_at")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix user engagement: {e}")
        return False

def create_emergency_database_fix():
    """Create an emergency database fix for the timestamp issue"""
    logger.info("🔧 Creating emergency database fix...")
    
    emergency_fix = '''#!/usr/bin/env python3
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
'''
    
    try:
        with open('emergency_database_fix.py', 'w') as f:
            f.write(emergency_fix)
        
        logger.info("✅ Created emergency database fix script")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create emergency fix: {e}")
        return False

def main():
    """Run all timestamp fixes"""
    logger.info("🚀 Fixing final timestamp issues...")
    
    fixes = [
        ("Google Analytics", fix_google_analytics_timestamp),
        ("User Engagement", fix_user_engagement_timestamp),
        ("Emergency Database Fix", create_emergency_database_fix)
    ]
    
    success_count = 0
    for fix_name, fix_func in fixes:
        if fix_func():
            success_count += 1
    
    logger.info(f"✅ Applied {success_count}/{len(fixes)} timestamp fixes")
    
    if success_count == len(fixes):
        logger.info("🎉 All timestamp issues should now be resolved!")
        logger.info("🔄 The fixes will take effect on the next Streamlit Cloud deployment")
    
    return success_count == len(fixes)

if __name__ == "__main__":
    main()