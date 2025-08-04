"""
Simple Database Initialization
Minimal, bulletproof database setup for Streamlit Cloud
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def create_minimal_database():
    """Create minimal database with essential tables only"""
    try:
        # Ensure data directory exists
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        
        db_path = 'data/app.db'
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create users table (essential)
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
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create subscriptions table (essential)
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
            
            # Create usage tracking table (essential)
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
            
            # Create analysis sessions table (for report persistence)
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
            
            # Create subscription plans table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscription_plans (
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
            INSERT OR IGNORE INTO subscription_plans 
            (id, plan_type, name, price_monthly, price_annual, features, is_active)
            VALUES 
            ('plan_free', 'free', 'Free', 0, 0, '["3 analyses per month", "Basic reports", "PDF download"]', TRUE),
            ('plan_professional', 'professional', 'Professional', 1499, 14990, '["Unlimited analyses", "Advanced AI insights", "All export formats"]', TRUE),
            ('plan_business', 'business', 'Business', 7999, 79990, '["Everything in Professional", "Team collaboration", "Analytics dashboard"]', TRUE),
            ('plan_enterprise', 'enterprise', 'Enterprise', 39999, 399990, '["Everything in Business", "Unlimited seats", "Custom integrations"]', TRUE)
            """)
            
            conn.commit()
            logger.info("Minimal database created successfully")
            return True
            
    except Exception as e:
        logger.error(f"Failed to create minimal database: {e}")
        return False

def ensure_database_exists():
    """Ensure database exists and is functional"""
    try:
        db_path = 'data/app.db'
        
        # Check if database exists and has users table
        if Path(db_path).exists():
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
                if cursor.fetchone():
                    # Database exists, run migration to add missing columns
                    _run_migrations()
                    logger.info("Database already exists and is functional")
                    return True
        
        # Create database if it doesn't exist or is incomplete
        return create_minimal_database()
        
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        # Try to create from scratch
        return create_minimal_database()

def _run_migrations():
    """Run database migrations"""
    try:
        from database.migrate_add_is_active import add_is_active_column
        add_is_active_column()
    except Exception as e:
        logger.error(f"Migration failed: {e}")

# Auto-run when imported
if __name__ != "__main__":
    ensure_database_exists()