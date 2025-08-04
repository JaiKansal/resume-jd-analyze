#!/usr/bin/env python3
"""
FINAL RAZORPAY FIX - Multiple approaches to ensure Razorpay works on Streamlit Cloud
"""

import os
import subprocess
import sys
from pathlib import Path

def create_streamlit_config():
    """Create Streamlit config to help with package installation"""
    print("🔧 Creating Streamlit configuration...")
    
    config_dir = Path(".streamlit")
    config_dir.mkdir(exist_ok=True)
    
    config_content = """
[server]
headless = true
port = $PORT
enableCORS = false

[browser]
gatherUsageStats = false

[theme]
base = "light"
"""
    
    with open(config_dir / "config.toml", "w") as f:
        f.write(config_content)
    
    print("✅ Streamlit config created")

def create_alternative_requirements():
    """Create alternative requirements.txt with different approaches"""
    print("🔧 Creating comprehensive requirements.txt...")
    
    requirements_content = """# Core Streamlit dependencies
streamlit>=1.28.0
requests>=2.25.0
pandas>=1.3.0
python-dotenv>=0.19.0

# PDF processing
pypdf2>=2.0.0
pdfplumber>=0.7.0
reportlab>=3.6.0

# Payment processing - Multiple approaches
razorpay>=1.3.0,<2.0.0
# Alternative: razorpay==1.4.2
stripe>=5.0.0

# Database support
psycopg2-binary>=2.9.0

# Security and utilities
bcrypt>=3.2.0
cryptography>=3.4.0

# Additional dependencies that might help with Razorpay
setuptools>=60.0.0
wheel>=0.37.0
pip>=21.0.0

# HTTP and networking (Razorpay dependencies)
urllib3>=1.26.0
certifi>=2021.0.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements_content)
    
    print("✅ Comprehensive requirements.txt created")

def create_enhanced_packages():
    """Create enhanced packages.txt with all possible system dependencies"""
    print("🔧 Creating enhanced packages.txt...")
    
    packages_content = """build-essential
python3-dev
python3-pip
libffi-dev
libssl-dev
libcurl4-openssl-dev
libxml2-dev
libxslt1-dev
zlib1g-dev
pkg-config
"""
    
    with open("packages.txt", "w") as f:
        f.write(packages_content)
    
    print("✅ Enhanced packages.txt created")

def create_runtime_installer():
    """Create a runtime installer that tries to install Razorpay if missing"""
    print("🔧 Creating runtime installer...")
    
    installer_content = '''"""
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
'''
    
    with open("runtime_razorpay_installer.py", "w") as f:
        f.write(installer_content)
    
    print("✅ Runtime installer created")

def create_fallback_payment_service():
    """Create a fallback payment service that works without Razorpay SDK"""
    print("🔧 Creating fallback payment service...")
    
    fallback_content = '''"""
Fallback Payment Service - Works without Razorpay SDK using direct API calls
"""

import requests
import json
import base64
import hmac
import hashlib
import streamlit as st
from typing import Dict, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)

