#!/usr/bin/env python3
"""
Quick User Check Script
Simple command to check users in database
"""

import sqlite3
from pathlib import Path

def quick_user_check():
    """Quick check of users in database"""
    db_path = 'data/app.db'
    
    if not Path(db_path).exists():
        print("❌ Database not found. Run the app first to create database.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get user count
            cursor.execute("SELECT COUNT(*) as count FROM users")
            count = cursor.fetchone()['count']
            
            print(f"👥 Total users in database: {count}")
            
            if count == 0:
                print("📭 No users found. Create a test user:")
                print("   python3 database/view_users.py")
                return
            
            # Get recent users
            cursor.execute("""
            SELECT email, first_name, last_name, is_active, created_at
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 5
            """)
            
            users = cursor.fetchall()
            
            print(f"\n📋 Recent users:")
            for user in users:
                status = "✅ Active" if user['is_active'] else "❌ Inactive"
                name = f"{user['first_name']} {user['last_name']}".strip() or "No name"
                print(f"   • {user['email']} ({name}) - {status}")
            
            if count > 5:
                print(f"   ... and {count - 5} more users")
            
            print(f"\n💡 For detailed view, run: python3 database/view_users.py")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_user_check()