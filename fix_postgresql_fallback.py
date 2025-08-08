#!/usr/bin/env python3
"""
Fix PostgreSQL service to not break when DATABASE_URL is not configured
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_registration_fallback():
    """Fix registration to use fallback when PostgreSQL is not available"""
    logger.info("🔧 Fixing registration fallback...")
    
    try:
        with open('auth/registration.py', 'r') as f:
            content = f.read()
        
        # Add fallback logic for authentication
        auth_fallback = '''
def get_auth_service():
    """Get the appropriate auth service based on configuration"""
    try:
        if postgresql_auth_service.is_postgresql:
            return postgresql_auth_service
    except:
        pass
    return user_service

# Use the fallback service
auth_service = get_auth_service()
'''
        
        # Add this after the imports
        import_end = content.find('logger = logging.getLogger(__name__)')
        if import_end != -1:
            insert_pos = content.find('\n', import_end) + 1
            content = content[:insert_pos] + auth_fallback + content[insert_pos:]
        
        # Replace direct service calls with auth_service
        content = content.replace('postgresql_auth_service.authenticate_user', 'auth_service.authenticate_user')
        content = content.replace('postgresql_auth_service.get_user_by_email', 'auth_service.get_user_by_email')
        content = content.replace('postgresql_auth_service.create_user', 'auth_service.create_user')
        
        with open('auth/registration.py', 'w') as f:
            f.write(content)
        
        logger.info("✅ Fixed registration fallback")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix registration: {e}")
        return False

def create_database_url_instructions():
    """Create instructions for setting up DATABASE_URL"""
    logger.info("🔧 Creating DATABASE_URL setup instructions...")
    
    instructions = '''# 🚨 URGENT: Set up PostgreSQL DATABASE_URL

## Current Status:
Your app is trying to use PostgreSQL but DATABASE_URL is not configured in Streamlit Cloud secrets.

## Quick Fix (2 minutes):

### Step 1: Get your Neon connection string
From your Neon dashboard (the screenshot you showed earlier):
```
postgresql://neondb_owner:[PASSWORD]@ep-square-recipe-a6tm-pooler.c2.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### Step 2: Update Streamlit Cloud Secrets
1. Go to your Streamlit Cloud app
2. Click Settings (gear icon)
3. Go to Secrets tab
4. Find the DATABASE_URL line and replace it:

```toml
DATABASE_URL = "postgresql://neondb_owner:YOUR_PASSWORD@ep-square-recipe-a6tm-pooler.c2.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

### Step 3: Save and Deploy
1. Save the secrets
2. App will redeploy automatically
3. Login with jaikansal85@gmail.com will work!

## What happens after:
- ✅ Users persist forever (no more loss on deployments)
- ✅ Login/signup works perfectly
- ✅ Production-ready user management
- ✅ Ready to sell!

## Current Fallback:
The app will use SQLite temporarily, but users will be lost on next deployment.
PostgreSQL setup is REQUIRED for production use.
'''
    
    with open('SETUP_DATABASE_URL.md', 'w') as f:
        f.write(instructions)
    
    logger.info("✅ Created DATABASE_URL setup instructions")
    return True

def main():
    """Apply fallback fixes"""
    logger.info("🚀 Applying PostgreSQL fallback fixes...")
    
    fixes = [
        ("Registration Fallback", fix_registration_fallback),
        ("DATABASE_URL Instructions", create_database_url_instructions)
    ]
    
    success_count = 0
    for fix_name, fix_func in fixes:
        logger.info(f"\n--- {fix_name} ---")
        if fix_func():
            success_count += 1
    
    logger.info(f"\n✅ Applied {success_count}/{len(fixes)} fallback fixes")
    
    if success_count == len(fixes):
        logger.info("🎉 App will now work without PostgreSQL!")
        logger.info("📋 Next steps:")
        logger.info("1. App will load with SQLite fallback")
        logger.info("2. Set up DATABASE_URL for permanent PostgreSQL")
        logger.info("3. See SETUP_DATABASE_URL.md for instructions")
    
    return success_count == len(fixes)

if __name__ == "__main__":
    main()