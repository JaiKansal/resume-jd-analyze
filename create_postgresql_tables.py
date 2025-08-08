#!/usr/bin/env python3
"""
Create PostgreSQL tables with proper schema
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_postgresql_tables():
    """Create all required tables in PostgreSQL"""
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url or 'postgresql' not in database_url:
        logger.error("PostgreSQL DATABASE_URL not configured")
        return False
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                company_name TEXT,
                role TEXT DEFAULT 'individual',
                phone TEXT,
                country TEXT,
                timezone TEXT DEFAULT 'UTC',
                email_verified BOOLEAN DEFAULT FALSE,
                email_verification_token TEXT,
                password_reset_token TEXT,
                password_reset_expires TIMESTAMP,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create analysis_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                resume_filename TEXT,
                score INTEGER,
                match_category TEXT,
                analysis_result TEXT,
                processing_time_seconds REAL,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Create other required tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                plan_id TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                current_period_start TIMESTAMP,
                current_period_end TIMESTAMP,
                cancel_at_period_end BOOLEAN DEFAULT FALSE,
                canceled_at TIMESTAMP,
                trial_start TIMESTAMP,
                trial_end TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                plan_type TEXT NOT NULL,
                price_monthly DECIMAL(10,2),
                price_yearly DECIMAL(10,2),
                features JSONB,
                analysis_limit INTEGER,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS engagement_events (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                page_path TEXT,
                session_id TEXT,
                parameters TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Insert default plans
        cursor.execute("""
            INSERT INTO plans (id, name, plan_type, price_monthly, price_yearly, features, analysis_limit, is_active)
            VALUES 
                ('free', 'Free Plan', 'FREE', 0, 0, '{"analyses_per_month": 3}', 3, TRUE),
                ('professional', 'Professional Plan', 'PROFESSIONAL', 19, 190, '{"unlimited_analyses": true}', -1, TRUE),
                ('business', 'Business Plan', 'BUSINESS', 99, 990, '{"unlimited_analyses": true, "team_features": true}', -1, TRUE)
            ON CONFLICT (id) DO NOTHING
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_sessions_user_id ON analysis_sessions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_engagement_events_user_id ON engagement_events(user_id)")
        
        conn.commit()
        conn.close()
        
        logger.info("✅ PostgreSQL tables created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create PostgreSQL tables: {e}")
        return False

if __name__ == "__main__":
    create_postgresql_tables()
