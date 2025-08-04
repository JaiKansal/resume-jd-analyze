"""
Emergency Database Initialization
Ultra-simple database setup that works on any environment
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def emergency_database_setup():
    """Create the most basic database schema that works everywhere"""
    try:
        # Ensure data directory exists
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        
        db_path = 'data/app.db'
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create users table (minimal)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT DEFAULT '',
                last_name TEXT DEFAULT '',
                company_name TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                role TEXT DEFAULT 'user',
                country TEXT DEFAULT 'IN',
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create subscriptions table (minimal)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                plan_type TEXT NOT NULL DEFAULT 'free',
                status TEXT NOT NULL DEFAULT 'active',
                current_period_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                current_period_end TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create subscription_plans table (minimal)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscription_plans (
                id TEXT PRIMARY KEY,
                plan_type TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                price_monthly REAL NOT NULL,
                price_annual REAL NOT NULL,
                features TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create usage_tracking table (minimal)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_tracking (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                analysis_count INTEGER DEFAULT 0,
                period_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                period_end TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create analysis_sessions table (minimal)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                resume_filename TEXT DEFAULT '',
                job_description TEXT DEFAULT '',
                analysis_result TEXT DEFAULT '',
                score INTEGER DEFAULT 0,
                match_category TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Insert default plans (without is_active dependency)
            cursor.execute("""
            INSERT OR IGNORE INTO subscription_plans 
            (id, plan_type, name, price_monthly, price_annual, features)
            VALUES 
            ('plan_free', 'free', 'Free', 0, 0, '["3 analyses per month", "Basic reports"]'),
            ('plan_professional', 'professional', 'Professional', 1499, 14990, '["Unlimited analyses", "Advanced AI insights"]'),
            ('plan_business', 'business', 'Business', 7999, 79990, '["Team collaboration", "Analytics dashboard"]'),
            ('plan_enterprise', 'enterprise', 'Enterprise', 39999, 399990, '["Custom integrations", "Dedicated support"]')
            """)
            
            conn.commit()
            logger.info("Emergency database setup completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Emergency database setup failed: {e}")
        return False

def force_clean_database():
    """Force clean database recreation"""
    try:
        db_path = 'data/app.db'
        
        # Remove existing database
        if Path(db_path).exists():
            Path(db_path).unlink()
            logger.info("Removed existing database")
        
        # Create fresh database
        return emergency_database_setup()
        
    except Exception as e:
        logger.error(f"Force clean database failed: {e}")
        return False

if __name__ == "__main__":
    print("🚨 Emergency Database Setup")
    print("=" * 30)
    
    choice = input("1. Emergency setup\n2. Force clean setup\nChoose (1-2): ")
    
    if choice == "1":
        result = emergency_database_setup()
    elif choice == "2":
        result = force_clean_database()
    else:
        print("Invalid choice")
        exit(1)
    
    if result:
        print("✅ Database setup successful!")
    else:
        print("❌ Database setup failed!")