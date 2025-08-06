#!/usr/bin/env python3
"""
Real-time database monitor to see changes as they happen
"""

import sqlite3
import time
import os
from datetime import datetime

def monitor_database_changes():
    """Monitor database for real-time changes"""
    print("🔄 REAL-TIME DATABASE MONITOR")
    print("=" * 40)
    print("Monitoring database for changes...")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    db_path = 'data/app.db'
    last_user_count = 0
    last_analysis_count = 0
    last_session_count = 0
    
    try:
        while True:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check users
            cursor.execute("SELECT COUNT(*) as count FROM users")
            user_count = cursor.fetchone()['count']
            
            # Check analysis sessions
            cursor.execute("SELECT COUNT(*) as count FROM analysis_sessions")
            analysis_count = cursor.fetchone()['count']
            
            # Check user sessions
            cursor.execute("SELECT COUNT(*) as count FROM user_sessions")
            session_count = cursor.fetchone()['count']
            
            # Check for changes
            changes = []
            
            if user_count != last_user_count:
                changes.append(f"👥 Users: {last_user_count} → {user_count}")
                
                # Show new users
                if user_count > last_user_count:
                    cursor.execute("""
                        SELECT email, first_name, last_name, created_at 
                        FROM users 
                        ORDER BY created_at DESC 
                        LIMIT ?
                    """, (user_count - last_user_count,))
                    
                    new_users = cursor.fetchall()
                    for user in new_users:
                        changes.append(f"   ✅ New user: {user['email']} ({user['first_name']} {user['last_name']})")
                
                last_user_count = user_count
            
            if analysis_count != last_analysis_count:
                changes.append(f"📊 Analyses: {last_analysis_count} → {analysis_count}")
                
                # Show new analyses
                if analysis_count > last_analysis_count:
                    cursor.execute("""
                        SELECT user_id, resume_filename, created_at 
                        FROM analysis_sessions 
                        ORDER BY created_at DESC 
                        LIMIT ?
                    """, (analysis_count - last_analysis_count,))
                    
                    new_analyses = cursor.fetchall()
                    for analysis in new_analyses:
                        # Get user email
                        cursor.execute("SELECT email FROM users WHERE id = ?", (analysis['user_id'],))
                        user = cursor.fetchone()
                        user_email = user['email'] if user else 'Unknown'
                        
                        changes.append(f"   📄 New analysis: {analysis['resume_filename']} by {user_email}")
                
                last_analysis_count = analysis_count
            
            if session_count != last_session_count:
                changes.append(f"🔐 Sessions: {last_session_count} → {session_count}")
                last_session_count = session_count
            
            if changes:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"\n[{timestamp}] CHANGES DETECTED:")
                for change in changes:
                    print(f"  {change}")
            else:
                # Show current status every 10 seconds
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Status: {user_count} users, {analysis_count} analyses, {session_count} sessions", end='\r')
            
            conn.close()
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print(f"\n\n✅ Monitoring stopped")
    except Exception as e:
        print(f"\n❌ Error monitoring database: {e}")

def check_analysis_storage():
    """Check analysis storage functionality"""
    print("🔍 CHECKING ANALYSIS STORAGE")
    print("=" * 35)
    
    db_path = 'data/app.db'
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check analysis_sessions table structure
        cursor.execute("PRAGMA table_info(analysis_sessions)")
        columns = cursor.fetchall()
        
        print("📋 Analysis Sessions Table Structure:")
        for col in columns:
            print(f"   - {col['name']} ({col['type']})")
        
        # Check existing analyses
        cursor.execute("SELECT COUNT(*) as count FROM analysis_sessions")
        count = cursor.fetchone()['count']
        
        print(f"\n📊 Total analyses stored: {count}")
        
        if count > 0:
            cursor.execute("""
                SELECT a.id, a.user_id, a.resume_filename, a.created_at, u.email
                FROM analysis_sessions a
                LEFT JOIN users u ON a.user_id = u.id
                ORDER BY a.created_at DESC
                LIMIT 5
            """)
            
            analyses = cursor.fetchall()
            print("\n📄 Recent analyses:")
            for analysis in analyses:
                print(f"   - {analysis['resume_filename']} by {analysis['email']} at {analysis['created_at']}")
        
        # Test analysis storage
        print(f"\n🧪 Testing analysis storage...")
        
        # Get a test user
        cursor.execute("SELECT id, email FROM users LIMIT 1")
        test_user = cursor.fetchone()
        
        if test_user:
            test_analysis_id = f"test_analysis_{int(time.time())}"
            
            cursor.execute("""
                INSERT INTO analysis_sessions 
                (id, user_id, resume_filename, job_description, analysis_result, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (
                test_analysis_id,
                test_user['id'],
                "test_resume.pdf",
                "test job description",
                "test analysis result"
            ))
            
            conn.commit()
            
            # Verify it was stored
            cursor.execute("SELECT * FROM analysis_sessions WHERE id = ?", (test_analysis_id,))
            stored_analysis = cursor.fetchone()
            
            if stored_analysis:
                print(f"✅ Analysis storage test successful!")
                print(f"   Stored analysis for user: {test_user['email']}")
                
                # Clean up test data
                cursor.execute("DELETE FROM analysis_sessions WHERE id = ?", (test_analysis_id,))
                conn.commit()
                print(f"✅ Test data cleaned up")
            else:
                print(f"❌ Analysis storage test failed!")
        else:
            print(f"❌ No users found for testing")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking analysis storage: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_current_database_status():
    """Show current database status"""
    print("📊 CURRENT DATABASE STATUS")
    print("=" * 30)
    
    db_path = 'data/app.db'
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get counts for all important tables
        tables = ['users', 'subscriptions', 'user_sessions', 'analysis_sessions']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            print(f"📋 {table}: {count} records")
        
        # Show recent activity
        print(f"\n🕒 Recent Activity:")
        
        # Recent users
        cursor.execute("""
            SELECT email, first_name, last_name, created_at 
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 3
        """)
        recent_users = cursor.fetchall()
        
        if recent_users:
            print("   Recent users:")
            for user in recent_users:
                print(f"     - {user['email']} ({user['created_at']})")
        
        # Recent analyses
        cursor.execute("""
            SELECT a.resume_filename, a.created_at, u.email
            FROM analysis_sessions a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.created_at DESC
            LIMIT 3
        """)
        recent_analyses = cursor.fetchall()
        
        if recent_analyses:
            print("   Recent analyses:")
            for analysis in recent_analyses:
                print(f"     - {analysis['resume_filename']} by {analysis['email']} ({analysis['created_at']})")
        else:
            print("   No analyses found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error getting database status: {e}")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'monitor':
        monitor_database_changes()
    else:
        show_current_database_status()
        print()
        check_analysis_storage()
        
        print(f"\n💡 To monitor real-time changes, run:")
        print(f"   python3 realtime_database_monitor.py monitor")

if __name__ == "__main__":
    main()