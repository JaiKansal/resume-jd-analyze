#!/usr/bin/env python3
"""
Fix Razorpay Streamlit secrets configuration
"""

import os
import logging

def fix_razorpay_secrets():
    """Fix Razorpay secrets configuration for Streamlit Cloud"""
    
    # Read the enhanced Razorpay service
    with open('billing/enhanced_razorpay_service.py', 'r') as f:
        content = f.read()
    
    # Add better debugging and error handling for secrets
    debug_code = '''
    def _debug_secrets_access(self):
        """Debug secrets access for troubleshooting"""
        logger.info("🔍 Debugging Razorpay secrets access...")
        
        # Check environment variables
        env_key_id = os.getenv('RAZORPAY_KEY_ID')
        env_key_secret = os.getenv('RAZORPAY_KEY_SECRET')
        logger.info(f"Environment RAZORPAY_KEY_ID: {'✅ Found' if env_key_id else '❌ Missing'}")
        logger.info(f"Environment RAZORPAY_KEY_SECRET: {'✅ Found' if env_key_secret else '❌ Missing'}")
        
        # Check Streamlit secrets
        try:
            import streamlit as st
            if hasattr(st, 'secrets'):
                secrets_key_id = st.secrets.get('RAZORPAY_KEY_ID')
                secrets_key_secret = st.secrets.get('RAZORPAY_KEY_SECRET')
                logger.info(f"Streamlit secrets RAZORPAY_KEY_ID: {'✅ Found' if secrets_key_id else '❌ Missing'}")
                logger.info(f"Streamlit secrets RAZORPAY_KEY_SECRET: {'✅ Found' if secrets_key_secret else '❌ Missing'}")
                
                # Log available secrets (without values)
                available_secrets = list(st.secrets.keys()) if hasattr(st.secrets, 'keys') else []
                logger.info(f"Available secrets: {available_secrets}")
            else:
                logger.warning("❌ st.secrets not available")
        except Exception as e:
            logger.error(f"❌ Error accessing Streamlit secrets: {e}")
    
'''
    
    # Add the debug method after the __init__ method
    init_end = content.find("    def _get_api_key_id(self)")
    if init_end > 0:
        content = content[:init_end] + debug_code + "\n    " + content[init_end:]
    
    # Update the initialize_client method to call debug
    old_init = '''    def initialize_client(self):
        """Initialize Razorpay client with multiple configuration sources"""
        # Try multiple sources for API keys
        self.key_id = self._get_api_key_id()
        self.key_secret = self._get_api_key_secret()'''
    
    new_init = '''    def initialize_client(self):
        """Initialize Razorpay client with multiple configuration sources"""
        # Debug secrets access
        self._debug_secrets_access()
        
        # Try multiple sources for API keys
        self.key_id = self._get_api_key_id()
        self.key_secret = self._get_api_key_secret()'''
    
    content = content.replace(old_init, new_init)
    
    # Add better error messages
    old_error = '''        if not self.key_id or not self.key_secret:
            logger.warning("Razorpay credentials not found in any configuration source")
            self.client = None
            self.status = "credentials_missing"'''
    
    new_error = '''        if not self.key_id or not self.key_secret:
            logger.error("❌ Razorpay credentials not found in any configuration source")
            logger.error(f"Key ID found: {'✅' if self.key_id else '❌'}")
            logger.error(f"Key Secret found: {'✅' if self.key_secret else '❌'}")
            logger.error("💡 Make sure RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET are set in Streamlit Cloud secrets")
            self.client = None
            self.status = "credentials_missing"'''
    
    content = content.replace(old_error, new_error)
    
    # Write the updated content
    with open('billing/enhanced_razorpay_service.py', 'w') as f:
        f.write(content)
    
    print("✅ Enhanced Razorpay secrets debugging")

def create_razorpay_test_script():
    """Create a test script to verify Razorpay configuration"""
    
    test_script = '''#!/usr/bin/env python3
"""
Test Razorpay configuration in Streamlit Cloud
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_razorpay_config():
    """Test Razorpay configuration"""
    logger.info("🧪 Testing Razorpay configuration...")
    
    # Test environment variables
    env_key_id = os.getenv('RAZORPAY_KEY_ID')
    env_key_secret = os.getenv('RAZORPAY_KEY_SECRET')
    
    print(f"Environment variables:")
    print(f"  RAZORPAY_KEY_ID: {'✅ Set' if env_key_id else '❌ Missing'}")
    print(f"  RAZORPAY_KEY_SECRET: {'✅ Set' if env_key_secret else '❌ Missing'}")
    
    # Test Streamlit secrets
    try:
        import streamlit as st
        print(f"\\nStreamlit secrets:")
        
        if hasattr(st, 'secrets'):
            secrets_key_id = st.secrets.get('RAZORPAY_KEY_ID')
            secrets_key_secret = st.secrets.get('RAZORPAY_KEY_SECRET')
            
            print(f"  RAZORPAY_KEY_ID: {'✅ Set' if secrets_key_id else '❌ Missing'}")
            print(f"  RAZORPAY_KEY_SECRET: {'✅ Set' if secrets_key_secret else '❌ Missing'}")
            
            # Show available secrets (without values)
            try:
                available_secrets = list(st.secrets.keys())
                print(f"  Available secrets: {available_secrets}")
            except:
                print("  Could not list available secrets")
        else:
            print("  ❌ st.secrets not available")
    except ImportError:
        print("  ❌ Streamlit not available")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test Razorpay SDK
    try:
        import razorpay
        print(f"\\nRazorpay SDK: ✅ Available")
    except ImportError:
        print(f"\\nRazorpay SDK: ❌ Not installed")
    
    # Test enhanced service
    try:
        from billing.enhanced_razorpay_service import enhanced_razorpay_service
        print(f"\\nEnhanced Razorpay Service:")
        print(f"  Status: {enhanced_razorpay_service.status}")
        print(f"  Client initialized: {'✅' if enhanced_razorpay_service.client else '❌'}")
    except Exception as e:
        print(f"\\nEnhanced Razorpay Service: ❌ Error - {e}")

if __name__ == "__main__":
    test_razorpay_config()
'''
    
    with open('test_razorpay_config.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created Razorpay test script")

if __name__ == "__main__":
    print("🚀 Fixing Razorpay Streamlit secrets configuration...")
    fix_razorpay_secrets()
    create_razorpay_test_script()
    print("🎉 Razorpay secrets fixes completed!")
    print("📋 Next steps:")
    print("1. Ensure RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET are set in Streamlit Cloud app secrets")
    print("2. Deploy and check logs for detailed debugging information")
    print("3. Run test_razorpay_config.py to verify configuration")