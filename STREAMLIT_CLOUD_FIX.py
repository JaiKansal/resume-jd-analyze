#!/usr/bin/env python3
"""
Complete Streamlit Cloud deployment fix
Addresses all import errors and compatibility issues
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_analytics_module():
    """Ensure analytics module works on Streamlit Cloud"""
    logger.info("🔧 Fixing analytics module...")
    
    # Ensure analytics directory exists
    os.makedirs('analytics', exist_ok=True)
    
    # Create __init__.py if it doesn't exist
    if not os.path.exists('analytics/__init__.py'):
        with open('analytics/__init__.py', 'w') as f:
            f.write('"""Analytics module for Resume + JD Analyzer"""')
    
    logger.info("✅ Analytics module fixed")

def clean_python_cache():
    """Clean all Python cache files"""
    logger.info("🧹 Cleaning Python cache files...")
    
    import shutil
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                cache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(cache_path)
                    logger.info(f"Removed {cache_path}")
                except Exception as e:
                    logger.warning(f"Could not remove {cache_path}: {e}")
    
    logger.info("✅ Python cache cleaned")

def fix_requirements():
    """Ensure requirements.txt is optimized for Streamlit Cloud"""
    logger.info("📦 Fixing requirements.txt...")
    
    # Read current requirements
    with open('requirements.txt', 'r') as f:
        lines = f.readlines()
    
    # Filter out problematic packages
    clean_lines = []
    skip_packages = ['stripe', 'google-analytics', 'google-oauth2']
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            package_name = line.split('==')[0].split('>=')[0].split('<=')[0].lower()
            if not any(skip in package_name for skip in skip_packages):
                clean_lines.append(line)
            else:
                logger.info(f"Skipping problematic package: {line}")
    
    # Write cleaned requirements
    with open('requirements.txt', 'w') as f:
        for line in clean_lines:
            f.write(line + '\n')
    
    logger.info("✅ Requirements.txt cleaned")

def create_streamlit_config():
    """Create optimized Streamlit configuration"""
    logger.info("⚙️ Creating Streamlit configuration...")
    
    os.makedirs('.streamlit', exist_ok=True)
    
    config_content = """[server]
headless = true
port = $PORT
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
"""
    
    with open('.streamlit/config.toml', 'w') as f:
        f.write(config_content)
    
    logger.info("✅ Streamlit configuration created")

def fix_app_imports():
    """Fix all problematic imports in app.py"""
    logger.info("🔧 Fixing app.py imports...")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Ensure all imports are wrapped in try-except
    import_fixes = [
        ('from analytics.google_analytics import', 'try:\n    from analytics.google_analytics import'),
        ('from billing.stripe_service import', '# Stripe removed - using Razorpay only'),
        ('import stripe', '# import stripe  # Removed - using Razorpay only'),
    ]
    
    for old_import, new_import in import_fixes:
        if old_import in content and 'try:' not in content.split(old_import)[0].split('\n')[-1]:
            content = content.replace(old_import, new_import)
    
    with open('app.py', 'w') as f:
        f.write(content)
    
    logger.info("✅ App.py imports fixed")

def create_startup_script():
    """Create a startup script for Streamlit Cloud"""
    logger.info("🚀 Creating startup script...")
    
    startup_content = """#!/bin/bash
# Streamlit Cloud startup script

echo "🚀 Starting Resume + JD Analyzer..."

# Set environment variables for Streamlit Cloud
export PYTHONPATH="${PYTHONPATH}:."
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Clean any problematic cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "✅ Environment prepared"

# Start the application
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
"""
    
    with open('startup.sh', 'w') as f:
        f.write(startup_content)
    
    # Make it executable
    os.chmod('startup.sh', 0o755)
    
    logger.info("✅ Startup script created")

def verify_critical_files():
    """Verify all critical files exist and are properly configured"""
    logger.info("🔍 Verifying critical files...")
    
    critical_files = [
        'app.py',
        'requirements.txt',
        '.streamlit/secrets.toml',
        'analytics/__init__.py',
        'analytics/google_analytics.py',
        'billing/__init__.py',
        'billing/stripe_service.py',
        'database/connection.py'
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.warning(f"Missing files: {missing_files}")
        return False
    
    logger.info("✅ All critical files present")
    return True

def main():
    """Run all fixes"""
    logger.info("🚀 Starting Streamlit Cloud deployment fixes...")
    
    try:
        clean_python_cache()
        fix_analytics_module()
        fix_requirements()
        create_streamlit_config()
        fix_app_imports()
        create_startup_script()
        
        if verify_critical_files():
            logger.info("🎉 All fixes completed successfully!")
            logger.info("\n📋 What was fixed:")
            logger.info("1. ✅ Cleaned Python cache files")
            logger.info("2. ✅ Fixed analytics module imports")
            logger.info("3. ✅ Cleaned requirements.txt")
            logger.info("4. ✅ Created Streamlit configuration")
            logger.info("5. ✅ Fixed app.py imports")
            logger.info("6. ✅ Created startup script")
            logger.info("7. ✅ Verified all critical files")
            
            logger.info("\n🚀 Ready for Streamlit Cloud deployment!")
            logger.info("💡 After deployment, the app should start without import errors")
            
        else:
            logger.error("❌ Some critical files are missing")
            return False
            
    except Exception as e:
        logger.error(f"❌ Fix failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)