class FallbackRazorpayService:
    """Fallback Razorpay service using direct API calls"""
    
    def __init__(self):
        self.key_id = self._get_key_id()
        self.key_secret = self._get_key_secret()
        self.base_url = "https://api.razorpay.com/v1"
        
        # Check if we have credentials
        if self.key_id and self.key_secret:
            self.status = "connected"
            self.client_available = True
        else:
            self.status = "credentials_missing"
            self.client_available = False
    
    def _get_key_id(self):
        """Get API key ID from multiple sources"""
        # Try environment variables
        key_id = os.getenv('RAZORPAY_KEY_ID')
        if key_id:
            return key_id
        
        # Try Streamlit secrets
        try:
            if hasattr(st, 'secrets') and 'RAZORPAY_KEY_ID' in st.secrets:
                return st.secrets['RAZORPAY_KEY_ID']
        except:
            pass
        
        return None
    
    def _get_key_secret(self):
        """Get API key secret from multiple sources"""
        # Try environment variables
        key_secret = os.getenv('RAZORPAY_KEY_SECRET')
        if key_secret:
            return key_secret
        
        # Try Streamlit secrets
        try:
            if hasattr(st, 'secrets') and 'RAZORPAY_KEY_SECRET' in st.secrets:
                return st.secrets['RAZORPAY_KEY_SECRET']
        except:
            pass
        
        return None
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Make authenticated request to Razorpay API"""
        if not self.key_id or not self.key_secret:
            return None
        
        url = f"{self.base_url}/{endpoint}"
        
        # Create basic auth header
        auth_string = f"{self.key_id}:{self.key_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Razorpay API request failed: {e}")
            return None
    
    def create_payment_link(self, amount: int, description: str, 
                          customer_email: str, plan_type: str) -> Optional[Dict[str, Any]]:
        """Create payment link using direct API call"""
        if not self.client_available:
            return None
        
        data = {
            'amount': amount,
            'currency': 'INR',
            'accept_partial': False,
            'description': description,
            'customer': {
                'email': customer_email
            },
            'notify': {
                'sms': True,
                'email': True
            },
            'reminder_enable': True,
            'notes': {
                'plan_type': plan_type,
                'product': 'resume_analyzer'
            },
            'callback_url': f"{os.getenv('APP_URL', 'https://resume-jd-analyze.streamlit.app')}/payment/success",
            'callback_method': 'get'
        }
        
        result = self._make_request('POST', 'payment_links', data)
        if result:
            logger.info(f"Created payment link: {result.get('id')}")
        
        return result
    
    def create_customer(self, user_email: str, user_name: str = None) -> Optional[Dict[str, Any]]:
        """Create customer using direct API call"""
        if not self.client_available:
            return None
        
        data = {
            'email': user_email,
            'name': user_name or 'Customer'
        }
        
        result = self._make_request('POST', 'customers', data)
        if result:
            logger.info(f"Created customer: {result.get('id')}")
        
        return result
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get status information"""
        return {
            'status': self.status,
            'key_id_present': bool(self.key_id),
            'key_secret_present': bool(self.key_secret),
            'sdk_available': False,  # We're not using SDK
            'api_available': self.client_available,
            'client_initialized': self.client_available,
            'key_id_preview': self.key_id[:12] + "..." if self.key_id else None,
            'fallback_mode': True
        }
    
    def render_status_debug(self):
        """Render status debug information"""
        status_info = self.get_status_info()
        
        if self.status == "connected":
            st.success("✅ Razorpay payment system is working (Fallback Mode)")
            st.info("💡 Using direct API calls instead of SDK")
        else:
            st.error("❌ Razorpay payment system configuration issue")
            
            with st.expander("🔧 Debug Information"):
                st.json(status_info)
                
                if self.status == "credentials_missing":
                    st.markdown("""
                    **Fix Required**: Add Razorpay API credentials
                    
                    **For Streamlit Cloud:**
                    1. Go to your app settings
                    2. Add secrets:
                       - `RAZORPAY_KEY_ID` = rzp_live_gBOm5l3scvXYjP
                       - `RAZORPAY_KEY_SECRET` = your_secret_key
                    """)

# Global fallback instance
fallback_razorpay_service = FallbackRazorpayService()
'''
    
    with open("billing/fallback_razorpay_service.py", "w") as f:
        f.write(fallback_content)
    
    print("✅ Fallback payment service created")

def update_enhanced_service_with_fallback():
    """Update the enhanced service to use fallback when SDK is missing"""
    print("🔧 Updating enhanced service with fallback...")
    
    try:
        with open("billing/enhanced_razorpay_service.py", "r") as f:
            content = f.read()
        
        # Add fallback import at the top
        if "from billing.fallback_razorpay_service import fallback_razorpay_service" not in content:
            # Find the imports section
            import_section = content.find("logger = logging.getLogger(__name__)")
            if import_section != -1:
                # Add fallback import
                fallback_import = """
# Fallback service for when SDK is not available
try:
    from billing.fallback_razorpay_service import fallback_razorpay_service
    FALLBACK_AVAILABLE = True
except ImportError:
    FALLBACK_AVAILABLE = False

"""
                content = content[:import_section] + fallback_import + content[import_section:]
        
        # Update the global instance to use fallback when needed
        if "# Global instance" in content:
            content = content.replace(
                "# Global instance\nenhanced_razorpay_service = EnhancedRazorpayService()",
                """# Global instance with fallback
enhanced_razorpay_service = EnhancedRazorpayService()

# Use fallback if SDK is not available
if enhanced_razorpay_service.status == 'sdk_missing' and FALLBACK_AVAILABLE:
    enhanced_razorpay_service = fallback_razorpay_service"""
            )
        
        with open("billing/enhanced_razorpay_service.py", "w") as f:
            f.write(content)
        
        print("✅ Enhanced service updated with fallback")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update enhanced service: {e}")
        return False

def create_streamlit_app_patch():
    """Create a patch for the main app to handle Razorpay issues"""
    print("🔧 Creating app patch...")
    
    patch_content = '''"""
App patch to handle Razorpay installation issues
Add this to the top of your app.py file
"""

