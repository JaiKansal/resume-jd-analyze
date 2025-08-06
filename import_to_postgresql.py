#!/usr/bin/env python3
"""
Import users and data into PostgreSQL database
Run this AFTER setting up PostgreSQL and updating DATABASE_URL
"""

import json
import psycopg2
import os
from datetime import datetime

def import_to_postgresql():
    """Import backup data to PostgreSQL"""
    
    # Load backup data
    try:
        with open('user_data_backup.json', 'r') as f:
            backup_data = json.load(f)
    except FileNotFoundError:
        print("❌ Backup file not found. Run export first.")
        return False
    
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        print("✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False
    
    try:
        # Import users
        users = backup_data['users']
        for user in users:
            cursor.execute("""
                INSERT INTO users (id, email, password_hash, full_name, created_at, is_active, role, email_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                user['id'], user['email'], user['password_hash'], 
                user['full_name'], user['created_at'], user.get('is_active', True),
                user.get('role', 'user'), user.get('email_verified', False)
            ))
        
        print(f"✅ Imported {len(users)} users")
        
        # Import analysis sessions
        sessions = backup_data['analysis_sessions']
        for session in sessions:
            cursor.execute("""
                INSERT INTO analysis_sessions (
                    id, user_id, resume_filename, score, match_category, 
                    created_at, analysis_result, processing_time_seconds, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                session['id'], session['user_id'], session['resume_filename'],
                session['score'], session['match_category'], session['created_at'],
                session.get('analysis_result', ''), session.get('processing_time_seconds', 0),
                session.get('status', 'completed')
            ))
        
        print(f"✅ Imported {len(sessions)} analysis sessions")
        
        # Import subscriptions if they exist
        subscriptions = backup_data.get('subscriptions', [])
        if subscriptions:
            for sub in subscriptions:
                cursor.execute("""
                    INSERT INTO subscriptions (id, user_id, plan_id, status, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    sub['id'], sub['user_id'], sub['plan_id'], 
                    sub['status'], sub['created_at']
                ))
            
            print(f"✅ Imported {len(subscriptions)} subscriptions")
        
        conn.commit()
        conn.close()
        
        print("🎉 Migration completed successfully!")
        print("🗑️  You can now delete user_data_backup.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        conn.rollback()
        conn.close()
        return False

if __name__ == "__main__":
    import_to_postgresql()
