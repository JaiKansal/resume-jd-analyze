#!/usr/bin/env python3
"""
Debug Streamlit Cloud environment and database connection
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_environment():
    """Debug the Streamlit Cloud environment"""
    logger.info("🔍 Debugging Streamlit Cloud environment...")
    
    # Check DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    logger.info(f"DATABASE_URL exists: {database_url is not None}")
    
    if database_url:
        # Don't log the full URL for security, just check if it's PostgreSQL
        is_postgresql = 'postgresql' in database_url.lower()
        logger.info(f"DATABASE_URL is PostgreSQL: {is_postgresql}")
        logger.info(f"DATABASE_URL starts with: {database_url[:20]}...")
    else:
        logger.error("❌ DATABASE_URL not found in environment")
    
    # Check other environment variables
    env_vars = ['PERPLEXITY_API_KEY', 'RAZORPAY_KEY_ID', 'RAZORPAY_KEY_SECRET']
    for var in env_vars:
        value = os.getenv(var)
        logger.info(f"{var} exists: {value is not None}")
    
    return database_url is not None

def test_streamlit_secrets():
    """Test if Streamlit secrets are accessible"""
    logger.info("🔍 Testing Streamlit secrets access...")
    
    try:
        import streamlit as st
        
        # Try to access secrets
        if hasattr(st, 'secrets'):
            logger.info("✅ st.secrets is available")
            
            # Check if DATABASE_URL is in secrets
            try:
                database_url = st.secrets.get('DATABASE_URL')
                if database_url:
                    logger.info("✅ DATABASE_URL found in st.secrets")
                    is_postgresql = 'postgresql' in database_url.lower()
                    logger.info(f"✅ DATABASE_URL is PostgreSQL: {is_postgresql}")
                    return True
                else:
                    logger.error("❌ DATABASE_URL not found in st.secrets")
            except Exception as e:
                logger.error(f"❌ Error accessing DATABASE_URL from secrets: {e}")
        else:
            logger.error("❌ st.secrets not available")
    
    except ImportError:
        logger.info("ℹ️ Streamlit not available (running locally)")
    except Exception as e:
        logger.error(f"❌ Error testing Streamlit secrets: {e}")
    
    return False

def create_streamlit_cloud_fix():
    """Create a fix for Streamlit Cloud environment detection"""
    logger.info("🔧 Creating Streamlit Cloud environment fix...")
    
    fix_content = '''"""
Streamlit Cloud Environment Fix
Ensures DATABASE_URL is properly detected in Streamlit Cloud
"""

import os
import logging

logger = logging.getLogger(__name__)

def get_database_url():
    """Get DATABASE_URL from environment or Streamlit secrets"""
    
    # First try environment variable
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        logger.info("✅ DATABASE_URL found in environment")
        return database_url
    
    # Try Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            database_url = st.secrets.get('DATABASE_URL')
            if database_url:
                logger.info("✅ DATABASE_URL found in Streamlit secrets")
                # Set it in environment for other modules
                os.environ['DATABASE_URL'] = database_url
                return database_url
    except:
        pass
    
    logger.warning("⚠️ DATABASE_URL not found - using SQLite fallback")
    return None

# Set DATABASE_URL if found
database_url = get_database_url()
if database_url:
    os.environ['DATABASE_URL'] = database_url
'''
    
    with open('utils/streamlit_env.py', 'w') as f:
        f.write(fix_content)
    
    logger.info("✅ Created Streamlit Cloud environment fix")
    return True

def update_app_py_for_streamlit_cloud():
    """Update app.py to use Streamlit Cloud environment fix"""
    logger.info("🔧 Updating app.py for Streamlit Cloud...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Add the environment fix import at the top
        if 'from utils.streamlit_env import' not in content:
            # Find the imports section and add our fix
            import_pos = content.find('import streamlit as st')
            if import_pos != -1:
                # Add before streamlit import
                env_import = "# Streamlit Cloud environment fix\nfrom utils.streamlit_env import get_database_url\nget_database_url()  # Ensure DATABASE_URL is set\n\n"
                content = content[:import_pos] + env_import + content[import_pos:]
        
        with open('app.py', 'w') as f:
            f.write(content)
        
        logger.info("✅ Updated app.py for Streamlit Cloud")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update app.py: {e}")
        return False

def create_utils_directory():
    """Create utils directory for helper modules"""
    import os
    os.makedirs('utils', exist_ok=True)
    
    # Create __init__.py
    with open('utils/__init__.py', 'w') as f:
        f.write('# Utils package\n')
    
    logger.info("✅ Created utils directory")
    return True

def main():
    """Debug and fix Streamlit Cloud issues"""
    logger.info("🚀 Debugging and fixing Streamlit Cloud issues...")
    
    # Debug current environment
    env_ok = debug_environment()
    secrets_ok = test_streamlit_secrets()
    
    if not env_ok and not secrets_ok:
        logger.error("❌ DATABASE_URL not accessible in any way")
        logger.info("💡 Make sure DATABASE_URL is set in Streamlit Cloud app secrets")
    
    # Apply fixes
    fixes = [
        ("Utils Directory", create_utils_directory),
        ("Streamlit Cloud Fix", create_streamlit_cloud_fix),
        ("App.py Update", update_app_py_for_streamlit_cloud)
    ]
    
    success_count = 0
    for fix_name, fix_func in fixes:
        logger.info(f"\n--- {fix_name} ---")
        if fix_func():
            success_count += 1
    
    logger.info(f"\n✅ Applied {success_count}/{len(fixes)} fixes")
    
    if success_count == len(fixes):
        logger.info("🎉 Streamlit Cloud fixes applied!")
        logger.info("🔄 Push changes and check if DATABASE_URL is detected")
    
    return success_count == len(fixes)

if __name__ == "__main__":
    main()