#!/usr/bin/env python3
"""
Fix subscriptions table schema to match expected structure
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def fix_subscriptions_schema():
    """Fix subscriptions table schema issues"""
    db_path = Path("data/app.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(subscriptions)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        print(f"Current subscriptions columns: {list(columns.keys())}")
        
        # Add plan_id column if missing
        if 'plan_id' not in columns:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN plan_id TEXT")
            print("✅ Added plan_id column")
            
            # Populate plan_id based on plan_type
            cursor.execute("""
                UPDATE subscriptions 
                SET plan_id = CASE 
                    WHEN plan_type = 'free' THEN 'plan_free'
                    WHEN plan_type = 'professional' THEN 'plan_professional'
                    WHEN plan_type = 'business' THEN 'plan_business'
                    WHEN plan_type = 'enterprise' THEN 'plan_enterprise'
                    ELSE 'plan_free'
                END
            """)
            print("✅ Populated plan_id values based on plan_type")
        
        conn.commit()
        
        # Verify the fix
        cursor.execute("SELECT id, user_id, plan_id, plan_type, status FROM subscriptions LIMIT 5")
        results = cursor.fetchall()
        print(f"Sample subscriptions data: {results}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to fix subscriptions schema: {e}")
        return False

def main():
    """Main function to fix subscriptions schema"""
    print("🔧 Fixing subscriptions table schema...")
    
    if fix_subscriptions_schema():
        print("🎉 Subscriptions schema fixed successfully!")
    else:
        print("❌ Failed to fix subscriptions schema")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()