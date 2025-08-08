#!/usr/bin/env python3
"""
Check database consistency and fix subscription issues
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

def check_database_consistency():
    """Check database tables and fix subscription issues"""
    database_url = get_database_url()
    if not database_url:
        logger.error("❌ DATABASE_URL not found")
        return False
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        logger.info("🔍 Checking database consistency...")
        
        # 1. Check all tables
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
        tables = [row['table_name'] for row in cursor.fetchall()]
        logger.info(f"📊 Available tables: {tables}")
        
        # 2. Check users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        logger.info(f"👥 Users: {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT id, email, role FROM users LIMIT 5")
            users = cursor.fetchall()
            for user in users:
                logger.info(f"  - {user['email']} (ID: {user['id']}, Role: {user['role']})")
        
        # 3. Check subscription_plans
        cursor.execute("SELECT COUNT(*) as count FROM subscription_plans")
        plan_count = cursor.fetchone()['count']
        logger.info(f"📋 Subscription plans: {plan_count}")
        
        if plan_count > 0:
            cursor.execute("SELECT id, name, plan_type, price_monthly FROM subscription_plans")
            plans = cursor.fetchall()
            for plan in plans:
                logger.info(f"  - {plan['name']} ({plan['id']}) - ${plan['price_monthly']}/month")
        else:
            logger.warning("⚠️ No subscription plans found!")
        
        # 4. Check subscriptions
        cursor.execute("SELECT COUNT(*) as count FROM subscriptions")
        subscription_count = cursor.fetchone()['count']
        logger.info(f"💳 Subscriptions: {subscription_count}")
        
        if subscription_count > 0:
            cursor.execute("""
                SELECT s.id, s.user_id, s.plan_id, s.status, u.email, sp.name as plan_name
                FROM subscriptions s
                JOIN users u ON s.user_id = u.id
                LEFT JOIN subscription_plans sp ON s.plan_id = sp.id
                LIMIT 10
            """)
            subscriptions = cursor.fetchall()
            for sub in subscriptions:
                logger.info(f"  - {sub['email']}: {sub['plan_name']} ({sub['status']})")
        else:
            logger.warning("⚠️ No subscriptions found!")
        
        # 5. Fix missing subscriptions for existing users
        if user_count > 0 and subscription_count == 0:
            logger.info("🔧 Creating missing subscriptions for existing users...")
            
            # Get all users without subscriptions
            cursor.execute("""
                SELECT u.id, u.email 
                FROM users u 
                LEFT JOIN subscriptions s ON u.id = s.user_id 
                WHERE s.id IS NULL
            """)
            users_without_subs = cursor.fetchall()
            
            for user in users_without_subs:
                # Create free subscription for each user
                import uuid
                from datetime import datetime, timedelta
                
                subscription_id = str(uuid.uuid4())
                current_time = datetime.utcnow()
                
                cursor.execute("""
                    INSERT INTO subscriptions (
                        id, user_id, plan_id, status, current_period_start, 
                        current_period_end, monthly_analysis_used, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    subscription_id, user['id'], 'plan_free', 'active',
                    current_time, current_time + timedelta(days=30),
                    0, current_time, current_time
                ))
                
                logger.info(f"✅ Created free subscription for {user['email']}")
            
            conn.commit()
            logger.info(f"🎉 Created {len(users_without_subs)} missing subscriptions!")
        
        # 6. Verify final state
        cursor.execute("SELECT COUNT(*) as count FROM subscriptions")
        final_subscription_count = cursor.fetchone()['count']
        logger.info(f"✅ Final subscription count: {final_subscription_count}")
        
        # 7. Check for any other missing tables or data
        required_tables = ['users', 'subscription_plans', 'subscriptions', 'user_sessions', 'analysis_sessions']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            logger.warning(f"⚠️ Missing required tables: {missing_tables}")
        else:
            logger.info("✅ All required tables present")
        
        cursor.close()
        conn.close()
        
        logger.info("🎉 Database consistency check completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database consistency check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("🚀 Checking database consistency and fixing subscription issues...")
    success = check_database_consistency()
    if success:
        logger.info("✅ Database consistency check completed!")
    else:
        logger.error("❌ Database consistency check failed!")