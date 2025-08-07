#!/usr/bin/env python3
"""
USER RECOVERY SYSTEM - Restore users from any backup
"""

import sqlite3
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def restore_users_from_backup():
    """Restore users from the most recent backup"""
    
    # Look for backup files
    backup_files = [
        'user_data_backup.json',
        'users_backup.json',
        'database_backup.json'
    ]
    
    backup_data = None
    for backup_file in backup_files:
        if Path(backup_file).exists():
            try:
                with open(backup_file, 'r') as f:
                    backup_data = json.load(f)
                logger.info(f"✅ Found backup: {backup_file}")
                break
            except:
                continue
    
    if not backup_data:
        logger.error("❌ No backup files found")
        return False
    
    # Restore to database
    try:
        conn = sqlite3.connect('data/app.db')
        cursor = conn.cursor()
        
        # Clear existing users to avoid conflicts
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM analysis_sessions")
        cursor.execute("DELETE FROM subscriptions")
        
        # Restore users
        users = backup_data.get('users', [])
        for user in users:
            cursor.execute("""
                INSERT INTO users (
                    id, email, password_hash, first_name, last_name,
                    company_name, role, phone, country, timezone,
                    email_verified, email_verification_token,
                    last_login, login_count, is_active, created_at, updated_at
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
        
        # Restore analysis sessions
        sessions = backup_data.get('analysis_sessions', [])
        for session in sessions:
            cursor.execute("""
                INSERT INTO analysis_sessions (
                    id, user_id, resume_filename, score, match_category,
                    analysis_result, processing_time_seconds, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session['id'], session['user_id'], session['resume_filename'],
                session['score'], session['match_category'], session.get('analysis_result', ''),
                session.get('processing_time_seconds', 0), session.get('status', 'completed'),
                session['created_at']
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Restored {len(users)} users and {len(sessions)} sessions")
        return True
        
    except Exception as e:
        logger.error(f"❌ Restore failed: {e}")
        return False

if __name__ == "__main__":
    restore_users_from_backup()
