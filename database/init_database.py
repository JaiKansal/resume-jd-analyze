"""
Database Initialization for Streamlit Cloud
Automatically creates database schema on app startup
"""

import os
import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def init_database_for_streamlit():
    """Initialize database for Streamlit Cloud deployment"""
    try:
        # Ensure data directory exists
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        
        db_path = 'data/app.db'
        
        # Create database with all required tables
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Create users table
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
            
            # Create subscription plans table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscription_plans (
                id TEXT PRIMARY KEY,
                plan_type TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                price_monthly REAL NOT NULL,
                price_annual REAL NOT NULL,
                features TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            
            # Create analysis sessions table
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
            
            # Create indexes for better performance
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
            
            # Insert default subscription plans
            cursor.execute("""
            INSERT OR IGNORE INTO subscription_plans 
            (id, plan_type, name, price_monthly, price_annual, features)
            VALUES 
            ('plan_free', 'free', 'Free', 0, 0, '["3 analyses per month", "Basic reports", "PDF download", "Community support"]'),
            ('plan_professional', 'professional', 'Professional', 1499, 14990, '["Unlimited analyses", "Advanced AI insights", "All export formats", "Email support", "Resume templates"]'),
            ('plan_business', 'business', 'Business', 7999, 79990, '["Everything in Professional", "Team collaboration", "Bulk processing", "Analytics dashboard", "API access", "Phone support"]'),
            ('plan_enterprise', 'enterprise', 'Enterprise', 39999, 399990, '["Everything in Business", "Unlimited seats", "SSO integration", "Custom integrations", "Dedicated support", "White-label options"]')
            """)
            
            conn.commit()
            logger.info("Database initialized successfully for Streamlit Cloud")
            return True
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

# Auto-initialize when imported
if __name__ != "__main__":
    init_database_for_streamlit()