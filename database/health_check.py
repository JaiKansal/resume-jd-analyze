"""
Database Health Check for Streamlit Cloud
Ensures database is working before app starts
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def check_and_fix_database():
    """Check database health and fix if needed"""
    try:
        # Ensure data directory exists
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        
        db_path = 'data/app.db'
        
        # Test database connection and tables
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                logger.warning("Users table missing, creating database schema")
                create_database_schema(conn)
            else:
                logger.info("Database health check passed")
        
        return True
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        # Try to create database from scratch
        try:
            create_database_schema_from_scratch()
            logger.info("Database created from scratch")
            return True
        except Exception as e2:
            logger.error(f"Failed to create database from scratch: {e2}")
            return False

def create_database_schema(conn):
    """Create database schema in existing connection"""
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create all tables
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            company_name TEXT,
            phone TEXT,
            role TEXT DEFAULT 'user',
            country TEXT DEFAULT 'IN',
            is_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS subscriptions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            plan_type TEXT NOT NULL DEFAULT 'free',
            status TEXT NOT NULL DEFAULT 'active',
            current_period_start TIMESTAMP,
            current_period_end TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS subscription_plans (
            id TEXT PRIMARY KEY,
            plan_type TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            price_monthly REAL NOT NULL,
            price_annual REAL NOT NULL,
            features TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS usage_tracking (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            analysis_count INTEGER DEFAULT 0,
            period_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            period_end TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS analysis_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            resume_filename TEXT,
            job_description TEXT,
            analysis_result TEXT,
            score INTEGER,
            match_category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS payment_records (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            razorpay_payment_id TEXT,
            amount INTEGER NOT NULL,
            currency TEXT DEFAULT 'INR',
            status TEXT NOT NULL,
            plan_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]
    
    for table_sql in tables:
        cursor.execute(table_sql)
    
    # Create indexes
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        "CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_analysis_sessions_user_id ON analysis_sessions(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_payment_records_user_id ON payment_records(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token)"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    conn.commit()

def create_database_schema_from_scratch():
    """Create database schema from scratch"""
    db_path = 'data/app.db'
    
    # Remove existing database if corrupted
    if Path(db_path).exists():
        Path(db_path).unlink()
    
    # Create new database
    with sqlite3.connect(db_path) as conn:
        create_database_schema(conn)

# Run health check when imported
if __name__ != "__main__":
    check_and_fix_database()