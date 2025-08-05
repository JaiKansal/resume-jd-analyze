#!/usr/bin/env python3
"""
Simple User Viewer - Works with actual database schema
"""

import sqlite3
from pathlib import Path

def view_users():
    """View all users with their subscription details"""
    db_path = 'data/app.db'
    
    if not Path(db_path).exists():
        print("❌ Database not found.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get users with their subscription plan details
            cursor.execute("""
            SELECT 
                u.id, u.email, u.first_name, u.last_name, u.company_name, 
                u.role, u.country, u.email_verified, u.is_active, u.created_at,
                s.status as subscription_status, s.monthly_analysis_used,
                sp.name as plan_name, sp.plan_type, sp.monthly_analysis_limit
            FROM users u
            LEFT JOIN subscriptions s ON u.id = s.user_id
            LEFT JOIN subscription_plans sp ON s.plan_id = sp.id
            ORDER BY u.created_at DESC
            """)
            
            users = cursor.fetchall()
            
            if not users:
                print("📭 No users found.")
                return
            
            print(f"👥 Found {len(users)} user(s):")
            print("=" * 80)
            
            for i, user in enumerate(users, 1):
                print(f"\n🔹 User #{i}")
                print(f"   📧 Email: {user['email']}")
                print(f"   👤 Name: {user['first_name']} {user['last_name']}")
                print(f"   🏢 Company: {user['company_name'] or 'Not provided'}")
                print(f"   🎭 Role: {user['role']}")
                print(f"   🌍 Country: {user['country'] or 'Not provided'}")
                print(f"   ✅ Verified: {'Yes' if user['email_verified'] else 'No'}")
                print(f"   🟢 Active: {'Yes' if user['is_active'] else 'No'}")
                print(f"   📅 Created: {user['created_at']}")
                
                # Subscription info
                if user['plan_name']:
                    print(f"   💳 Plan: {user['plan_name']} ({user['plan_type'].upper()})")
                    print(f"   📊 Status: {user['subscription_status']}")
                    
                    used = user['monthly_analysis_used'] or 0
                    limit = user['monthly_analysis_limit']
                    if limit == -1:
                        print(f"   🔢 Usage: {used} analyses (Unlimited)")
                    else:
                        remaining = limit - used if limit else 0
                        print(f"   🔢 Usage: {used}/{limit} analyses ({remaining} remaining)")
                else:
                    print(f"   💳 Plan: No subscription found")
                
                print("-" * 50)
            
            # Summary stats
            print(f"\n📊 Summary:")
            active_users = sum(1 for u in users if u['is_active'])
            verified_users = sum(1 for u in users if u['email_verified'])
            print(f"   Total: {len(users)} users")
            print(f"   Active: {active_users} users")
            print(f"   Verified: {verified_users} users")
            
            # Plan breakdown
            plans = {}
            for user in users:
                plan = user['plan_type'] or 'no_plan'
                plans[plan] = plans.get(plan, 0) + 1
            
            print(f"   Plans: {', '.join(f'{k.upper()}: {v}' for k, v in plans.items())}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🗄️  Resume + JD Analyzer - User Database")
    print("=" * 50)
    view_users()