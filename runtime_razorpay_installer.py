"""
Runtime Razorpay Installer - Installs Razorpay at runtime if missing
"""

import subprocess
import sys
import importlib
import streamlit as st

def install_razorpay():
    """Install Razorpay at runtime if not available"""
    try:
        import razorpay
        return True
    except ImportError:
        st.warning("🔧 Installing Razorpay SDK...")
        
        try:
            # Try to install Razorpay
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "razorpay>=1.3.0", "--user"
            ])
            
            # Try to import again
            importlib.invalidate_caches()
            import razorpay
            st.success("✅ Razorpay SDK installed successfully!")
            return True
            
        except Exception as e:
            st.error(f"❌ Failed to install Razorpay: {e}")
            return False

def ensure_razorpay_available():
    """Ensure Razorpay is available, install if necessary"""
    if not install_razorpay():
        st.error("❌ Razorpay SDK is not available and could not be installed")
        st.info("💡 This is likely due to Streamlit Cloud restrictions")
        return False
    return True

# Auto-run when imported
if __name__ != "__main__":
    ensure_razorpay_available()
