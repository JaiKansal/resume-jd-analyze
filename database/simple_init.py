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