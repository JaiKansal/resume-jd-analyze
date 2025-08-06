#!/usr/bin/env python3
"""
Quick setup script to migrate to Neon PostgreSQL
Run this BEFORE your next deployment to preserve users
"""

import sqlite3
import os
import json
from datetime import datetime

def export_current_users():
    """Export current users and data to JSON for backup"""
    print("📦 Exporting current users and data...")
    
    try:
        conn = sqlite3.connect('data/app.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Export users
        cursor.execute("SELECT * FROM users")
        users = [dict(row) for row in cursor.fetchall()]
        
        # Export analysis sessions
        cursor.execute("SELECT * FROM analysis_sessions")
        sessions = [dict(row) for row in cursor.fetchall()]
        
        # Export subscriptions if they exist
        try:
            cursor.execute("SELECT * FROM subscriptions")
            subscriptions = [dict(row) for row in cursor.fetchall()]
        except:
            subscriptions = []
        
        conn.close()
        
        # Save to backup file
        backup_data = {
            'export_date': datetime.now().isoformat(),
            'users': users,
            'analysis_sessions': sessions,
            'subscriptions': subscriptions
        }
        
        with open('user_data_backup.json', 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        print(f"✅ Exported {len(users)} users and {len(sessions)} analysis sessions")
        print("📁 Backup saved to: user_data_backup.json")
        
        return backup_data
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return None

def create_postgresql_migration_script():
    """Create a script to import data into PostgreSQL"""
    
    migration_script = '''#!/usr/bin/env python3
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
'''
    
    with open('import_to_postgresql.py', 'w') as f:
        f.write(migration_script)
    
    print("✅ Created import_to_postgresql.py script")

def main():
    """Main setup process"""
    print("🚀 Quick PostgreSQL Migration Setup")
    print("=" * 50)
    
    # Step 1: Export current data
    backup_data = export_current_users()
    if not backup_data:
        print("❌ Failed to export data. Aborting.")
        return
    
    # Step 2: Create import script
    create_postgresql_migration_script()
    
    print("\n📋 NEXT STEPS:")
    print("1. Go to https://neon.tech and create a free account")
    print("2. Create a new database project")
    print("3. Copy the connection string (DATABASE_URL)")
    print("4. Update your Streamlit Cloud secrets with the new DATABASE_URL")
    print("5. Deploy your app (it will create the PostgreSQL tables)")
    print("6. Run: python3 import_to_postgresql.py")
    print("7. Test your app - users should be preserved!")
    
    print(f"\n💾 Backup created with {len(backup_data['users'])} users")
    print("🔒 Your data is safe in user_data_backup.json")

if __name__ == "__main__":
    main()