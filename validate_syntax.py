#!/usr/bin/env python3
"""
Validate Python syntax for all critical files
"""

import ast
import sys
import os

def validate_file(file_path):
    """Validate syntax of a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file
        ast.parse(content, file_path)
        print(f"✅ {file_path} - Syntax OK")
        return True
        
    except SyntaxError as e:
        print(f"❌ {file_path} - Syntax Error:")
        print(f"   Line {e.lineno}: {e.text.strip() if e.text else 'N/A'}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"⚠️ {file_path} - Could not validate: {e}")
        return False

def main():
    """Validate all critical Python files"""
    print("🔍 Validating Python syntax...")
    
    critical_files = [
        'app.py',
        'analytics/google_analytics.py',
        'billing/enhanced_razorpay_service.py',
        'billing/fallback_razorpay_service.py',
        'database/connection.py',
        'auth/services.py'
    ]
    
    all_valid = True
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            if not validate_file(file_path):
                all_valid = False
        else:
            print(f"⚠️ {file_path} - File not found")
    
    if all_valid:
        print("\n🎉 All files have valid syntax!")
        return True
    else:
        print("\n❌ Some files have syntax errors!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)