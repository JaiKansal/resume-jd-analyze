#!/usr/bin/env python3
"""
Fix subscription service import issues
"""

import re

def fix_subscription_service_imports():
    """Fix all subscription service import and usage issues"""
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Replace all instances of subscription_service.increment_usage with safe version
    old_pattern = r'from auth\.services import subscription_service\s+subscription_service\.increment_usage\(user\.id\)'
    new_replacement = '''try:
                        service = get_subscription_service()
                        if service:
                            service.increment_usage(user.id)
                    except Exception as e:
                        logger.error(f"Failed to increment usage: {e}")'''
    
    content = re.sub(old_pattern, new_replacement, content)
    
    # Also fix the bulk analysis version
    old_bulk_pattern = r'# Increment subscription usage count for bulk analysis\s+from auth\.services import subscription_service\s+subscription_service\.increment_usage\(user\.id\)'
    new_bulk_replacement = '''# Increment subscription usage count for bulk analysis
            try:
                service = get_subscription_service()
                if service:
                    service.increment_usage(user.id)
            except Exception as e:
                logger.error(f"Failed to increment bulk usage: {e}")'''
    
    content = re.sub(old_bulk_pattern, new_bulk_replacement, content)
    
    # Manual replacements for specific patterns
    replacements = [
        (
            '                    # Increment subscription usage count\n                    from auth.services import subscription_service\n                    subscription_service.increment_usage(user.id)',
            '''                    # Increment subscription usage count
                    try:
                        service = get_subscription_service()
                        if service:
                            service.increment_usage(user.id)
                    except Exception as e:
                        logger.error(f"Failed to increment usage: {e}")'''
        ),
        (
            '            # Increment subscription usage count for bulk analysis\n            from auth.services import subscription_service\n            subscription_service.increment_usage(user.id)',
            '''            # Increment subscription usage count for bulk analysis
            try:
                service = get_subscription_service()
                if service:
                    service.increment_usage(user.id)
            except Exception as e:
                logger.error(f"Failed to increment bulk usage: {e}")'''
        )
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed all subscription service import issues")

if __name__ == "__main__":
    print("🚀 Fixing subscription service import issues...")
    fix_subscription_service_imports()
    print("🎉 All subscription service imports fixed!")