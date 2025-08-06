#!/usr/bin/env python3
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
