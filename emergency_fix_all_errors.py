#!/usr/bin/env python3
"""
EMERGENCY FIX - Fix all critical app errors immediately
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def fix_database_schema():
    """Fix missing database tables and columns"""
    print("🔧 Fixing database schema...")
    
    db_path = 'data/app.db'
    Path('data').mkdir(exist_ok=True)
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create missing engagement_events table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS engagement_events (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                page_path TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create missing analytics_events table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_events (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                event_name TEXT NOT NULL,
                event_properties TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create missing payment_records table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_records (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'INR',
                status TEXT NOT NULL,
                payment_method TEXT,
                razorpay_payment_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create missing usage_tracking table
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
            
            # Add indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_engagement_events_user_id ON engagement_events(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON analytics_events(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_records_user_id ON payment_records(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id)")
            
            conn.commit()
            print("✅ Database schema fixed")
            return True
            
    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        return False

def fix_app_py_null_checks():
    """Fix null pointer exceptions in app.py"""
    print("🔧 Fixing app.py null checks...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Fix subscription null checks
        fixes = [
            # Fix dashboard subscription check
            (
                'if subscription.plan.monthly_analysis_limit != -1:',
                'if subscription and subscription.plan and subscription.plan.monthly_analysis_limit != -1:'
            ),
            # Fix bulk analysis subscription check
            (
                'if not subscription.plan.has_feature(\'bulk_upload\'):',
                'if not subscription or not subscription.plan or not hasattr(subscription.plan, \'has_feature\') or not subscription.plan.has_feature(\'bulk_upload\'):'
            ),
            # Fix subscription plan access
            (
                'subscription.plan.monthly_analysis_limit',
                'subscription.plan.monthly_analysis_limit if subscription and subscription.plan else 0'
            ),
            # Fix subscription plan name access
            (
                'subscription.plan.name',
                'subscription.plan.name if subscription and subscription.plan else "Free"'
            )
        ]
        
        for old, new in fixes:
            if old in content:
                content = content.replace(old, new)
                print(f"✅ Fixed: {old[:50]}...")
        
        with open('app.py', 'w') as f:
            f.write(content)
        
        print("✅ App.py null checks fixed")
        return True
        
    except Exception as e:
        print(f"❌ App.py fix failed: {e}")
        return False

def fix_registration_py_null_checks():
    """Fix null pointer exceptions in registration.py"""
    print("🔧 Fixing registration.py null checks...")
    
    try:
        with open('auth/registration.py', 'r') as f:
            content = f.read()
        
        # Fix user null checks
        fixes = [
            # Fix user first_name access
            (
                'st.markdown(f"Hi **{user.first_name}**! Your account has been',
                'st.markdown(f"Hi **{user.first_name if user and user.first_name else \'User\'}**! Your account has been'
            ),
            # Fix user email_verified access
            (
                'if not user.email_verified:',
                'if user and not getattr(user, \'email_verified\', False):'
            ),
            # Fix user email access
            (
                'st.markdown(f"We\'ve sent a verification email to **{user.email}**',
                'st.markdown(f"We\'ve sent a verification email to **{user.email if user and user.email else \'your email\'}**'
            )
        ]
        
        for old, new in fixes:
            if old in content:
                content = content.replace(old, new)
                print(f"✅ Fixed: {old[:50]}...")
        
        with open('auth/registration.py', 'w') as f:
            f.write(content)
        
        print("✅ Registration.py null checks fixed")
        return True
        
    except Exception as e:
        print(f"❌ Registration.py fix failed: {e}")
        return False

def add_subscription_fallback():
    """Add subscription fallback logic"""
    print("🔧 Adding subscription fallback logic...")
    
    subscription_fallback = '''
def get_subscription_with_fallback(user_id):
    """Get subscription with fallback to free plan"""
    try:
        subscription = subscription_service.get_user_subscription(user_id)
        if subscription:
            return subscription
        
        # Create default free subscription if none exists
        free_plan = subscription_service.get_plan_by_type(PlanType.FREE)
        if free_plan:
            return subscription_service.create_subscription(user_id, free_plan.id)
        
        # Return mock subscription as last resort
        from auth.models import Subscription, SubscriptionPlan, SubscriptionStatus, PlanType
        mock_plan = SubscriptionPlan(
            id='plan_free',
            name='Free',
            plan_type=PlanType.FREE,
            price_monthly=0,
            price_annual=0,
            monthly_analysis_limit=3,
            features={},
            is_active=True
        )
        mock_subscription = Subscription(
            id='mock_sub',
            user_id=user_id,
            plan_id='plan_free',
            status=SubscriptionStatus.ACTIVE,
            monthly_analysis_used=0
        )
        mock_subscription.plan = mock_plan
        return mock_subscription
        
    except Exception as e:
        logger.error(f"Failed to get subscription: {e}")
        return None
'''
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Add the fallback function after imports
        if 'def get_subscription_with_fallback' not in content:
            # Find a good place to insert (after imports, before main functions)
            insert_point = content.find('def initialize_session_state():')
            if insert_point != -1:
                content = content[:insert_point] + subscription_fallback + '\n\n' + content[insert_point:]
                
                # Replace subscription service calls with fallback
                content = content.replace(
                    'subscription = subscription_service.get_user_subscription(user.id)',
                    'subscription = get_subscription_with_fallback(user.id)'
                )
                
                with open('app.py', 'w') as f:
                    f.write(content)
                
                print("✅ Subscription fallback added")
                return True
        
        print("✅ Subscription fallback already exists")
        return True
        
    except Exception as e:
        print(f"❌ Subscription fallback failed: {e}")
        return False

def fix_emergency_init():
    """Fix emergency_init.py to include all required tables"""
    print("🔧 Fixing emergency_init.py...")
    
    emergency_init_content = '''"""
