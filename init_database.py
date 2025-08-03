#!/usr/bin/env python3
"""
Database initialization script for Resume + JD Analyzer
Sets up the database schema and creates initial data
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.connection import init_database, get_db
from auth.services import user_service, subscription_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Initialize database and create sample data"""
    print("🚀 Initializing Resume + JD Analyzer Database...")
    print("=" * 60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check database configuration
    db_type = os.getenv('DB_TYPE', 'sqlite')
    print(f"📊 Database Type: {db_type}")
    
    if db_type == 'sqlite':
        db_path = os.getenv('SQLITE_PATH', 'data/app.db')
        print(f"📁 Database Path: {db_path}")
        
        # Create data directory
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    else:
        print(f"🔗 Database Host: {os.getenv('DB_HOST', 'localhost')}")
        print(f"🗄️  Database Name: {os.getenv('DB_NAME', 'resume_analyzer')}")
    
    print("-" * 60)
    
    # Initialize database
    print("🔧 Setting up database schema...")
    if init_database():
        print("✅ Database schema created successfully!")
    else:
        print("❌ Database initialization failed!")
        return False
    
    # Verify database connection
    print("🔍 Verifying database connection...")
    try:
        db = get_db()
        with db.get_connection() as conn:
            print("✅ Database connection verified!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Check if subscription plans exist
    print("📋 Checking subscription plans...")
    plans = subscription_service.get_all_plans()
    if plans:
        print(f"✅ Found {len(plans)} subscription plans:")
        for plan in plans:
            print(f"   • {plan.name} ({plan.plan_type.value}) - ${plan.price_monthly}/month")
    else:
        print("⚠️  No subscription plans found - they should be created by schema")
    
    # Create sample admin user if in development
    if os.getenv('CREATE_ADMIN_USER', '').lower() == 'true':
        print("👤 Creating sample admin user...")
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        existing_user = user_service.get_user_by_email(admin_email)
        if not existing_user:
            admin_user = user_service.create_user(
                email=admin_email,
                password=admin_password,
                first_name="Admin",
                last_name="User",
                role="admin",
                email_verified=True
            )
            
            if admin_user:
                print(f"✅ Created admin user: {admin_email}")
            else:
                print(f"❌ Failed to create admin user")
        else:
            print(f"ℹ️  Admin user already exists: {admin_email}")
    
    print("-" * 60)
    print("🎉 Database initialization completed successfully!")
    print("\n📝 Next steps:")
    print("   1. Update your .env file with database credentials")
    print("   2. Run the application: streamlit run app.py")
    print("   3. Register your first user account")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)