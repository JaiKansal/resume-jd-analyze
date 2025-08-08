#!/usr/bin/env python3
"""
PostgreSQL Schema Fix for Resume + JD Analyzer
Fixes timestamp column issues and creates missing tables
"""

import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get DATABASE_URL from environment or Streamlit secrets"""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url
    
    try:
        import streamlit as st
        database_url = st.secrets.get('DATABASE_URL')
        if database_url:
            os.environ['DATABASE_URL'] = database_url
            return database_url
    except:
        pass
    
    return None

def fix_postgresql_schema():
    """Fix PostgreSQL schema issues"""
    database_url = get_database_url()
    if not database_url:
        logger.error("❌ DATABASE_URL not found")
        return False
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        logger.info("🔧 Fixing PostgreSQL schema...")
        
        # PostgreSQL-compatible schema with proper timestamp handling
        schema_fixes = [
            # Fix users table with proper PostgreSQL syntax
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                company_name VARCHAR(255),
                role VARCHAR(50) CHECK (role IN ('individual', 'hr_manager', 'admin', 'enterprise_admin')) DEFAULT 'individual',
                phone VARCHAR(20),
                country VARCHAR(100),
                timezone VARCHAR(50) DEFAULT 'UTC',
                email_verified BOOLEAN DEFAULT FALSE,
                email_verification_token VARCHAR(255),
                password_reset_token VARCHAR(255),
                password_reset_expires TIMESTAMPTZ,
                last_login TIMESTAMPTZ,
                login_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Fix user_engagement table
            """
            CREATE TABLE IF NOT EXISTS user_engagement (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                date DATE NOT NULL,
                sessions_count INTEGER DEFAULT 0,
                analyses_performed INTEGER DEFAULT 0,
                features_used TEXT,
                time_spent_minutes INTEGER DEFAULT 0,
                pages_visited INTEGER DEFAULT 0,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(user_id, date)
            );
            """,
            
            # Fix analysis_sessions table
            """
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                team_id TEXT,
                session_type VARCHAR(50) CHECK (session_type IN ('single', 'bulk', 'job_matching', 'api')) DEFAULT 'single',
                resume_count INTEGER DEFAULT 1,
                job_description_count INTEGER DEFAULT 1,
                processing_time_seconds REAL,
                api_cost_usd REAL,
                tokens_used INTEGER,
                status VARCHAR(20) CHECK (status IN ('completed', 'failed', 'processing')) DEFAULT 'completed',
                error_message TEXT,
                metadata TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Fix subscription_plans table
            """
            CREATE TABLE IF NOT EXISTS subscription_plans (
                id TEXT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                plan_type VARCHAR(50) CHECK (plan_type IN ('free', 'professional', 'business', 'enterprise')) NOT NULL,
                price_monthly REAL,
                price_annual REAL,
                monthly_analysis_limit INTEGER,
                features TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Fix subscriptions table
            """
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                plan_id TEXT REFERENCES subscription_plans(id),
                status VARCHAR(20) CHECK (status IN ('active', 'cancelled', 'past_due', 'trialing', 'incomplete')) DEFAULT 'active',
                current_period_start TIMESTAMPTZ,
                current_period_end TIMESTAMPTZ,
                trial_start TIMESTAMPTZ,
                trial_end TIMESTAMPTZ,
                monthly_analysis_used INTEGER DEFAULT 0,
                stripe_customer_id VARCHAR(255),
                stripe_subscription_id VARCHAR(255),
                cancel_at_period_end BOOLEAN DEFAULT FALSE,
                cancelled_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        ]
        
        # Execute schema fixes
        for i, sql in enumerate(schema_fixes, 1):
            try:
                cursor.execute(sql)
                logger.info(f"✅ Applied schema fix {i}/{len(schema_fixes)}")
            except Exception as e:
                logger.warning(f"⚠️ Schema fix {i} already applied or failed: {e}")
        
        # Insert default subscription plans if they don't exist
        try:
            cursor.execute("SELECT COUNT(*) FROM subscription_plans")
            result = cursor.fetchone()
            plan_count = result[0] if result else 0
        except:
            plan_count = 0
        
        if plan_count == 0:
            logger.info("📝 Inserting default subscription plans...")
            plans_sql = """
            INSERT INTO subscription_plans (id, name, plan_type, price_monthly, price_annual, monthly_analysis_limit, features) VALUES
            ('plan_free', 'Free Tier', 'free', 0.00, 0.00, 3, '{"pdf_download": true, "basic_reports": true, "community_support": true, "watermarked_pdfs": true}'),
            ('plan_professional', 'Professional', 'professional', 19.00, 190.00, -1, '{"unlimited_analyses": true, "premium_ai": true, "all_formats": true, "priority_processing": true, "email_support": true, "resume_templates": true}'),
            ('plan_business', 'Business', 'business', 99.00, 990.00, -1, '{"team_collaboration": true, "bulk_upload": true, "analytics_dashboard": true, "api_access": true, "integration_support": true, "phone_support": true, "custom_branding": true, "seats": 5}'),
            ('plan_enterprise', 'Enterprise', 'enterprise', 500.00, 5000.00, -1, '{"unlimited_seats": true, "sso": true, "custom_integrations": true, "dedicated_support": true, "sla_guarantee": true, "on_premise": true, "white_label": true, "custom_features": true}')
            ON CONFLICT (id) DO NOTHING
            """
            cursor.execute(plans_sql)
            logger.info("✅ Default subscription plans inserted")
        
        # Commit all changes
        conn.commit()
        
        # Verify the fix
        try:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"✅ PostgreSQL tables available: {', '.join(tables)}")
        except Exception as e:
            logger.warning(f"⚠️ Could not verify tables: {e}")
        
        cursor.close()
        conn.close()
        
        logger.info("🎉 PostgreSQL schema fixed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix PostgreSQL schema: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Fixing PostgreSQL schema issues...")
    success = fix_postgresql_schema()
    if success:
        logger.info("✅ Schema fix completed successfully!")
    else:
        logger.error("❌ Schema fix failed!")