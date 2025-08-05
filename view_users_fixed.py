#!/usr/bin/env python3
"""
Quick and Fixed User Viewer
"""

import sqlite3
from pathlib import Path

def view_all_users():
    """View all users with correct schema"""
    db_path = 'data/app.db'
    
    if not Path(db_path).exists():
        print("❌ Database not found.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all users with correct column names
            cursor.execute("""
            SELECT id, email, first_name, last_name, company_name, phone, 
                   role, country, email_verified, is_active, created_at, updated_at
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
                print(f"   Country: {user['country'] or 'Not provided'}")
                print(f"   Email Verified: {'✅ Yes' if user['email_verified'] else '❌ No'}")
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
                    print(f"   Period: {subscription['current_period_start']} to {subscription['current_period_end']}")
                else:
                    print(f"   Plan: FREE (default)")
                
                # Get user's usage stats
                cursor.execute("""
                SELECT monthly_analysis_used
                FROM subscriptions 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """, (user['id'],))
                
                usage = cursor.fetchone()
                if usage and usage['monthly_analysis_used'] is not None:
                    print(f"   Usage: {usage['monthly_analysis_used']} analyses this month")
                else:
                    print(f"   Usage: 0 analyses")
                
                print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error reading database: {e}")

def view_database_stats():
    """View database statistics"""
    db_path = 'data/app.db'
    
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
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            active_count = cursor.fetchone()[0]
            print(f"✅ Active Users: {active_count}")
            
            # Count verified users
            cursor.execute("SELECT COUNT(*) FROM users WHERE email_verified = 1")
            verified_count = cursor.fetchone()[0]
            print(f"🔐 Verified Users: {verified_count}")
            
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
            
            # Recent activity
            cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE created_at > datetime('now', '-7 days')
            """)
            recent_users = cursor.fetchone()[0]
            print(f"\n📅 New users (last 7 days): {recent_users}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🗄️  Resume + JD Analyzer - User Viewer")
    print("=" * 50)
    
    print("\n1. All Users:")
    view_all_users()
    
    print("\n2. Database Stats:")
    view_database_stats()