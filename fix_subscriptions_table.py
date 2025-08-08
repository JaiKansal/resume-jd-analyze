#!/usr/bin/env python3
"""
Fix subscriptions table by adding missing columns
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

def fix_subscriptions_table():
    """Add missing columns to subscriptions table"""
    database_url = get_database_url()
    if not database_url:
        logger.error("❌ DATABASE_URL not found")
        return False
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        logger.info("🔧 Fixing subscriptions table...")
        
        # Check current columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'subscriptions'
        """)
        existing_columns = [row['column_name'] for row in cursor.fetchall()]
        logger.info(f"Existing columns: {existing_columns}")
        
        # Add missing columns
        columns_to_add = [
            ("monthly_analysis_used", "INTEGER DEFAULT 0"),
            ("stripe_customer_id", "VARCHAR(255)"),
            ("stripe_subscription_id", "VARCHAR(255)")
        ]
        
        for column_name, column_definition in columns_to_add:
            if column_name not in existing_columns:
                try:
                    alter_query = f"ALTER TABLE subscriptions ADD COLUMN {column_name} {column_definition}"
                    cursor.execute(alter_query)
                    logger.info(f"✅ Added column: {column_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not add column {column_name}: {e}")
            else:
                logger.info(f"✅ Column {column_name} already exists")
        
        # Commit changes
        conn.commit()
        
        # Now create missing subscriptions for users
        logger.info("🔧 Creating missing subscriptions for existing users...")
        
        # Get users without subscriptions
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
            current_time = datetime.now()
            
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
        
        # Verify final state
        cursor.execute("SELECT COUNT(*) as count FROM subscriptions")
        subscription_count = cursor.fetchone()['count']
        logger.info(f"✅ Final subscription count: {subscription_count}")
        
        # Show subscription details
        cursor.execute("""
            SELECT s.id, u.email, sp.name as plan_name, s.status
            FROM subscriptions s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN subscription_plans sp ON s.plan_id = sp.id
        """)
        subscriptions = cursor.fetchall()
        
        logger.info("📋 Current subscriptions:")
        for sub in subscriptions:
            logger.info(f"  - {sub['email']}: {sub['plan_name']} ({sub['status']})")
        
        cursor.close()
        conn.close()
        
        logger.info("🎉 Subscriptions table fixed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix subscriptions table: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("🚀 Fixing subscriptions table and creating missing subscriptions...")
    success = fix_subscriptions_table()
    if success:
        logger.info("✅ Subscriptions fix completed successfully!")
    else:
        logger.error("❌ Subscriptions fix failed!")