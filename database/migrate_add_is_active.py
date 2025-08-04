"""
Database Migration: Add is_active column to users table
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def add_is_active_column():
    """Add is_active column to tables if it doesn't exist"""
    try:
        db_path = 'data/app.db'
        
        if not Path(db_path).exists():
            logger.info("Database doesn't exist, skipping migration")
            return True
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Add is_active to users table
            cursor.execute("PRAGMA table_info(users)")
            user_columns = [column[1] for column in cursor.fetchall()]
            
            if 'is_active' not in user_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
                cursor.execute("UPDATE users SET is_active = TRUE WHERE is_active IS NULL")
                logger.info("Added is_active column to users table")
            
            # Check if subscription_plans table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subscription_plans'")
            if not cursor.fetchone():
                # Create subscription_plans table
                cursor.execute("""
                CREATE TABLE subscription_plans (
                    id TEXT PRIMARY KEY,
                    plan_type TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    price_monthly REAL NOT NULL,
                    price_annual REAL NOT NULL,
                    features TEXT DEFAULT '',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # Insert default plans
                cursor.execute("""
                INSERT INTO subscription_plans 
                (id, plan_type, name, price_monthly, price_annual, features, is_active)
                VALUES 
                ('plan_free', 'free', 'Free', 0, 0, '["3 analyses per month"]', TRUE),
                ('plan_professional', 'professional', 'Professional', 1499, 14990, '["Unlimited analyses"]', TRUE),
                ('plan_business', 'business', 'Business', 7999, 79990, '["Team collaboration"]', TRUE),
                ('plan_enterprise', 'enterprise', 'Enterprise', 39999, 399990, '["Custom integrations"]', TRUE)
                """)
                
                logger.info("Created subscription_plans table with default plans")
            else:
                # Add is_active to subscription_plans if missing
                cursor.execute("PRAGMA table_info(subscription_plans)")
                plan_columns = [column[1] for column in cursor.fetchall()]
                
                if 'is_active' not in plan_columns:
                    cursor.execute("ALTER TABLE subscription_plans ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
                    cursor.execute("UPDATE subscription_plans SET is_active = TRUE WHERE is_active IS NULL")
                    logger.info("Added is_active column to subscription_plans table")
            
            conn.commit()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to add is_active column: {e}")
        return False

if __name__ == "__main__":
    add_is_active_column()