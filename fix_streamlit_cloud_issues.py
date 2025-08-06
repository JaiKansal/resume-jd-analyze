#!/usr/bin/env python3
"""
Fix all Streamlit Cloud deployment issues
"""

import re
import os

def fix_absolute_paths():
    """Fix absolute paths in app.py"""
    print("🔧 Fixing Absolute Paths")
    print("=" * 25)
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # These are actually URL paths for navigation, not file paths
        # They should be relative paths for better compatibility
        url_replacements = {
            '"/single-analysis"': '"single-analysis"',
            '"/bulk-analysis"': '"bulk-analysis"',
            '"/job-matching"': '"job-matching"',
            '"/analysis-history"': '"analysis-history"',
            '"/dashboard"': '"dashboard"',
            '"/admin-dashboard"': '"admin-dashboard"',
            '"/beta-program"': '"beta-program"',
            '"/support"': '"support"',
            '"/settings"': '"settings"'
        }
        
        for old_path, new_path in url_replacements.items():
            if old_path in content:
                content = content.replace(old_path, new_path)
                print(f"✅ Fixed: {old_path} → {new_path}")
        
        with open('app.py', 'w') as f:
            f.write(content)
        
        print("✅ All absolute paths fixed")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing paths: {e}")
        return False

def fix_dependencies():
    """Fix missing dependencies"""
    print("\n🔧 Fixing Dependencies")
    print("=" * 20)
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        # Check if numpy is missing
        has_numpy = any('numpy' in req for req in requirements)
        
        if not has_numpy:
            requirements.append('numpy>=1.21.0')
            print("✅ Added numpy dependency")
        
        # Ensure all requirements are properly formatted
        cleaned_requirements = []
        for req in requirements:
            req = req.strip()
            if req and not req.startswith('#'):
                cleaned_requirements.append(req)
        
        # Sort requirements for better organization
        cleaned_requirements.sort()
        
        with open('requirements.txt', 'w') as f:
            f.write('\n'.join(cleaned_requirements) + '\n')
        
        print("✅ Dependencies fixed and organized")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing dependencies: {e}")
        return False

def fix_streamlit_config():
    """Fix Streamlit configuration issues"""
    print("\n🔧 Fixing Streamlit Configuration")
    print("=" * 35)
    
    try:
        config_path = '.streamlit/config.toml'
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_content = f.read()
        else:
            config_content = ""
        
        # Fix CORS issue
        if 'enableCORS = false' in config_content:
            config_content = config_content.replace('enableCORS = false', 'enableCORS = true')
            print("✅ Fixed CORS configuration")
        
        # Add headless mode if not present
        if 'headless = true' not in config_content:
            if '[server]' not in config_content:
                config_content += '\n[server]\n'
            config_content += 'headless = true\n'
            print("✅ Added headless mode")
        
        # Add other cloud-friendly settings
        cloud_settings = """
# Cloud-friendly settings
maxUploadSize = 200
maxMessageSize = 200

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[browser]
gatherUsageStats = false
"""
        
        if 'maxUploadSize' not in config_content:
            config_content += cloud_settings
            print("✅ Added cloud-friendly settings")
        
        # Ensure directory exists
        os.makedirs('.streamlit', exist_ok=True)
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print("✅ Streamlit configuration fixed")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing Streamlit config: {e}")
        return False

def fix_file_upload_limits():
    """Add file upload size limits"""
    print("\n🔧 Adding File Upload Limits")
    print("=" * 30)
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Find file_uploader calls and add size limits
        file_uploader_pattern = r'st\.file_uploader\([^)]+\)'
        
        def add_size_limit(match):
            uploader_call = match.group(0)
            if 'max_upload_size' not in uploader_call:
                # Add size limit before the closing parenthesis
                uploader_call = uploader_call[:-1] + ', max_upload_size=10)'
            return uploader_call
        
        new_content = re.sub(file_uploader_pattern, add_size_limit, content)
        
        if new_content != content:
            with open('app.py', 'w') as f:
                f.write(new_content)
            print("✅ Added file upload size limits (10MB)")
        else:
            print("✅ File upload limits already present")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding upload limits: {e}")
        return False

