#!/usr/bin/env python3
"""
Database Fix Script for Resume + JD Analyzer
Fixes all database persistence issues and ensures proper data storage
"""

import os
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseFixer:
    """Fix all database issues"""
    
    def __init__(self):
        self.db_path = 'data/app.db'
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        logger.info(f"Data directory ensured: {data_dir.absolute()}")
    
    def fix_database_schema(self):
        """Fix and create proper database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Enable foreign keys
                cursor.execute("PRAGMA foreign_keys = ON")
                
                # Create users table with proper constraints
                cursor.execute("""
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
                """)
                
                # Create subscriptions table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    plan_type TEXT NOT NULL DEFAULT 'free',
                    status TEXT NOT NULL DEFAULT 'active',
                    current_period_start TIMESTAMP,
                    current_period_end TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """)
                
                # Create usage tracking table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage_tracking (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    analysis_count INTEGER DEFAULT 0,
                    period_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    period_end TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """)
                
                # Create analysis sessions table (for report persistence)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    resume_filename TEXT,
                    job_description TEXT,
                    analysis_result TEXT,
                    score INTEGER,
                    match_category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """)
                
                # Create payment records table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_records (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    razorpay_payment_id TEXT,
                    amount INTEGER NOT NULL,
                    currency TEXT DEFAULT 'INR',
                    status TEXT NOT NULL,
                    plan_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """)
                
                conn.commit()
                logger.info("Database schema fixed successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to fix database schema: {e}")
            return False
    
    def fix_user_sessions(self):
        """Fix user session persistence"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create user sessions table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """)
                
                conn.commit()
                logger.info("User sessions table fixed")
                return True
                
        except Exception as e:
            logger.error(f"Failed to fix user sessions: {e}")
            return False
    
    def reset_usage_limits_properly(self):
        """Fix usage limit tracking to prevent resets on login"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Update usage tracking to use monthly periods
                cursor.execute("""
                UPDATE usage_tracking 
                SET period_end = datetime('now', '+1 month')
                WHERE period_end IS NULL OR period_end < datetime('now')
                """)
                
                conn.commit()
                logger.info("Usage limits fixed")
                return True
                
        except Exception as e:
            logger.error(f"Failed to fix usage limits: {e}")
            return False
    
    def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
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
                logger.info("Database indexes created")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            return False
    
    def fix_all_issues(self):
        """Fix all database issues"""
        print("🔧 Fixing all database issues...")
        
        results = []
        results.append(("Database Schema", self.fix_database_schema()))
        results.append(("User Sessions", self.fix_user_sessions()))
        results.append(("Usage Limits", self.reset_usage_limits_properly()))
        results.append(("Database Indexes", self.create_indexes()))
        
        print("\n📊 Fix Results:")
        for name, success in results:
            status = "✅ Fixed" if success else "❌ Failed"
            print(f"  {status}: {name}")
        
        all_fixed = all(result[1] for result in results)
        
        if all_fixed:
            print("\n🎉 All database issues fixed successfully!")
            print(f"📁 Database location: {Path(self.db_path).absolute()}")
        else:
            print("\n⚠️  Some issues remain. Check logs for details.")
        
        return all_fixed

if __name__ == "__main__":
    fixer = DatabaseFixer()
    fixer.fix_all_issues()