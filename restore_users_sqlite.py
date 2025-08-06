#!/usr/bin/env python3
"""
Restore users to SQLite database (temporary solution)
This will work until the next deployment
"""

import sqlite3
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def restore_users_to_sqlite():
    """Restore users from backup to SQLite"""
    
    try:
        # Load backup data
        with open('user_data_backup.json', 'r') as f:
            backup_data = json.load(f)
        
        logger.info(f"📦 Loading backup from {backup_data['export_date']}")
        
        # Connect to SQLite
        conn = sqlite3.connect('data/app.db')
        cursor = conn.cursor()
        
        # Restore users
        users = backup_data['users']
        for user in users:
            # Handle different name formats
            full_name = user.get('full_name')
            if not full_name:
                first_name = user.get('first_name', '')
                last_name = user.get('last_name', '')
                full_name = f"{first_name} {last_name}".strip()
            
            cursor.execute("""
                INSERT OR REPLACE INTO users (
                    id, email, password_hash, first_name, last_name, company_name,
                    role, phone, country, timezone, email_verified, 
                    email_verification_token, last_login, login_count,
                    is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user['id'], user['email'], user['password_hash'],
                user.get('first_name', ''), user.get('last_name', ''),
                user.get('company_name'), user.get('role', 'individual'),
                user.get('phone'), user.get('country'), user.get('timezone', 'UTC'),
                user.get('email_verified', 0), user.get('email_verification_token'),
                user.get('last_login'), user.get('login_count', 0),
                user.get('is_active', 1), user['created_at'], user.get('updated_at')
            ))
        
        logger.info(f"✅ Restored {len(users)} users")
        
        # Restore analysis sessions
        sessions = backup_data['analysis_sessions']
        for session in sessions:
            cursor.execute("""
                INSERT OR REPLACE INTO analysis_sessions (
                    id, user_id, resume_filename, score, match_category,
                    created_at, analysis_result, processing_time_seconds, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session['id'], session['user_id'], session['resume_filename'],
                session['score'], session['match_category'], session['created_at'],
                session.get('analysis_result', ''), session.get('processing_time_seconds', 0),
                session.get('status', 'completed')
            ))
        
        logger.info(f"✅ Restored {len(sessions)} analysis sessions")
        
        # Restore subscriptions if they exist
        subscriptions = backup_data.get('subscriptions', [])
        if subscriptions:
            for sub in subscriptions:
                cursor.execute("""
                    INSERT OR REPLACE INTO subscriptions (
                        id, user_id, plan_id, status, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    sub['id'], sub['user_id'], sub['plan_id'],
                    sub['status'], sub['created_at']
                ))
            
            logger.info(f"✅ Restored {len(subscriptions)} subscriptions")
        
        conn.commit()
        conn.close()
        
        logger.info("🎉 All users and data restored successfully!")
        logger.info("⚠️  WARNING: This is temporary - data will be lost on next deployment")
        logger.info("💡 Set up PostgreSQL for permanent solution")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Restore failed: {e}")
        return False

def verify_restore():
    """Verify that users were restored correctly"""
    
    try:
        conn = sqlite3.connect('data/app.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM analysis_sessions")
        session_count = cursor.fetchone()[0]
        
        conn.close()
        
        logger.info(f"📊 Verification: {user_count} users, {session_count} sessions in database")
        
        if user_count > 0:
            logger.info("✅ Users successfully restored!")
            return True
        else:
            logger.error("❌ No users found after restore")
            return False
            
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return False

def main():
    """Main restore process"""
    logger.info("🔄 Restoring users from backup...")
    
    if restore_users_to_sqlite():
        if verify_restore():
            logger.info("\n🎉 SUCCESS! Your users are back!")
            logger.info("🔑 Users can now log in again")
            logger.info("📊 Analysis history is restored")
            logger.info("\n⚠️  IMPORTANT: Set up PostgreSQL to prevent this happening again!")
        else:
            logger.error("❌ Restore verification failed")
    else:
        logger.error("❌ Restore process failed")

if __name__ == "__main__":
    main()