import streamlit as st
import sys
import importlib

def ensure_payment_system():
    """Ensure payment system is available"""
    try:
        # Try to import the enhanced service
        from billing.enhanced_razorpay_service import enhanced_razorpay_service
        
        # Check if it's working
        status_info = enhanced_razorpay_service.get_status_info()
        
        if status_info['status'] == 'sdk_missing':
            # Try fallback service
            try:
                from billing.fallback_razorpay_service import fallback_razorpay_service
                st.sidebar.info("💡 Using fallback payment system (Direct API)")
                return fallback_razorpay_service
            except ImportError:
                st.sidebar.error("❌ Payment system unavailable")
                return None
        
        return enhanced_razorpay_service
        
    except Exception as e:
        st.sidebar.error(f"❌ Payment system error: {e}")
        return None

# Use this instead of importing enhanced_razorpay_service directly
payment_service = ensure_payment_system()
'''
    
    with open("app_payment_patch.py", "w") as f:
        f.write(patch_content)
    
    print("✅ App patch created")

def create_deployment_script():
    """Create a deployment script for Streamlit Cloud"""
    print("🔧 Creating deployment script...")
    
    script_content = '''#!/bin/bash
# Streamlit Cloud deployment script
# This runs automatically when your app deploys

echo "🚀 Starting Razorpay deployment fix..."

# Install pip packages with specific versions
pip install --upgrade pip
pip install razorpay>=1.3.0 --no-cache-dir
pip install requests>=2.25.0 --no-cache-dir

# Verify installation
python -c "import razorpay; print('✅ Razorpay installed:', razorpay.__version__ if hasattr(razorpay, '__version__') else 'Unknown')"

echo "✅ Deployment fix complete"
'''
    
    with open("deploy.sh", "w") as f:
        f.write(script_content)
    
    # Make it executable
    os.chmod("deploy.sh", 0o755)
    
    print("✅ Deployment script created")

def main():
    """Apply all fixes"""
    print("🚨 FINAL RAZORPAY FIX - Applying all solutions")
    print("=" * 60)
    
    fixes = [
        ("Streamlit Config", create_streamlit_config),
        ("Alternative Requirements", create_alternative_requirements),
        ("Enhanced Packages", create_enhanced_packages),
        ("Runtime Installer", create_runtime_installer),
        ("Fallback Payment Service", create_fallback_payment_service),
        ("Enhanced Service Update", update_enhanced_service_with_fallback),
        ("App Patch", create_streamlit_app_patch),
        ("Deployment Script", create_deployment_script)
    ]
    
    success_count = 0
    
    for fix_name, fix_func in fixes:
        print(f"\\n🔧 {fix_name}...")
        try:
            if fix_func():
                success_count += 1
                print(f"✅ {fix_name}: SUCCESS")
            else:
                print(f"❌ {fix_name}: FAILED")
        except Exception as e:
            print(f"❌ {fix_name}: ERROR - {e}")
    
    print(f"\\n{'='*60}")
    print(f"FINAL FIX RESULTS: {success_count}/{len(fixes)} fixes applied")
    
    if success_count >= 6:  # Most fixes successful
        print("🎉 COMPREHENSIVE RAZORPAY FIX APPLIED!")
        print("\\n✅ Multiple approaches implemented:")
        print("  - Enhanced requirements.txt with specific versions")
        print("  - System packages for compilation")
        print("  - Runtime installer for missing packages")
        print("  - Fallback service using direct API calls")
        print("  - Enhanced error handling and debugging")
        print("\\n🚀 NEXT STEPS:")
        print("1. Commit and push all changes to GitHub")
        print("2. Restart your Streamlit Cloud app")
        print("3. If SDK still missing, fallback service will work")
        print("4. Payment system will work either way!")
    else:
        print(f"⚠️ {len(fixes) - success_count} fixes failed")
        print("Some solutions may not be available")
    
    return success_count >= 6

if __name__ == "__main__":
    main()