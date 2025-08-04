#!/usr/bin/env python3
"""
Fix database schema issues by adding missing columns and ensuring consistency
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def fix_user_sessions_table():
    """Fix user_sessions table by adding missing columns"""
    db_path = Path("data/app.db")
    
    if not db_path.exists():
        logger.error("Database file not found")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(user_sessions)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        print(f"Current user_sessions columns: {list(columns.keys())}")
        
        # Add missing columns
        missing_columns = []
        
        if 'ip_address' not in columns:
            cursor.execute("ALTER TABLE user_sessions ADD COLUMN ip_address TEXT")
            missing_columns.append('ip_address')
        
        if 'user_agent' not in columns:
            cursor.execute("ALTER TABLE user_sessions ADD COLUMN user_agent TEXT")
            missing_columns.append('user_agent')
        
        if 'is_active' not in columns:
            cursor.execute("ALTER TABLE user_sessions ADD COLUMN is_active BOOLEAN DEFAULT 1")
            missing_columns.append('is_active')
        
        # Add missing indexes if they don't exist
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON user_sessions(is_active)")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")
        
        conn.commit()
        
        if missing_columns:
            print(f"✅ Added missing columns to user_sessions: {missing_columns}")
        else:
            print("✅ user_sessions table already has all required columns")
        
        # Verify the fix
        cursor.execute("PRAGMA table_info(user_sessions)")
        updated_columns = {row[1]: row[2] for row in cursor.fetchall()}
        print(f"Updated user_sessions columns: {list(updated_columns.keys())}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to fix user_sessions table: {e}")
        return False

def fix_users_table():
    """Fix users table by ensuring all required columns exist"""
    db_path = Path("data/app.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(users)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        print(f"Current users columns: {list(columns.keys())}")
        
        # Add missing columns that might be needed
        missing_columns = []
        
        # Check for email_verified vs is_verified inconsistency
        if 'is_verified' in columns and 'email_verified' not in columns:
            # Rename is_verified to email_verified for consistency
            cursor.execute("ALTER TABLE users RENAME COLUMN is_verified TO email_verified")
            missing_columns.append('renamed is_verified to email_verified')
        elif 'email_verified' not in columns and 'is_verified' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0")
            missing_columns.append('email_verified')
        
        # Add other potentially missing columns
        if 'email_verification_token' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN email_verification_token VARCHAR(255)")
            missing_columns.append('email_verification_token')
        
        if 'password_reset_token' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN password_reset_token VARCHAR(255)")
            missing_columns.append('password_reset_token')
        
        if 'password_reset_expires' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN password_reset_expires TIMESTAMP")
            missing_columns.append('password_reset_expires')
        
        if 'last_login' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
            missing_columns.append('last_login')
        
        if 'login_count' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0")
            missing_columns.append('login_count')
        
        conn.commit()
        
        if missing_columns:
            print(f"✅ Fixed users table: {missing_columns}")
        else:
            print("✅ users table already has all required columns")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to fix users table: {e}")
        return False

def fix_subscriptions_table():
    """Fix subscriptions table by ensuring all required columns exist"""
    db_path = Path("data/app.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(subscriptions)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        print(f"Current subscriptions columns: {list(columns.keys())}")
        
        # Add missing columns
        missing_columns = []
        
        if 'trial_start' not in columns:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN trial_start TIMESTAMP")
            missing_columns.append('trial_start')
        
        if 'trial_end' not in columns:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN trial_end TIMESTAMP")
            missing_columns.append('trial_end')
        
        if 'monthly_analysis_used' not in columns:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN monthly_analysis_used INTEGER DEFAULT 0")
            missing_columns.append('monthly_analysis_used')
        
        if 'stripe_customer_id' not in columns:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN stripe_customer_id VARCHAR(255)")
            missing_columns.append('stripe_customer_id')
        
        if 'stripe_subscription_id' not in columns:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN stripe_subscription_id VARCHAR(255)")
            missing_columns.append('stripe_subscription_id')
        
        if 'cancel_at_period_end' not in columns:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN cancel_at_period_end BOOLEAN DEFAULT 0")
            missing_columns.append('cancel_at_period_end')
        
        if 'cancelled_at' not in columns:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN cancelled_at TIMESTAMP")
            missing_columns.append('cancelled_at')
        
        conn.commit()
        
        if missing_columns:
            print(f"✅ Fixed subscriptions table: {missing_columns}")
        else:
            print("✅ subscriptions table already has all required columns")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to fix subscriptions table: {e}")
        return False

def verify_database_integrity():
    """Verify that all tables have the expected structure"""
    db_path = Path("data/app.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Test critical queries that were failing
        test_queries = [
            "SELECT id, user_id, session_token, ip_address, user_agent, expires_at, is_active, created_at FROM user_sessions LIMIT 1",
            "SELECT id, email, email_verified, last_login, login_count FROM users LIMIT 1",
            "SELECT id, user_id, plan_id, status, monthly_analysis_used FROM subscriptions LIMIT 1"
        ]
        
        for query in test_queries:
            try:
                cursor.execute(query)
                print(f"✅ Query test passed: {query[:50]}...")
            except Exception as e:
                print(f"❌ Query test failed: {query[:50]}... - {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Database integrity check failed: {e}")
        return False

def main():
    """Main function to fix all database schema issues"""
    print("🔧 Starting database schema fixes...")
    
    # Fix each table
    success = True
    
    print("\n1. Fixing user_sessions table...")
    if not fix_user_sessions_table():
        success = False
    
    print("\n2. Fixing users table...")
    if not fix_users_table():
        success = False
    
    print("\n3. Fixing subscriptions table...")
    if not fix_subscriptions_table():
        success = False
    
    print("\n4. Verifying database integrity...")
    if not verify_database_integrity():
        success = False
    
    if success:
        print("\n🎉 All database schema fixes completed successfully!")
    else:
        print("\n❌ Some database schema fixes failed. Check the logs.")
    
    return success

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()