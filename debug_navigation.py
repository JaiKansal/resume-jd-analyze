#!/usr/bin/env python3
"""
Debug navigation and authentication issues
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_session_state():
    """Debug session state"""
    st.write("## 🔍 Session State Debug")
    
    st.write("### Authentication State:")
    st.write(f"- user_authenticated: {st.session_state.get('user_authenticated', 'NOT SET')}")
    st.write(f"- current_user: {st.session_state.get('current_user', 'NOT SET')}")
    st.write(f"- user_session: {st.session_state.get('user_session', 'NOT SET')}")
    
    st.write("### All Session State Keys:")
    for key in st.session_state.keys():
        st.write(f"- {key}: {type(st.session_state[key])}")

def debug_imports():
    """Debug import issues"""
    st.write("## 📦 Import Debug")
    
    # Test auth imports
    try:
        from auth.registration import render_auth_page
        st.success("✅ auth.registration imported successfully")
    except Exception as e:
        st.error(f"❌ auth.registration import failed: {e}")
    
    # Test services
    try:
        from auth.services import user_service
        st.success("✅ auth.services imported successfully")
    except Exception as e:
        st.error(f"❌ auth.services import failed: {e}")
    
    # Test database
    try:
        from database.connection import get_db
        db = get_db()
        st.success("✅ Database connection available")
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")

def debug_authentication():
    """Debug authentication flow"""
    st.write("## 🔐 Authentication Debug")
    
    if st.button("Test Authentication Flow"):
        try:
            from auth.registration import render_auth_page
            st.write("Calling render_auth_page()...")
            result = render_auth_page()
            st.write(f"render_auth_page() returned: {result}")
        except Exception as e:
            st.error(f"Authentication flow failed: {e}")
            st.exception(e)

def main():
    st.title("🐛 Navigation Debug Tool")
    
    st.write("This tool helps debug navigation and authentication issues.")
    
    debug_session_state()
    debug_imports()
    debug_authentication()
    
    st.write("## 🔄 Actions")
    
    if st.button("Clear Session State"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Session state cleared!")
        st.rerun()
    
    if st.button("Force Authentication"):
        st.session_state.user_authenticated = True
        st.session_state.current_user = type('User', (), {
            'id': 1,
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'USER',
            'is_active': True,
            'get_full_name': lambda: 'Test User'
        })()
        st.success("Forced authentication!")
        st.rerun()

if __name__ == "__main__":
    main()