Emergency Database Initialization - COMPLETE VERSION
Ultra-simple database setup that works on any environment with ALL required tables
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
                processing_time_seconds REAL DEFAULT 0,
                api_cost_usd REAL DEFAULT 0,
                tokens_used INTEGER DEFAULT 0,
                status TEXT DEFAULT 'completed',
                session_type TEXT DEFAULT 'single',
                metadata TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create engagement_events table (MISSING!)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS engagement_events (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                page_path TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create analytics_events table (MISSING!)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_events (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                event_name TEXT NOT NULL,
                event_properties TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create payment_records table (MISSING!)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_records (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'INR',
                status TEXT NOT NULL,
                payment_method TEXT,
                razorpay_payment_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create usage_tracking table (MISSING!)
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
            
            # Create report_downloads table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS report_downloads (
                id TEXT PRIMARY KEY,
                analysis_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                report_type TEXT NOT NULL,
                report_format TEXT NOT NULL,
                download_count INTEGER DEFAULT 1,
                first_downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_engagement_events_user_id ON engagement_events(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON analytics_events(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_records_user_id ON payment_records(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_report_downloads_user_id ON report_downloads(user_id)")
            
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
    
    try:
        with open('database/emergency_init.py', 'w') as f:
            f.write(emergency_init_content)
        
        print("✅ Emergency init fixed")
        return True
        
    except Exception as e:
        print(f"❌ Emergency init fix failed: {e}")
        return False

def main():
    """Main emergency fix function"""
    print("🚨 EMERGENCY FIX - Fixing all critical errors")
    print("=" * 50)
    
    fixes = [
        ("Database Schema", fix_database_schema),
        ("App.py Null Checks", fix_app_py_null_checks),
        ("Registration.py Null Checks", fix_registration_py_null_checks),
        ("Subscription Fallback", add_subscription_fallback),
        ("Emergency Init", fix_emergency_init)
    ]
    
    success_count = 0
    
    for fix_name, fix_func in fixes:
        print(f"\\n🔧 {fix_name}...")
        try:
            if fix_func():
                success_count += 1
                print(f"✅ {fix_name}: SUCCESS")
            else:
                print(f"❌ {fix_name}: FAILED")
        except Exception as e:
            print(f"❌ {fix_name}: ERROR - {e}")
    
    print(f"\\n{'='*50}")
    print(f"EMERGENCY FIX RESULTS: {success_count}/{len(fixes)} fixes applied")
    
    if success_count == len(fixes):
        print("🎉 ALL EMERGENCY FIXES APPLIED SUCCESSFULLY!")
        print("\\n✅ Database schema complete with all required tables")
        print("✅ Null pointer exceptions fixed")
        print("✅ Subscription fallback logic added")
        print("✅ Emergency init updated")
        print("\\n🚀 Your app should now work without crashes!")
    else:
        print(f"⚠️ {len(fixes) - success_count} fixes failed")
        print("\\nSome issues may persist. Check the errors above.")
    
    return success_count == len(fixes)

if __name__ == "__main__":
    main()