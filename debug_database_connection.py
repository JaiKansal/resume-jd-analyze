#!/usr/bin/env python3
"""
Debug database connection issues between Streamlit and command line
"""

import os
import sqlite3
from pathlib import Path

def check_database_locations():
    """Check all possible database locations"""
    print("🔍 DEBUGGING DATABASE CONNECTION ISSUES")
    print("=" * 50)
    
    # Check current working directory
    print(f"📁 Current working directory: {os.getcwd()}")
    
    # Check for all possible database files
    possible_db_paths = [
        'data/app.db',
        'data/users.db',
        'app.db',
        'users.db',
        '/tmp/app.db',
        os.path.expanduser('~/app.db'),
        '.streamlit/app.db'
    ]
    
    found_databases = []
    
    for db_path in possible_db_paths:
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"✅ Found database: {db_path} (Size: {size} bytes)")
            found_databases.append((db_path, size))
        else:
            print(f"❌ Not found: {db_path}")
    
    return found_databases

def analyze_database_contents(db_path):
    """Analyze the contents of a database"""
    print(f"\n🔍 Analyzing database: {db_path}")
    print("=" * 40)
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📋 Tables found: {len(tables)}")
        
        for table in tables:
            table_name = table['name']
            print(f"\n📊 Table: {table_name}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            print(f"   Rows: {count}")
            
            # If it's users table, show some data
            if table_name == 'users' and count > 0:
                cursor.execute("SELECT email, first_name, last_name, created_at FROM users ORDER BY created_at DESC LIMIT 5")
                users = cursor.fetchall()
                print("   Recent users:")
                for user in users:
                    print(f"     - {user['email']} ({user['first_name']} {user['last_name']}) - {user['created_at']}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing database: {e}")
        return False

def check_streamlit_database_config():
    """Check how Streamlit is configured to use the database"""
    print(f"\n🔍 Checking Streamlit Database Configuration")
    print("=" * 45)
    
    # Check database connection configuration
    files_to_check = [
        'database/connection.py',
        'startup.py',
        'app.py',
        'config.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\n📄 Checking {file_path}:")
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Look for database path configurations
            import re
            
            # Find database paths
            db_paths = re.findall(r'["\'][^"\']*\.db["\']', content)
            if db_paths:
                print(f"   Database paths found: {db_paths}")
            
            # Find sqlite connections
            sqlite_patterns = [
                r'sqlite3\.connect\([^)]+\)',
                r'DATABASE_URL.*=.*["\'][^"\']*["\']',
                r'db_path.*=.*["\'][^"\']*["\']'
            ]
            
            for pattern in sqlite_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    print(f"   SQLite config: {matches}")

def test_database_creation_in_streamlit_context():
    """Test database creation as it would happen in Streamlit"""
    print(f"\n🧪 Testing Database Creation in Streamlit Context")
    print("=" * 50)
    
    try:
        # Import the same modules that Streamlit would use
        import sys
        sys.path.append('.')
        
        # Test startup initialization
        print("🔄 Testing startup initialization...")
        import startup
        print("✅ Startup module imported successfully")
        
        # Test database connection
        print("🔄 Testing database connection...")
        from database.connection import get_db
        db = get_db()
        print("✅ Database connection established")
        
        # Test a simple query
        print("🔄 Testing database query...")
        result = db.execute_query("SELECT COUNT(*) as count FROM users")
        user_count = result[0]['count'] if result else 0
        print(f"✅ Users in database: {user_count}")
        
        # Test user service
        print("🔄 Testing user service...")
        from auth.services import user_service
        
        # Try to get a user
        test_user = user_service.get_user_by_email("test@example.com")
        if test_user:
            print(f"✅ Found test user: {test_user.email}")
        else:
            print("⚠️  No test user found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Streamlit context test: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_test_user_in_streamlit_context():
    """Create a test user using the same context as Streamlit"""
    print(f"\n🧪 Creating Test User in Streamlit Context")
    print("=" * 45)
    
    try:
        from auth.services import user_service
        from auth.models import UserRole
        
        test_email = "streamlit_test@example.com"
        
        # Clean up existing user
        existing = user_service.get_user_by_email(test_email)
        if existing:
            print(f"⚠️  User {test_email} already exists")
            return True
        
        # Create new user
        print(f"🔄 Creating user: {test_email}")
        user = user_service.create_user(
            email=test_email,
            password="TestPassword123!",
            first_name="Streamlit",
            last_name="Test",
            role=UserRole.INDIVIDUAL
        )
        
        if user:
            print(f"✅ User created successfully: {user.id}")
            
            # Verify user was saved
            saved_user = user_service.get_user_by_email(test_email)
            if saved_user:
                print(f"✅ User verified in database: {saved_user.email}")
                return True
            else:
                print("❌ User not found after creation!")
                return False
        else:
            print("❌ User creation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_permissions():
    """Check database file permissions"""
    print(f"\n🔍 Checking Database Permissions")
    print("=" * 35)
    
    db_path = 'data/app.db'
    
    if os.path.exists(db_path):
        stat = os.stat(db_path)
        print(f"📄 Database file: {db_path}")
        print(f"   Size: {stat.st_size} bytes")
        print(f"   Permissions: {oct(stat.st_mode)[-3:]}")
        print(f"   Owner readable: {bool(stat.st_mode & 0o400)}")
        print(f"   Owner writable: {bool(stat.st_mode & 0o200)}")
        
        # Check directory permissions
        data_dir = 'data'
        if os.path.exists(data_dir):
            dir_stat = os.stat(data_dir)
            print(f"📁 Data directory: {data_dir}")
            print(f"   Permissions: {oct(dir_stat.st_mode)[-3:]}")
            print(f"   Owner writable: {bool(dir_stat.st_mode & 0o200)}")
        
        return True
    else:
        print(f"❌ Database file not found: {db_path}")
        return False

def main():
    """Run comprehensive database debugging"""
    print("🚀 COMPREHENSIVE DATABASE CONNECTION DEBUG")
    print("=" * 60)
    
    tests = [
        ("Database Locations", check_database_locations),
        ("Database Permissions", check_database_permissions),
        ("Streamlit Config", check_streamlit_database_config),
        ("Streamlit Context Test", test_database_creation_in_streamlit_context),
        ("Create Test User", create_test_user_in_streamlit_context)
    ]
    
    results = []
    found_databases = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_name == "Database Locations":
                found_databases = test_func()
                success = len(found_databases) > 0
            else:
                success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append((test_name, False))
    
    # Analyze all found databases
    if found_databases:
        for db_path, size in found_databases:
            analyze_database_contents(db_path)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DATABASE DEBUG SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:.<35} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    print(f"Databases found: {len(found_databases)}")
    
    if len(found_databases) > 1:
        print("\n⚠️  MULTIPLE DATABASES FOUND!")
        print("This is likely the cause of your issue.")
        print("Streamlit and command line are using different databases.")
        
        print("\n💡 RECOMMENDED SOLUTION:")
        print("1. Identify which database Streamlit is using")
        print("2. Consolidate all data into one database")
        print("3. Update configuration to use consistent path")
    
    elif len(found_databases) == 0:
        print("\n❌ NO DATABASES FOUND!")
        print("This explains why users aren't being saved.")
        
        print("\n💡 RECOMMENDED SOLUTION:")
        print("1. Fix database initialization")
        print("2. Ensure data directory exists and is writable")
        print("3. Test database creation manually")

if __name__ == "__main__":
    main()