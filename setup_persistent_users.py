#!/usr/bin/env python3
"""
Set up persistent user storage using PostgreSQL
This will solve the user loss problem permanently
"""

import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_neon_setup_guide():
    """Create step-by-step guide for setting up Neon PostgreSQL"""
    logger.info("📋 Creating Neon PostgreSQL setup guide...")
    
    guide = """# 🗄️ PERMANENT USER STORAGE SETUP

## 🚨 PROBLEM: Users Lost on Every Deployment

**Current Issue:**
- SQLite database is wiped every time you push changes
- Users can't login after deployments
- Can't signup with same email (database conflicts)

## ✅ SOLUTION: PostgreSQL with Neon (Free)

### Step 1: Create Neon Database (2 minutes)

1. **Go to https://neon.tech**
2. **Sign up** with GitHub (free)
3. **Create new project**:
   - Project name: `resume-analyzer`
   - Database name: `resume_analyzer`
   - Region: Choose closest to you
4. **Copy the connection string** (looks like):
   ```
   postgresql://username:password@hostname.neon.tech/resume_analyzer?sslmode=require
   ```

### Step 2: Update Streamlit Cloud Secrets (1 minute)

1. **Go to your Streamlit Cloud app**
2. **Click Settings** (gear icon)
3. **Go to Secrets tab**
4. **Replace the DATABASE_URL line** with:
   ```toml
   DATABASE_URL = "postgresql://your-connection-string-here"
   ```
5. **Save secrets**

### Step 3: Deploy and Migrate Users (2 minutes)

1. **Your app will redeploy automatically**
2. **PostgreSQL tables will be created**
3. **Users will persist forever**

## 🎯 IMMEDIATE TEMPORARY FIX

If you want to test right now before setting up PostgreSQL:

1. **Clear browser cache/cookies**
2. **Try registering with a NEW email address**
3. **This will work until next deployment**

## 📞 Need Help?

If you need help with Neon setup:
1. The connection string format is: `postgresql://user:pass@host/db`
2. Make sure to include `?sslmode=require` at the end
3. Test the connection in Neon's SQL editor first

## 🎉 After Setup

Once PostgreSQL is configured:
- ✅ Users persist forever
- ✅ No more login issues after deployments  
- ✅ Analysis history preserved
- ✅ Subscription data maintained
- ✅ Production-ready user management

**This is the ONLY way to solve the user persistence problem on Streamlit Cloud.**
"""
    
    with open('NEON_POSTGRESQL_SETUP.md', 'w') as f:
        f.write(guide)
    
    logger.info("✅ Created Neon setup guide")
    return True

def create_quick_user_fix():
    """Create a quick fix for immediate testing"""
    logger.info("🔧 Creating quick user fix for immediate testing...")
    
    quick_fix = """#!/usr/bin/env python3
'''
Quick fix to clear user conflicts and allow immediate testing
Run this if you can't login or signup
'''

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_user_conflicts():
    '''Clear any user conflicts in the database'''
    try:
        conn = sqlite3.connect('data/app.db')
        cursor = conn.cursor()
        
        # Get current user count
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        logger.info(f"Current users in database: {user_count}")
        
        # Show existing users (email only for privacy)
        cursor.execute("SELECT email, created_at FROM users ORDER BY created_at DESC LIMIT 5")
        users = cursor.fetchall()
        
        if users:
            logger.info("Recent users:")
            for email, created_at in users:
                logger.info(f"  - {email} (created: {created_at[:10]})")
        
        # Option to clear all users (for testing)
        print("\\n🚨 WARNING: This will delete ALL users!")
        print("Only do this for testing purposes.")
        confirm = input("Type 'DELETE ALL USERS' to confirm: ")
        
        if confirm == "DELETE ALL USERS":
            cursor.execute("DELETE FROM users")
            cursor.execute("DELETE FROM analysis_sessions")
            cursor.execute("DELETE FROM subscriptions")
            conn.commit()
            logger.info("✅ All users deleted - you can now register fresh")
        else:
            logger.info("❌ User deletion cancelled")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    clear_user_conflicts()
'''
    
    with open('quick_user_fix.py', 'w') as f:
        f.write(quick_fix)
    
    logger.info("✅ Created quick user fix script")
    return True

def create_postgresql_migration_script():
    """Create the PostgreSQL migration script"""
    logger.info("🔧 Creating PostgreSQL migration script...")
    
    migration_script = """#!/usr/bin/env python3
