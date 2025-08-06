#!/usr/bin/env python3
"""
Fix the blank screen issue by ensuring main() is called
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_missing_main_call():
    """Add the missing main() call to app.py"""
    logger.info("🔧 Fixing missing main() call in app.py...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check if main() is already called
        if 'main()' in content and content.strip().endswith('main()'):
            logger.info("✅ main() is already called at the end of app.py")
            return True
        
        # Add main() call at the end
        if not content.strip().endswith('main()'):
            content = content.rstrip() + '\n\n# Run the main application\nmain()\n'
            
            with open('app.py', 'w') as f:
                f.write(content)
            
            logger.info("✅ Added main() call to the end of app.py")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix main() call: {e}")
        return False

def add_error_handling():
    """Add error handling to catch any startup issues"""
    logger.info("🔧 Adding error handling for startup issues...")
    
    error_handler = '''
# Error handling wrapper for main application
try:
    main()
except Exception as e:
    import streamlit as st
    st.error(f"🚨 Application Error: {e}")
    st.error("Please check the logs and try refreshing the page.")
    st.info("If the issue persists, contact support.")
    import traceback
    st.code(traceback.format_exc())
'''
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Replace simple main() call with error-handled version
        if content.strip().endswith('main()'):
            content = content.replace('\nmain()\n', error_handler)
            
            with open('app.py', 'w') as f:
                f.write(content)
            
            logger.info("✅ Added error handling wrapper")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to add error handling: {e}")
        return False

def create_minimal_test_app():
    """Create a minimal test version to verify basic functionality"""
    logger.info("🔧 Creating minimal test app...")
    
    minimal_app = '''#!/usr/bin/env python3
"""
Minimal test version of Resume + JD Analyzer
Use this to verify basic Streamlit functionality
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Page configuration
st.set_page_config(
    page_title="Resume + JD Analyzer - Test",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

def test_basic_functionality():
    """Test basic Streamlit functionality"""
    st.title("🧪 Resume + JD Analyzer - Test Mode")
    st.success("✅ Streamlit is working!")
    
    # Test environment
    st.subheader("🔍 Environment Test")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Python Version:**", sys.version)
        st.write("**Project Root:**", str(project_root))
        st.write("**Current Directory:**", os.getcwd())
    
    with col2:
        # Test secrets
        secrets_status = {}
        required_secrets = ['PERPLEXITY_API_KEY', 'RAZORPAY_KEY_ID', 'RAZORPAY_KEY_SECRET']
        
        for secret in required_secrets:
            try:
                value = st.secrets.get(secret, "NOT_SET")
                secrets_status[secret] = "✅ Set" if value != "NOT_SET" else "❌ Missing"
            except:
                secrets_status[secret] = "❌ Error"
        
        st.write("**Secrets Status:**")
        for secret, status in secrets_status.items():
            st.write(f"- {secret}: {status}")
    
    # Test database
    st.subheader("🗄️ Database Test")
    try:
        import sqlite3
        db_path = project_root / 'data' / 'app.db'
        
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            st.success(f"✅ Database found with {len(tables)} tables")
            st.write("Tables:", ", ".join(tables))
        else:
            st.warning("⚠️ Database not found - will be created on first use")
    
    except Exception as e:
        st.error(f"❌ Database test failed: {e}")
    
    # Test imports
    st.subheader("📦 Import Test")
    import_results = {}
    
    test_imports = [
        ('streamlit', 'st'),
        ('pandas', 'pd'),
        ('json', None),
        ('sqlite3', None),
        ('pathlib', 'Path')
    ]
    
    for module, alias in test_imports:
        try:
            if alias:
                exec(f"import {module} as {alias}")
            else:
                exec(f"import {module}")
            import_results[module] = "✅ Success"
        except ImportError as e:
            import_results[module] = f"❌ Failed: {e}"
    
    for module, result in import_results.items():
        st.write(f"- {module}: {result}")
    
    # Test button
    if st.button("🔄 Refresh Test"):
        st.rerun()
    
    st.info("💡 If you see this page, Streamlit is working correctly!")
    st.info("🔧 Check the main app.py file for any import or initialization errors.")

# Run the test
if __name__ == "__main__":
    test_basic_functionality()
else:
    test_basic_functionality()
'''
    
    try:
        with open('test_app.py', 'w') as f:
            f.write(minimal_app)
        
        logger.info("✅ Created test_app.py - you can deploy this to test basic functionality")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create test app: {e}")
        return False

def main():
    """Run all blank screen fixes"""
    logger.info("🚀 Fixing blank screen issue...")
    
    fixes = [
        ("Missing main() call", fix_missing_main_call),
        ("Error handling", add_error_handling),
        ("Minimal test app", create_minimal_test_app)
    ]
    
    success_count = 0
    for fix_name, fix_func in fixes:
        logger.info(f"\n--- {fix_name} ---")
        if fix_func():
            success_count += 1
    
    logger.info(f"\n✅ Applied {success_count}/{len(fixes)} fixes")
    
    if success_count == len(fixes):
        logger.info("🎉 Blank screen fixes applied!")
        logger.info("🔄 Push changes to GitHub to update Streamlit Cloud")
        logger.info("🧪 Or deploy test_app.py first to verify basic functionality")
    
    return success_count == len(fixes)

if __name__ == "__main__":
    main()