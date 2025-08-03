#!/usr/bin/env python3
"""
Deployment Readiness Test for Resume + JD Analyzer
Verifies all components are ready for Streamlit Cloud deployment
"""

import os
import sys
from pathlib import Path

def test_file_exists(filepath, description):
    """Test if a required file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - MISSING")
        return False

def test_import(module_name, description):
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {module_name} - {e}")
        return False

def test_requirements():
    """Test requirements.txt has all necessary dependencies"""
    required_packages = [
        'streamlit',
        'PyMuPDF',
        'requests',
        'pandas',
        'razorpay',
        'python-dotenv'
    ]
    
    if not Path('requirements.txt').exists():
        print("❌ requirements.txt not found")
        return False
    
    with open('requirements.txt', 'r') as f:
        content = f.read().lower()
    
    missing = []
    for package in required_packages:
        if package.lower() not in content:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages in requirements.txt: {missing}")
        return False
    else:
        print("✅ All required packages in requirements.txt")
        return True

def main():
    """Run all deployment readiness tests"""
    print("🚀 Resume + JD Analyzer - Deployment Readiness Test")
    print("=" * 55)
    
    tests_passed = 0
    total_tests = 0
    
    # Test required files
    files_to_test = [
        ('app.py', 'Main application file'),
        ('requirements.txt', 'Python dependencies'),
        ('.streamlit/config.toml', 'Streamlit configuration'),
        ('packages.txt', 'System packages'),
        ('streamlit_secrets_template.toml', 'Secrets template'),
        ('STREAMLIT_DEPLOYMENT_GUIDE.md', 'Deployment guide')
    ]
    
    print("\\n📁 Testing Required Files:")
    for filepath, description in files_to_test:
        if test_file_exists(filepath, description):
            tests_passed += 1
        total_tests += 1
    
    # Test Python imports
    modules_to_test = [
        ('streamlit', 'Streamlit framework'),
        ('razorpay', 'Razorpay payment gateway'),
        ('requests', 'HTTP requests library'),
        ('pandas', 'Data manipulation library')
    ]
    
    print("\\n🐍 Testing Python Imports:")
    for module, description in modules_to_test:
        if test_import(module, description):
            tests_passed += 1
        total_tests += 1
    
    # Test requirements.txt
    print("\\n📦 Testing Requirements:")
    if test_requirements():
        tests_passed += 1
    total_tests += 1
    
    # Test directory structure
    print("\\n📂 Testing Directory Structure:")
    required_dirs = [
        'resume_matcher_ai',
        'auth',
        'billing',
        'analytics',
        'support',
        'database'
    ]
    
    for dirname in required_dirs:
        if test_file_exists(dirname, f'Directory {dirname}'):
            tests_passed += 1
        total_tests += 1
    
    # Test configuration
    print("\\n⚙️  Testing Configuration:")
    try:
        from config import config
        print(f"✅ Config loaded successfully")
        print(f"   Razorpay Key ID: {config.RAZORPAY_KEY_ID[:12]}..." if config.RAZORPAY_KEY_ID else "   Razorpay Key ID: Not set")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
    total_tests += 1
    
    # Summary
    print("\\n" + "=" * 55)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("\\n🎉 ALL TESTS PASSED! Your app is ready for deployment!")
        print("\\n🚀 Next Steps:")
        print("1. Run: ./deploy_streamlit.sh")
        print("2. Push to GitHub")
        print("3. Deploy on Streamlit Cloud")
        print("4. Add your secrets")
        print("5. Go live!")
        return True
    else:
        print(f"\\n⚠️  {total_tests - tests_passed} issues need to be fixed before deployment")
        print("\\nPlease fix the issues above and run this test again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)