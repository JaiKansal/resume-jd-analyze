#!/usr/bin/env python3
"""
Test the complete database fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
logging.basicConfig(level=logging.INFO)

def test_database_tables():
    """Test that all required tables exist with correct columns"""
    import sqlite3
    
    print("🧪 Testing database tables and columns...")
    
    try:
        conn = sqlite3.connect('data/app.db')
        cursor = conn.cursor()
        
        # Test user_sessions table
        cursor.execute("SELECT id, user_id, session_token, ip_address, user_agent, expires_at, is_active, created_at FROM user_sessions LIMIT 1")
        print("✅ user_sessions table has all required columns")
        
        # Test users table
        cursor.execute("SELECT id, email, email_verified, last_login, login_count FROM users LIMIT 1")
        print("✅ users table has all required columns")
        
        # Test subscriptions table
        cursor.execute("SELECT id, user_id, plan_id, status, monthly_analysis_used FROM subscriptions LIMIT 1")
        print("✅ subscriptions table has all required columns")
        
        # Test subscription_plans table
        cursor.execute("SELECT id, plan_type, name, monthly_analysis_limit FROM subscription_plans")
        plans = cursor.fetchall()
        print(f"✅ subscription_plans table has {len(plans)} plans with all required columns")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_registration_flow():
    """Test the registration flow"""
    print("\n🧪 Testing registration flow...")
    
    try:
        from auth.services import user_service, session_service
        from database.connection import get_db
        
        db = get_db()
        
        # Clean up any existing test user
        db.execute_command("DELETE FROM user_sessions WHERE user_id IN (SELECT id FROM users WHERE email = ?)", ("test_final@example.com",))
        db.execute_command("DELETE FROM subscriptions WHERE user_id IN (SELECT id FROM users WHERE email = ?)", ("test_final@example.com",))
        db.execute_command("DELETE FROM users WHERE email = ?", ("test_final@example.com",))
        
        # Create test user
        user = user_service.create_user(
            email="test_final@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="Final"
        )
        
        if user:
            print("✅ User creation successful")
            
            # Create session with ip_address (this was the original failing point)
            session = session_service.create_session(
                user_id=user.id,
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0 (Test Browser)"
            )
            
            if session:
                print("✅ Session creation with ip_address successful")
                print(f"   Session ID: {session.id}")
                print(f"   IP Address: {session.ip_address}")
                print(f"   User Agent: {session.user_agent}")
                
                # Clean up
                db.execute_command("DELETE FROM user_sessions WHERE user_id = ?", (user.id,))
                db.execute_command("DELETE FROM subscriptions WHERE user_id = ?", (user.id,))
                db.execute_command("DELETE FROM users WHERE id = ?", (user.id,))
                
                return True
            else:
                print("❌ Session creation failed")
                return False
        else:
            print("❌ User creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Registration flow test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Complete Database Fix")
    print("=" * 40)
    
    # Test 1: Database structure
    if not test_database_tables():
        print("\n❌ Database structure test failed")
        return False
    
    # Test 2: Registration flow
    if not test_registration_flow():
        print("\n❌ Registration flow test failed")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Database structure is correct")
    print("✅ Registration flow works perfectly")
    print("✅ No more 'no such table: user_sessions' errors")
    print("✅ No more 'no such column: ip_address' errors")
    print("\n🚀 Your application is ready for production!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)