'''
Migrate users from SQLite to PostgreSQL
Run this after setting up Neon PostgreSQL
'''

import os
import sqlite3
import psycopg2
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_to_postgresql():
    '''Migrate all data from SQLite to PostgreSQL'''
    
    # Check if PostgreSQL URL is configured
    database_url = os.getenv('DATABASE_URL')
    if not database_url or 'postgresql' not in database_url:
        logger.error("❌ PostgreSQL DATABASE_URL not configured")
        logger.info("💡 Set DATABASE_URL environment variable with PostgreSQL connection string")
        return False
    
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect('data/app.db')
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to PostgreSQL
        pg_conn = psycopg2.connect(database_url)
        pg_cursor = pg_conn.cursor()
        
        logger.info("✅ Connected to both databases")
        
        # Migrate users
        sqlite_cursor.execute("SELECT * FROM users")
        users = sqlite_cursor.fetchall()
        
        for user in users:
            try:
                pg_cursor.execute("""
                    INSERT INTO users (
                        id, email, password_hash, first_name, last_name, 
                        company_name, role, phone, country, timezone,
                        email_verified, email_verification_token, 
                        last_login, login_count, is_active, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    user['id'], user['email'], user['password_hash'],
                    user['first_name'], user['last_name'], user['company_name'],
                    user['role'], user['phone'], user['country'], user['timezone'],
                    user['email_verified'], user['email_verification_token'],
                    user['last_login'], user['login_count'], user['is_active'],
                    user['created_at'], user['updated_at']
                ))
            except Exception as e:
                logger.warning(f"Failed to migrate user {user['email']}: {e}")
        
        logger.info(f"✅ Migrated {len(users)} users")
        
        # Migrate analysis sessions
        sqlite_cursor.execute("SELECT * FROM analysis_sessions")
        sessions = sqlite_cursor.fetchall()
        
        for session in sessions:
            try:
                pg_cursor.execute("""
                    INSERT INTO analysis_sessions (
                        id, user_id, resume_filename, score, match_category,
                        analysis_result, processing_time_seconds, status, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    session['id'], session['user_id'], session['resume_filename'],
                    session['score'], session['match_category'], session['analysis_result'],
                    session.get('processing_time_seconds', 0), 
                    session.get('status', 'completed'), session['created_at']
                ))
            except Exception as e:
                logger.warning(f"Failed to migrate session {session['id']}: {e}")
        
        logger.info(f"✅ Migrated {len(sessions)} analysis sessions")
        
        # Commit changes
        pg_conn.commit()
        
        # Close connections
        pg_conn.close()
        sqlite_conn.close()
        
        logger.info("🎉 Migration completed successfully!")
        logger.info("🔄 Your users will now persist forever!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    migrate_to_postgresql()
'''
    
    with open('migrate_to_postgresql.py', 'w') as f:
        f.write(migration_script)
    
    logger.info("✅ Created PostgreSQL migration script")
    return True

def main():
    """Create all user persistence solutions"""
    logger.info("🚀 Creating user persistence solutions...")
    
    solutions = [
        ("Neon PostgreSQL setup guide", create_neon_setup_guide),
        ("Quick user fix script", create_quick_user_fix),
        ("PostgreSQL migration script", create_postgresql_migration_script)
    ]
    
    success_count = 0
    for solution_name, solution_func in solutions:
        logger.info(f"\n--- {solution_name} ---")
        if solution_func():
            success_count += 1
    
    logger.info(f"\n✅ Created {success_count}/{len(solutions)} solutions")
    
    logger.info("\n🎯 IMMEDIATE OPTIONS:")
    logger.info("1. 🚀 PERMANENT FIX: Follow NEON_POSTGRESQL_SETUP.md (recommended)")
    logger.info("2. 🧪 QUICK TEST: Run quick_user_fix.py to clear conflicts")
    logger.info("3. 📊 MIGRATE: Run migrate_to_postgresql.py after PostgreSQL setup")
    
    logger.info("\n💡 The PostgreSQL setup is the ONLY permanent solution!")
    
    return success_count == len(solutions)

if __name__ == "__main__":
    main()