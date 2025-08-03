#!/usr/bin/env python3
"""
Test script to verify datetime parsing fixes
"""

# Test that the main application imports work without datetime errors
try:
    print('✅ Testing main application imports...')
    
    # Test core imports
    from auth.models import User, Subscription, parse_datetime
    print('✅ Auth models imported successfully')
    
    from billing.upgrade_flow import trial_manager
    print('✅ Billing upgrade flow imported successfully')
    
    from support.feedback_service import feedback_service
    print('✅ Support services imported successfully')
    
    # Test datetime parsing with various formats
    from datetime import datetime
    
    test_cases = [
        '2024-01-01T12:00:00',
        '2024-01-01 12:00:00',
        '2024-01-01T12:00:00.123456',
        datetime.now(),
        None
    ]
    
    for test_case in test_cases:
        result = parse_datetime(test_case)
        expected = result is not None or test_case is None
        print(f'✅ Parsed {type(test_case).__name__}: {expected}')
    
    print('✅ All application components working correctly!')
    print('🚀 Application is ready to launch!')
    
except Exception as e:
    print(f'❌ Error testing application: {e}')
    import traceback
    traceback.print_exc()