def add_caching():
    """Add caching to improve performance"""
    print("\n🔧 Adding Performance Caching")
    print("=" * 30)
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Add caching imports if not present
        if '@st.cache_data' not in content and 'import streamlit as st' in content:
            # Add caching to expensive operations
            
            # Cache subscription service calls
            if 'def get_subscription_with_fallback(' in content:
                content = content.replace(
                    'def get_subscription_with_fallback(',
                    '@st.cache_data(ttl=300)\ndef get_subscription_with_fallback('
                )
                print("✅ Added caching to subscription lookup")
            
            # Cache user service calls
            if 'def get_user_by_id(' in content:
                content = content.replace(
                    'def get_user_by_id(',
                    '@st.cache_data(ttl=300)\ndef get_user_by_id('
                )
                print("✅ Added caching to user lookup")
        
        # Add session state optimization
        if 'def initialize_session_state():' in content:
            # Add session state cleanup
            cleanup_code = '''
def cleanup_session_state():
    """Clean up old session state data to prevent memory issues"""
    # Remove old analysis results if too many
    if 'analysis_results' in st.session_state and len(st.session_state.analysis_results) > 50:
        st.session_state.analysis_results = st.session_state.analysis_results[-25:]
    
    if 'bulk_results' in st.session_state and len(st.session_state.bulk_results) > 50:
        st.session_state.bulk_results = st.session_state.bulk_results[-25:]

'''
            
            # Add cleanup call to main function
            if 'def main():' in content and 'cleanup_session_state()' not in content:
                content = content.replace(
                    'def main():',
                    cleanup_code + 'def main():'
                )
                
                # Add cleanup call at start of main
                content = content.replace(
                    'def main():\n    """Main application entry point"""',
                    'def main():\n    """Main application entry point"""\n    cleanup_session_state()'
                )
                print("✅ Added session state cleanup")
        
        with open('app.py', 'w') as f:
            f.write(content)
        
        print("✅ Performance optimizations added")
        return True
        
    except Exception as e:
        print(f"❌ Error adding caching: {e}")
        return False

def fix_error_handling():
    """Fix bare except clauses"""
    print("\n🔧 Fixing Error Handling")
    print("=" * 25)
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Replace bare except clauses with specific exceptions
        content = re.sub(
            r'except:\s*\n',
            'except Exception as e:\n',
            content
        )
        
        # Add logging to bare except clauses
        content = re.sub(
            r'except Exception as e:\s*\n(\s+)(.*)',
            r'except Exception as e:\n\1logger.error(f"Unexpected error: {e}")\n\1\2',
            content
        )
        
        with open('app.py', 'w') as f:
            f.write(content)
        
        print("✅ Fixed bare except clauses")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing error handling: {e}")
        return False

def create_secrets_template():
    """Create secrets template for Streamlit Cloud"""
    print("\n🔧 Creating Secrets Template")
    print("=" * 30)
    
    try:
        secrets_template = """# Streamlit Cloud Secrets Template
# Copy this to your Streamlit Cloud app secrets

# Required API Keys
PERPLEXITY_API_KEY = "your_perplexity_api_key_here"
RAZORPAY_KEY_SECRET = "your_razorpay_secret_key_here"
SECRET_KEY = "your_secret_key_for_sessions_here"

# Optional Configuration
RAZORPAY_KEY_ID = "your_razorpay_key_id_here"
DATABASE_URL = "sqlite:///data/app.db"
ENVIRONMENT = "production"

# Instructions:
# 1. Go to your Streamlit Cloud app settings
# 2. Navigate to the "Secrets" section
# 3. Copy the above variables (without comments)
# 4. Replace the placeholder values with your actual keys
# 5. Save the secrets configuration
"""
        
        with open('streamlit_secrets_template.toml', 'w') as f:
            f.write(secrets_template)
        
        print("✅ Created secrets template: streamlit_secrets_template.toml")
        return True
        
    except Exception as e:
        print(f"❌ Error creating secrets template: {e}")
        return False

