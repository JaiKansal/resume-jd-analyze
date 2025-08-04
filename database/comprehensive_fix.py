#!/usr/bin/env python3
"""
Comprehensive database schema fix for all identified issues
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def comprehensive_database_fix():
    """Apply all necessary database schema fixes"""
    db_path = Path("data/app.db")
    
    if not db_path.exists():
        logger.error("Database file not found")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("🔧 Starting comprehensive database schema fixes...")
        
        # 1. Fix user_sessions table
        print("\n1. Fixing user_sessions table...")
        cursor.execute("PRAGMA table_info(user_sessions)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
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
        
        if missing_columns:
            print(f"✅ Added columns to user_sessions: {missing_columns}")
        else:
            print("✅ user_sessions table already complete")
        
        # 2. Fix subscriptions table
        print("\n2. Fixing subscriptions table...")
        cursor.execute("PRAGMA table_info(subscriptions)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        missing_columns = []
        if 'plan_id' not in columns:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN plan_id TEXT")
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
            missing_columns.append('plan_id')
        
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
        
        if missing_columns:
            print(f"✅ Added columns to subscriptions: {missing_columns}")
        else:
            print("✅ subscriptions table already complete")
        
        # 3. Fix subscription_plans table
        print("\n3. Fixing subscription_plans table...")
        cursor.execute("PRAGMA table_info(subscription_plans)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        if 'monthly_analysis_limit' not in columns:
            cursor.execute("ALTER TABLE subscription_plans ADD COLUMN monthly_analysis_limit INTEGER")
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
            print("✅ Added monthly_analysis_limit column to subscription_plans")
        else:
            print("✅ subscription_plans table already complete")
        
        # 4. Add missing indexes for performance
        print("\n4. Adding missing indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON user_sessions(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_id ON subscriptions(plan_id)",
            "CREATE INDEX IF NOT EXISTS idx_subscription_plans_plan_type ON subscription_plans(plan_type)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Exception as e:
                logger.warning(f"Index creation warning: {e}")
        
        print("✅ Added missing indexes")
        
        conn.commit()
        
        # 5. Verify all critical queries work
        print("\n5. Verifying database integrity...")
        test_queries = [
            "SELECT id, user_id, session_token, ip_address, user_agent, expires_at, is_active, created_at FROM user_sessions LIMIT 1",
            "SELECT id, email, email_verified, last_login, login_count FROM users LIMIT 1",
            "SELECT id, user_id, plan_id, status, monthly_analysis_used FROM subscriptions LIMIT 1",
            "SELECT id, plan_type, name, monthly_analysis_limit FROM subscription_plans LIMIT 1"
        ]
        
        all_passed = True
        for query in test_queries:
            try:
                cursor.execute(query)
                print(f"✅ Query test passed: {query[:50]}...")
            except Exception as e:
                print(f"❌ Query test failed: {query[:50]}... - {e}")
                all_passed = False
        
        conn.close()
        
        if all_passed:
            print("\n🎉 All database schema fixes completed successfully!")
            print("✅ All critical queries are working")
            return True
        else:
            print("\n❌ Some database schema fixes failed")
            return False
        
    except Exception as e:
        logger.error(f"Comprehensive database fix failed: {e}")
        return False

def main():
    """Main function"""
    logging.basicConfig(level=logging.INFO)
    
    success = comprehensive_database_fix()
    
    if success:
        print("\n🚀 Database is now ready for production use!")
    else:
        print("\n💥 Database fixes failed. Manual intervention may be required.")
    
    return success

if __name__ == "__main__":
    main()