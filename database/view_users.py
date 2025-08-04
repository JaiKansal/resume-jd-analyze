#!/usr/bin/env python3
"""
Database User Viewer
View all users in the database with their details
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

def view_all_users():
    """View all users in the database"""
    db_path = 'data/app.db'
    
    if not Path(db_path).exists():
        print("❌ Database not found. Make sure the app has been run at least once.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            cursor = conn.cursor()
            
            # Get all users
            cursor.execute("""
            SELECT id, email, first_name, last_name, company_name, phone, 
                   role, country, is_verified, is_active, created_at, updated_at
            FROM users 
            ORDER BY created_at DESC
            """)
            
            users = cursor.fetchall()
            
            if not users:
                print("📭 No users found in the database.")
                return
            
            print(f"👥 Found {len(users)} user(s) in the database:")
            print("=" * 80)
            
            for i, user in enumerate(users, 1):
                print(f"\n🔹 User #{i}")
                print(f"   ID: {user['id']}")
                print(f"   Email: {user['email']}")
                print(f"   Name: {user['first_name']} {user['last_name']}")
                print(f"   Company: {user['company_name'] or 'Not provided'}")
                print(f"   Phone: {user['phone'] or 'Not provided'}")
                print(f"   Role: {user['role']}")
                print(f"   Country: {user['country']}")
                print(f"   Verified: {'✅ Yes' if user['is_verified'] else '❌ No'}")
                print(f"   Active: {'✅ Yes' if user['is_active'] else '❌ No'}")
                print(f"   Created: {user['created_at']}")
                print(f"   Updated: {user['updated_at']}")
                
                # Get user's subscription info
                cursor.execute("""
                SELECT plan_type, status, current_period_start, current_period_end
                FROM subscriptions 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """, (user['id'],))
                
                subscription = cursor.fetchone()
                if subscription:
                    print(f"   Plan: {subscription['plan_type'].upper()}")
                    print(f"   Status: {subscription['status']}")
                else:
                    print(f"   Plan: FREE (default)")
                
                # Get user's usage stats
                cursor.execute("""
                SELECT analysis_count, period_start, period_end
                FROM usage_tracking 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """, (user['id'],))
                
                usage = cursor.fetchone()
                if usage:
                    print(f"   Usage: {usage['analysis_count']} analyses this period")
                else:
                    print(f"   Usage: 0 analyses")
                
                print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error reading database: {e}")

def view_user_by_email(email):
    """View specific user by email"""
    db_path = 'data/app.db'
    
    if not Path(db_path).exists():
        print("❌ Database not found.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT * FROM users WHERE email = ?
            """, (email.lower().strip(),))
            
            user = cursor.fetchone()
            
            if not user:
                print(f"❌ User with email '{email}' not found.")
                return
            
            print(f"👤 User Details for: {email}")
            print("=" * 50)
            print(f"ID: {user['id']}")
            print(f"Email: {user['email']}")
            print(f"Name: {user['first_name']} {user['last_name']}")
            print(f"Company: {user['company_name'] or 'Not provided'}")
            print(f"Phone: {user['phone'] or 'Not provided'}")
            print(f"Role: {user['role']}")
            print(f"Country: {user['country']}")
            print(f"Verified: {'✅ Yes' if user['is_verified'] else '❌ No'}")
            print(f"Active: {'✅ Yes' if user['is_active'] else '❌ No'}")
            print(f"Created: {user['created_at']}")
            print(f"Password Hash: {user['password_hash'][:20]}... (truncated for security)")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def view_database_stats():
    """View database statistics"""
    db_path = 'data/app.db'
    
    if not Path(db_path).exists():
        print("❌ Database not found.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            print("📊 Database Statistics")
            print("=" * 30)
            
            # Count users
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"👥 Total Users: {user_count}")
            
            # Count active users
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = TRUE")
            active_count = cursor.fetchone()[0]
            print(f"✅ Active Users: {active_count}")
            
            # Count verified users
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_verified = TRUE")
            verified_count = cursor.fetchone()[0]
            print(f"🔐 Verified Users: {verified_count}")
            
            # Count analysis sessions
            cursor.execute("SELECT COUNT(*) FROM analysis_sessions")
            analysis_count = cursor.fetchone()[0]
            print(f"📋 Total Analyses: {analysis_count}")
            
            # Count subscriptions
            cursor.execute("SELECT COUNT(*) FROM subscriptions")
            subscription_count = cursor.fetchone()[0]
            print(f"💳 Subscriptions: {subscription_count}")
            
            # Plan breakdown
            cursor.execute("""
            SELECT plan_type, COUNT(*) as count 
            FROM subscriptions 
            GROUP BY plan_type
            """)
            plans = cursor.fetchall()
            
            if plans:
                print("\n📈 Plan Breakdown:")
                for plan, count in plans:
                    print(f"   {plan.upper()}: {count} users")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def create_test_user():
    """Create a test user for testing"""
    db_path = 'data/app.db'
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if test user already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", ('test@example.com',))
            if cursor.fetchone():
                print("⚠️  Test user already exists: test@example.com")
                return
            
            import uuid
            import bcrypt
            
            # Create test user
            user_id = str(uuid.uuid4())
            password_hash = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
            INSERT INTO users (id, email, password_hash, first_name, last_name, 
                             company_name, role, country, is_verified, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, 'test@example.com', password_hash, 'Test', 'User',
                'Test Company', 'user', 'IN', True, True
            ))
            
            # Create subscription
            sub_id = str(uuid.uuid4())
            cursor.execute("""
            INSERT INTO subscriptions (id, user_id, plan_type, status)
            VALUES (?, ?, ?, ?)
            """, (sub_id, user_id, 'free', 'active'))
            
            # Create usage tracking
            usage_id = str(uuid.uuid4())
            cursor.execute("""
            INSERT INTO usage_tracking (id, user_id, analysis_count)
            VALUES (?, ?, ?)
            """, (usage_id, user_id, 0))
            
            conn.commit()
            
            print("✅ Test user created successfully!")
            print("   Email: test@example.com")
            print("   Password: password123")
            print("   You can now test login with these credentials.")
            
    except Exception as e:
        print(f"❌ Error creating test user: {e}")

def main():
    """Main function with menu"""
    print("🗄️  Resume + JD Analyzer - Database User Viewer")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. View all users")
        print("2. View user by email")
        print("3. View database statistics")
        print("4. Create test user")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            view_all_users()
        elif choice == '2':
            email = input("Enter email address: ").strip()
            if email:
                view_user_by_email(email)
        elif choice == '3':
            view_database_stats()
        elif choice == '4':
            create_test_user()
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()