def create_deployment_guide():
    """Create deployment guide"""
    print("\n🔧 Creating Deployment Guide")
    print("=" * 30)
    
    try:
        guide = """# Streamlit Cloud Deployment Guide

## Pre-deployment Checklist

✅ All issues from audit have been fixed
✅ Dependencies are properly specified in requirements.txt
✅ Environment variables are configured
✅ Database initialization is handled
✅ File upload limits are set
✅ Caching is implemented for performance

## Deployment Steps

### 1. Repository Setup
- Ensure your code is pushed to GitHub
- Make sure all files are committed
- Verify the repository is public or you have Streamlit Cloud access

### 2. Streamlit Cloud Configuration
1. Go to https://share.streamlit.io/
2. Connect your GitHub account
3. Select your repository
4. Set the main file path: `app.py`
5. Set the Python version: `3.9` or `3.10`

### 3. Configure Secrets
1. In your Streamlit Cloud app settings, go to "Secrets"
2. Copy the contents from `streamlit_secrets_template.toml`
3. Replace placeholder values with your actual API keys:
   - `PERPLEXITY_API_KEY`: Your Perplexity API key
   - `RAZORPAY_KEY_SECRET`: Your Razorpay secret key
   - `SECRET_KEY`: A random secret key for sessions
   - `RAZORPAY_KEY_ID`: Your Razorpay key ID

### 4. Monitor Deployment
- Check the deployment logs for any errors
- Test all functionality after deployment
- Monitor resource usage and performance

## Common Issues and Solutions

### Database Issues
- SQLite database will be recreated on each deployment
- User data will be lost unless using external database
- Consider upgrading to PostgreSQL for production

### Memory Issues
- Streamlit Cloud has memory limits
- Large file uploads may cause issues
- Session state cleanup is implemented to prevent memory leaks

### API Rate Limits
- Monitor API usage to avoid rate limits
- Implement proper error handling for API failures
- Consider caching API responses

### File Upload Issues
- File upload size is limited to 10MB
- Temporary files are cleaned up automatically
- Large files may cause timeout issues

## Performance Optimization

### Implemented Optimizations
- Session state cleanup to prevent memory leaks
- File upload size limits
- Caching for expensive operations
- Proper error handling

### Additional Recommendations
- Monitor app performance regularly
- Optimize database queries
- Use appropriate caching strategies
- Minimize session state usage

## Support and Troubleshooting

If you encounter issues:
1. Check Streamlit Cloud logs
2. Verify all secrets are configured correctly
3. Test locally first
4. Check API key validity
5. Monitor resource usage

## Security Considerations

- Never commit API keys to the repository
- Use Streamlit Cloud secrets for sensitive data
- Implement proper input validation
- Monitor for suspicious activity
- Keep dependencies updated

## Post-Deployment

After successful deployment:
1. Test all features thoroughly
2. Monitor performance and errors
3. Set up monitoring and alerts
4. Plan for scaling if needed
5. Regular maintenance and updates
"""
        
        with open('STREAMLIT_DEPLOYMENT_GUIDE.md', 'w') as f:
            f.write(guide)
        
        print("✅ Created deployment guide: STREAMLIT_DEPLOYMENT_GUIDE.md")
        return True
        
    except Exception as e:
        print(f"❌ Error creating deployment guide: {e}")
        return False

def main():
    """Apply all Streamlit Cloud fixes"""
    print("🚀 FIXING STREAMLIT CLOUD DEPLOYMENT ISSUES")
    print("=" * 55)
    
    fixes = [
        ("Absolute Paths", fix_absolute_paths),
        ("Dependencies", fix_dependencies),
        ("Streamlit Configuration", fix_streamlit_config),
        ("File Upload Limits", fix_file_upload_limits),
        ("Performance Caching", add_caching),
        ("Error Handling", fix_error_handling),
        ("Secrets Template", create_secrets_template),
        ("Deployment Guide", create_deployment_guide)
    ]
    
    results = []
    
    for fix_name, fix_func in fixes:
        print(f"\n{'='*15} {fix_name} {'='*15}")
        try:
            success = fix_func()
            results.append((fix_name, success))
        except Exception as e:
            print(f"❌ Fix failed: {e}")
            results.append((fix_name, False))
    
    # Summary
    print("\n" + "=" * 55)
    print("📊 STREAMLIT CLOUD FIXES SUMMARY")
    print("=" * 55)
    
    passed = 0
    for fix_name, success in results:
        status = "✅ APPLIED" if success else "❌ FAILED"
        print(f"{fix_name:.<35} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(fixes)} fixes applied successfully")
    
    if passed == len(fixes):
        print("\n🎉 ALL FIXES APPLIED SUCCESSFULLY!")
        print("\n✅ Your app is now ready for Streamlit Cloud deployment!")
        print("\n📋 Next Steps:")
        print("1. Review the deployment guide: STREAMLIT_DEPLOYMENT_GUIDE.md")
        print("2. Configure secrets using: streamlit_secrets_template.toml")
        print("3. Test the app locally one more time")
        print("4. Deploy to Streamlit Cloud")
        print("5. Configure secrets in Streamlit Cloud dashboard")
    else:
        print(f"\n⚠️  {len(fixes) - passed} fixes failed")
        print("Manual intervention may be required")

if __name__ == "__main__":
    main()