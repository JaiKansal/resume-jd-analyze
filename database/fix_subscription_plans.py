#!/usr/bin/env python3
"""
Fix subscription_plans table schema
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def fix_subscription_plans_schema():
    """Fix subscription_plans table schema"""
    db_path = Path("data/app.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(subscription_plans)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        print(f"Current subscription_plans columns: {list(columns.keys())}")
        
        # Add missing monthly_analysis_limit column
        if 'monthly_analysis_limit' not in columns:
            cursor.execute("ALTER TABLE subscription_plans ADD COLUMN monthly_analysis_limit INTEGER")
            print("✅ Added monthly_analysis_limit column")
            
            # Update existing plans with proper limits
            cursor.execute("""
                UPDATE subscription_plans 
                SET monthly_analysis_limit = CASE 
                    WHEN plan_type = 'free' THEN 3
                    WHEN plan_type = 'professional' THEN -1
                    WHEN plan_type = 'business' THEN -1
                    WHEN plan_type = 'enterprise' THEN -1
                    ELSE 3
                END
            """)
            print("✅ Updated monthly_analysis_limit values")
        
        conn.commit()
        
        # Verify the fix
        cursor.execute("SELECT id, plan_type, name, monthly_analysis_limit FROM subscription_plans")
        results = cursor.fetchall()
        print(f"Updated subscription plans: {results}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to fix subscription_plans schema: {e}")
        return False

def main():
    """Main function to fix subscription_plans schema"""
    print("🔧 Fixing subscription_plans table schema...")
    
    if fix_subscription_plans_schema():
        print("🎉 Subscription plans schema fixed successfully!")
    else:
        print("❌ Failed to fix subscription plans schema")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()