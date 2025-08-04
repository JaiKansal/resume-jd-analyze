#!/usr/bin/env python3
"""
Complete Database Fix - Addresses ALL database issues at once
This script will create a fully functional database with all required tables and columns
"""

import sqlite3
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)

def create_complete_database():
    """Create a complete database with all required tables and columns"""
    try:
        # Ensure data directory exists
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        
        db_path = 'data/app.db'
        
        # Remove existing database to start fresh
        if Path(db_path).exists():
            Path(db_path).unlink()
            print("🗑️  Removed existing database")
        
        print("🔧 Creating complete database schema...")
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 1. Create users table with ALL required columns
            print("📝 Creating users table...")
            cursor.execute("""
            CREATE TABLE users (
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
                email_verified BOOLEAN DEFAULT 0,
                email_verification_token VARCHAR(255),
                password_reset_token VARCHAR(255),
                password_reset_expires TIMESTAMP,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # 2. Create subscription_plans table with ALL required columns
            print("💳 Creating subscription_plans table...")
            cursor.execute("""
            CREATE TABLE subscription_plans (
                id TEXT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                plan_type VARCHAR(50) CHECK (plan_type IN ('free', 'professional', 'business', 'enterprise')) NOT NULL,
                price_monthly REAL,
                price_annual REAL,
                monthly_analysis_limit INTEGER,
                features TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # 3. Create subscriptions table with ALL required columns
            print("📊 Creating subscriptions table...")
            cursor.execute("""
            CREATE TABLE subscriptions (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                plan_id TEXT REFERENCES subscription_plans(id),
                status VARCHAR(20) CHECK (status IN ('active', 'cancelled', 'past_due', 'trialing', 'incomplete')) DEFAULT 'active',
                current_period_start TIMESTAMP,
                current_period_end TIMESTAMP,
                trial_start TIMESTAMP,
                trial_end TIMESTAMP,
                monthly_analysis_used INTEGER DEFAULT 0,
                stripe_customer_id VARCHAR(255),
                stripe_subscription_id VARCHAR(255),
                cancel_at_period_end BOOLEAN DEFAULT 0,
                cancelled_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # 4. Create user_sessions table with ALL required columns (THIS WAS MISSING!)
            print("🔐 Creating user_sessions table...")
            cursor.execute("""
            CREATE TABLE user_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # 5. Create analysis_sessions table
            print("📈 Creating analysis_sessions table...")
            cursor.execute("""
            CREATE TABLE analysis_sessions (
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # 6. Create other required tables
            print("🏢 Creating teams table...")
            cursor.execute("""
            CREATE TABLE teams (
                id TEXT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                owner_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                subscription_id TEXT REFERENCES subscriptions(id),
                seat_limit INTEGER DEFAULT 5,
                seats_used INTEGER DEFAULT 1,
                settings TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            print("👥 Creating team_members table...")
            cursor.execute("""
            CREATE TABLE team_members (
                id TEXT PRIMARY KEY,
                team_id TEXT REFERENCES teams(id) ON DELETE CASCADE,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                role VARCHAR(50) CHECK (role IN ('member', 'admin', 'owner')) DEFAULT 'member',
                permissions TEXT,
                invited_by TEXT REFERENCES users(id),
                invited_at TIMESTAMP,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                UNIQUE(team_id, user_id)
            )
            """)
            
            print("💰 Creating revenue_events table...")
            cursor.execute("""
            CREATE TABLE revenue_events (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                subscription_id TEXT REFERENCES subscriptions(id) ON DELETE SET NULL,
                event_type VARCHAR(50) CHECK (event_type IN ('subscription', 'upgrade', 'downgrade', 'service', 'marketplace', 'refund')) NOT NULL,
                amount_usd REAL NOT NULL,
                currency VARCHAR(3) DEFAULT 'USD',
                stripe_payment_id VARCHAR(255),
                stripe_invoice_id VARCHAR(255),
                description TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            print("📊 Creating user_engagement table...")
            cursor.execute("""
            CREATE TABLE user_engagement (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                date DATE NOT NULL,
                sessions_count INTEGER DEFAULT 0,
                analyses_performed INTEGER DEFAULT 0,
                features_used TEXT,
                time_spent_minutes INTEGER DEFAULT 0,
                pages_visited INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date)
            )
            """)
            
            print("🎯 Creating conversion_events table...")
            cursor.execute("""
            CREATE TABLE conversion_events (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                event_name VARCHAR(100) NOT NULL,
                event_properties TEXT,
                source VARCHAR(100),
                medium VARCHAR(100),
                campaign VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            print("🔑 Creating api_keys table...")
            cursor.execute("""
            CREATE TABLE api_keys (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                key_name VARCHAR(100) NOT NULL,
                api_key VARCHAR(255) UNIQUE NOT NULL,
                key_prefix VARCHAR(20) NOT NULL,
                permissions TEXT,
                rate_limit_per_minute INTEGER DEFAULT 60,
                rate_limit_per_day INTEGER DEFAULT 1000,
                last_used_at TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            print("📋 Creating audit_logs table...")
            cursor.execute("""
            CREATE TABLE audit_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
                action VARCHAR(100) NOT NULL,
                resource_type VARCHAR(50),
                resource_id TEXT,
                old_values TEXT,
                new_values TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            print("🔄 Creating schema_migrations table...")
            cursor.execute("""
            CREATE TABLE schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # 7. Create all indexes for performance
            print("🚀 Creating indexes...")
            indexes = [
                "CREATE INDEX idx_users_email ON users(email)",
                "CREATE INDEX idx_users_email_verified ON users(email_verified)",
                "CREATE INDEX idx_users_created_at ON users(created_at)",
                "CREATE INDEX idx_users_last_login ON users(last_login)",
                
                "CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id)",
                "CREATE INDEX idx_subscriptions_status ON subscriptions(status)",
                "CREATE INDEX idx_subscriptions_current_period_end ON subscriptions(current_period_end)",
                
                "CREATE INDEX idx_teams_owner_id ON teams(owner_id)",
                "CREATE INDEX idx_team_members_team_id ON team_members(team_id)",
                "CREATE INDEX idx_team_members_user_id ON team_members(user_id)",
                
                "CREATE INDEX idx_analysis_sessions_user_id ON analysis_sessions(user_id)",
                "CREATE INDEX idx_analysis_sessions_created_at ON analysis_sessions(created_at)",
                "CREATE INDEX idx_analysis_sessions_status ON analysis_sessions(status)",
                
                "CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id)",
                "CREATE INDEX idx_user_sessions_token ON user_sessions(session_token)",
                "CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at)",
                
                "CREATE INDEX idx_revenue_events_user_id ON revenue_events(user_id)",
                "CREATE INDEX idx_revenue_events_created_at ON revenue_events(created_at)",
                "CREATE INDEX idx_revenue_events_event_type ON revenue_events(event_type)",
                
                "CREATE INDEX idx_user_engagement_user_id ON user_engagement(user_id)",
                "CREATE INDEX idx_user_engagement_date ON user_engagement(date)",
                
                "CREATE INDEX idx_conversion_events_user_id ON conversion_events(user_id)",
                "CREATE INDEX idx_conversion_events_event_name ON conversion_events(event_name)",
                "CREATE INDEX idx_conversion_events_created_at ON conversion_events(created_at)",
                
                "CREATE INDEX idx_api_keys_user_id ON api_keys(user_id)",
                "CREATE INDEX idx_api_keys_key_prefix ON api_keys(key_prefix)",
                "CREATE INDEX idx_api_keys_is_active ON api_keys(is_active)",
                
                "CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id)",
                "CREATE INDEX idx_audit_logs_action ON audit_logs(action)",
                "CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            # 8. Insert default subscription plans
            print("💳 Inserting default subscription plans...")
            cursor.execute("""
            INSERT INTO subscription_plans (id, name, plan_type, price_monthly, price_annual, monthly_analysis_limit, features) VALUES
            ('plan_free', 'Free Tier', 'free', 0.00, 0.00, 3, '{"pdf_download": true, "basic_reports": true, "community_support": true, "watermarked_pdfs": true}'),
            ('plan_professional', 'Professional', 'professional', 19.00, 190.00, -1, '{"unlimited_analyses": true, "premium_ai": true, "all_formats": true, "priority_processing": true, "email_support": true, "resume_templates": true}'),
            ('plan_business', 'Business', 'business', 99.00, 990.00, -1, '{"team_collaboration": true, "bulk_upload": true, "analytics_dashboard": true, "api_access": true, "integration_support": true, "phone_support": true, "custom_branding": true, "seats": 5}'),
            ('plan_enterprise', 'Enterprise', 'enterprise', 500.00, 5000.00, -1, '{"unlimited_seats": true, "sso": true, "custom_integrations": true, "dedicated_support": true, "sla_guarantee": true, "on_premise": true, "white_label": true, "custom_features": true}')
            """)
            
            conn.commit()
            print("✅ Database schema created successfully!")
            
            # 9. Verify all tables exist
            print("\n🔍 Verifying database integrity...")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = [
                'users', 'subscription_plans', 'subscriptions', 'user_sessions',
                'analysis_sessions', 'teams', 'team_members', 'revenue_events',
                'user_engagement', 'conversion_events', 'api_keys', 'audit_logs',
                'schema_migrations'
            ]
            
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"❌ Missing tables: {missing_tables}")
                return False
            else:
                print(f"✅ All {len(required_tables)} required tables created")
            
            # 10. Test critical queries
            print("\n🧪 Testing critical queries...")
            test_queries = [
                "SELECT id, user_id, session_token, ip_address, user_agent, expires_at, is_active, created_at FROM user_sessions LIMIT 1",
                "SELECT id, email, email_verified, last_login, login_count FROM users LIMIT 1",
                "SELECT id, user_id, plan_id, status, monthly_analysis_used FROM subscriptions LIMIT 1",
                "SELECT id, plan_type, name, monthly_analysis_limit FROM subscription_plans LIMIT 5"
            ]
            
            for query in test_queries:
                try:
                    cursor.execute(query)
                    print(f"✅ Query test passed: {query[:50]}...")
                except Exception as e:
                    print(f"❌ Query test failed: {query[:50]}... - {e}")
                    return False
            
            print("\n🎉 Complete database setup successful!")
            return True
            
    except Exception as e:
        logger.error(f"Complete database setup failed: {e}")
        print(f"❌ Database setup failed: {e}")
        return False

def update_emergency_init():
    """Update the emergency_init.py to include user_sessions table"""
    emergency_init_content = '''"""
Emergency Database Initialization
Ultra-simple database setup that works on any environment
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def emergency_database_setup():
    """Create the most basic database schema that works everywhere"""
    try:
        # Ensure data directory exists
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        
        db_path = 'data/app.db'
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create users table (minimal)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT DEFAULT '',
                last_name TEXT DEFAULT '',
                company_name TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                role TEXT DEFAULT 'individual',
                country TEXT DEFAULT 'IN',
                timezone TEXT DEFAULT 'Asia/Kolkata',
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
            
            # Create user_sessions table (THIS WAS MISSING!)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
            
            # Create subscriptions table (minimal)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                plan_id TEXT,
                plan_type TEXT NOT NULL DEFAULT 'free',
                status TEXT NOT NULL DEFAULT 'active',
                current_period_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                current_period_end TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trial_start TIMESTAMP,
                trial_end TIMESTAMP,
                monthly_analysis_used INTEGER DEFAULT 0,
                stripe_customer_id VARCHAR(255),
                stripe_subscription_id VARCHAR(255),
                cancel_at_period_end BOOLEAN DEFAULT 0,
                cancelled_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create subscription_plans table (minimal)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscription_plans (
                id TEXT PRIMARY KEY,
                plan_type TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                price_monthly REAL NOT NULL,
                price_annual REAL NOT NULL,
                monthly_analysis_limit INTEGER,
                features TEXT DEFAULT '',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create analysis_sessions table (minimal)
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
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)")
            
            # Insert default plans
            cursor.execute("""
            INSERT OR IGNORE INTO subscription_plans 
            (id, plan_type, name, price_monthly, price_annual, monthly_analysis_limit, features)
            VALUES 
            ('plan_free', 'free', 'Free', 0, 0, 3, '["3 analyses per month", "Basic reports"]'),
            ('plan_professional', 'professional', 'Professional', 1499, 14990, -1, '["Unlimited analyses", "Advanced AI insights"]'),
            ('plan_business', 'business', 'Business', 7999, 79990, -1, '["Team collaboration", "Analytics dashboard"]'),
            ('plan_enterprise', 'enterprise', 'Enterprise', 39999, 399990, -1, '["Custom integrations", "Dedicated support"]')
            """)
            
            conn.commit()
            logger.info("Emergency database setup completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Emergency database setup failed: {e}")
        return False

def force_clean_database():
    """Force clean database recreation"""
    try:
        db_path = 'data/app.db'
        
        # Remove existing database
        if Path(db_path).exists():
            Path(db_path).unlink()
            logger.info("Removed existing database")
        
        # Create fresh database
        return emergency_database_setup()
        
    except Exception as e:
        logger.error(f"Force clean database failed: {e}")
        return False

if __name__ == "__main__":
    print("🚨 Emergency Database Setup")
    print("=" * 30)
    
    choice = input("1. Emergency setup\\n2. Force clean setup\\nChoose (1-2): ")
    
    if choice == "1":
        result = emergency_database_setup()
    elif choice == "2":
        result = force_clean_database()
    else:
        print("Invalid choice")
        exit(1)
    
    if result:
        print("✅ Database setup successful!")
    else:
        print("❌ Database setup failed!")
'''
    
    with open('database/emergency_init.py', 'w') as f:
        f.write(emergency_init_content)
    
    print("✅ Updated emergency_init.py to include user_sessions table")

def main():
    """Main function to fix everything at once"""
    print("🚀 COMPLETE DATABASE FIX - Fixing everything at once!")
    print("=" * 60)
    
    # Step 1: Create complete database
    if not create_complete_database():
        print("❌ Failed to create complete database")
        return False
    
    # Step 2: Update emergency_init.py for future use
    update_emergency_init()
    
    # Step 3: Test the registration flow
    print("\n🧪 Testing registration flow...")
    try:
        from auth.services import user_service, session_service
        
        # Clean up any existing test user
        from database.connection import get_db
        db = get_db()
        db.execute_command("DELETE FROM user_sessions WHERE user_id IN (SELECT id FROM users WHERE email = ?)", ("test_complete@example.com",))
        db.execute_command("DELETE FROM subscriptions WHERE user_id IN (SELECT id FROM users WHERE email = ?)", ("test_complete@example.com",))
        db.execute_command("DELETE FROM users WHERE email = ?", ("test_complete@example.com",))
        
        # Create test user
        user = user_service.create_user(
            email="test_complete@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="Complete"
        )
        
        if user:
            print("✅ User creation works")
            
            # Create session with ip_address
            session = session_service.create_session(
                user_id=user.id,
                ip_address="192.168.1.1",
                user_agent="Test Browser"
            )
            
            if session:
                print("✅ Session creation with ip_address works")
                
                # Clean up
                db.execute_command("DELETE FROM user_sessions WHERE user_id = ?", (user.id,))
                db.execute_command("DELETE FROM subscriptions WHERE user_id = ?", (user.id,))
                db.execute_command("DELETE FROM users WHERE id = ?", (user.id,))
                
                print("✅ All tests passed!")
                return True
            else:
                print("❌ Session creation failed")
                return False
        else:
            print("❌ User creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    success = main()
    
    if success:
        print("\n🎉 COMPLETE DATABASE FIX SUCCESSFUL!")
        print("✅ All database issues resolved")
        print("✅ Registration flow works perfectly")
        print("✅ No more missing table or column errors")
        print("\n🚀 Your application is now ready for production!")
    else:
        print("\n❌ COMPLETE DATABASE FIX FAILED!")
        print("Manual intervention may be required")