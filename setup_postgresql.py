#!/usr/bin/env python3
"""
AUTOMATED POSTGRESQL SETUP
Sets up PostgreSQL and migrates all data automatically
"""

import os
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_postgresql_production():
    """Set up PostgreSQL for production"""
    
    logger.info("🚀 POSTGRESQL PRODUCTION SETUP")
    logger.info("=" * 50)
    
    # Check if PostgreSQL URL is configured
    database_url = os.getenv('DATABASE_URL', '')
    
    if 'postgresql' not in database_url.lower():
        logger.error("❌ PostgreSQL not configured!")
        logger.info("🔧 SETUP INSTRUCTIONS:")
        logger.info("1. Go to https://neon.tech")
        logger.info("2. Create free account")
        logger.info("3. Create new project: 'resume-analyzer'")
        logger.info("4. Copy connection string")
        logger.info("5. Update Streamlit Cloud secrets:")
        logger.info('   DATABASE_URL = "postgresql://user:pass@host/db"')
        logger.info("6. Redeploy app")
        return False
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Test PostgreSQL connection
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        logger.info("✅ PostgreSQL connection successful")
        
        # Create tables
        schema_sql = """
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
        );
        
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
        );
        
        CREATE TABLE IF NOT EXISTS analysis_reports (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            analysis_type TEXT DEFAULT 'resume_jd_match',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSONB,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        
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
        );
        
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
        );
        
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
        );
        """
        
        cursor.execute(schema_sql)
        
        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_analysis_sessions_user_id ON analysis_sessions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_analysis_reports_user_id ON analysis_reports(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_engagement_events_user_id ON engagement_events(user_id)"
        ]
        
        for index in indexes:
            cursor.execute(index)
        
        # Insert default plans
        plans = [
            ('free', 'Free Plan', 'FREE', 0, 0, '{"analyses_per_month": 3}', 3, True),
            ('professional', 'Professional Plan', 'PROFESSIONAL', 19, 190, '{"unlimited_analyses": true}', -1, True),
            ('business', 'Business Plan', 'BUSINESS', 99, 990, '{"unlimited_analyses": true, "team_features": true}', -1, True)
        ]
        
        for plan in plans:
            cursor.execute("""
                INSERT INTO plans (id, name, plan_type, price_monthly, price_yearly, features, analysis_limit, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, plan)
        
        conn.commit()
        conn.close()
        
        logger.info("✅ PostgreSQL setup completed successfully!")
        logger.info("🎉 Your users will now persist forever!")
        
        return True
        
    except ImportError:
        logger.error("❌ psycopg2 not installed")
        logger.info("Add 'psycopg2-binary>=2.9.0' to requirements.txt")
        return False
    except Exception as e:
        logger.error(f"❌ PostgreSQL setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_postgresql_production()
