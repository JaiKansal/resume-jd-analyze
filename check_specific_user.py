#!/usr/bin/env python3
"""
Check for a specific user by email
"""

import sqlite3
from datetime import datetime

def check_user_by_email(email):
    """Check if a specific user exists"""
    print(f"🔍 CHECKING FOR USER: {email}")
    print("=" * 50)
    
    db_path = 'data/app.db'
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Search for the user (case insensitive)
        cursor.execute("""
            SELECT * FROM users 
            WHERE LOWER(email) = LOWER(?)
        """, (email,))
        
        user = cursor.fetchone()
        
        if user:
            print("✅ USER FOUND!")
            print(f"   📧 Email: {user['email']}")
            print(f"   👤 Name: {user['first_name']} {user['last_name']}")
            print(f"   🏢 Company: {user['company_name'] or 'Not provided'}")
            print(f"   🎭 Role: {user['role']}")
            print(f"   🌍 Country: {user['country'] or 'Not provided'}")
            print(f"   ✅ Verified: {'Yes' if user['email_verified'] else 'No'}")
            print(f"   🟢 Active: {'Yes' if user['is_active'] else 'No'}")
            print(f"   📅 Created: {user['created_at']}")
            print(f"   🆔 User ID: {user['id']}")
            
            # Check subscription
            cursor.execute("""
                SELECT s.*, sp.name as plan_name, sp.plan_type, sp.monthly_analysis_limit
                FROM subscriptions s
                LEFT JOIN subscription_plans sp ON s.plan_id = sp.id
                WHERE s.user_id = ?
                ORDER BY s.created_at DESC
                LIMIT 1
            """, (user['id'],))
            
            subscription = cursor.fetchone()
            if subscription:
                print(f"   💳 Plan: {subscription['plan_name']} ({subscription['plan_type'].upper()})")
                print(f"   📊 Status: {subscription['status']}")
                
                used = subscription['monthly_analysis_used'] or 0
                limit = subscription['monthly_analysis_limit']
                if limit == -1:
                    print(f"   🔢 Usage: {used} analyses (Unlimited)")
                else:
                    remaining = limit - used if limit else 0
                    print(f"   🔢 Usage: {used}/{limit} analyses ({remaining} remaining)")
            else:
                print(f"   💳 Plan: No subscription found")
            
            # Check for analyses
            cursor.execute("""
                SELECT COUNT(*) as count FROM analysis_sessions 
                WHERE user_id = ?
            """, (user['id'],))
            
            analysis_count = cursor.fetchone()['count']
            print(f"   📊 Analyses performed: {analysis_count}")
            
            if analysis_count > 0:
                cursor.execute("""
                    SELECT resume_filename, score, match_category, created_at
                    FROM analysis_sessions 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 3
                """, (user['id'],))
                
                analyses = cursor.fetchall()
                print(f"   📄 Recent analyses:")
                for analysis in analyses:
                    score = analysis['score'] or 'N/A'
                    category = analysis['match_category'] or 'N/A'
                    print(f"     - {analysis['resume_filename']}: {score}% ({category}) at {analysis['created_at']}")
            
            return True
            
        else:
            print("❌ USER NOT FOUND")
            
            # Search for similar emails
            cursor.execute("""
                SELECT email FROM users 
                WHERE email LIKE ?
                LIMIT 5
            """, (f"%{email.split('@')[0]}%",))
            
            similar = cursor.fetchall()
            if similar:
                print(f"\n🔍 Similar emails found:")
                for sim in similar:
                    print(f"   - {sim['email']}")
            
            # Show recent users
            cursor.execute("""
                SELECT email, first_name, last_name, created_at
                FROM users 
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            recent = cursor.fetchall()
            print(f"\n📅 Most recent users:")
            for user in recent:
                print(f"   - {user['email']} ({user['first_name']} {user['last_name']}) at {user['created_at']}")
            
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return False

def check_database_activity():
    """Check recent database activity"""
    print(f"\n🔄 RECENT DATABASE ACTIVITY")
    print("=" * 30)
    
    db_path = 'data/app.db'
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        print(f"👥 Total users in database: {total_users}")
        
        # Check users created in last hour
        cursor.execute("""
            SELECT COUNT(*) as count FROM users 
            WHERE created_at > datetime('now', '-1 hour')
        """)
        recent_users = cursor.fetchone()['count']
        print(f"🕐 Users created in last hour: {recent_users}")
        
        # Check users created in last 10 minutes
        cursor.execute("""
            SELECT COUNT(*) as count FROM users 
            WHERE created_at > datetime('now', '-10 minutes')
        """)
        very_recent_users = cursor.fetchone()['count']
        print(f"🕐 Users created in last 10 minutes: {very_recent_users}")
        
        if very_recent_users > 0:
            cursor.execute("""
                SELECT email, first_name, last_name, created_at
                FROM users 
                WHERE created_at > datetime('now', '-10 minutes')
                ORDER BY created_at DESC
            """)
            
            new_users = cursor.fetchall()
            print(f"\n✨ Very recent users:")
            for user in new_users:
                print(f"   - {user['email']} ({user['first_name']} {user['last_name']}) at {user['created_at']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database activity: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = "jaikansal85@gmail.com"
    
    check_user_by_email(email)
    check_database_activity()