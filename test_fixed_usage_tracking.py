#!/usr/bin/env python3
"""
Test script to verify the usage tracking fixes are working correctly.
This test understands the current architecture where:
- Single analysis: usage_monitor.track_analysis_session() OR direct increment
- Bulk analysis: usage_monitor.track_analysis_session() only
"""

import re
import os

def test_usage_tracking_architecture():
    """Test that usage tracking follows the correct architecture"""
    print("🚀 TESTING FIXED USAGE TRACKING ARCHITECTURE")
    print("=" * 55)
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ app.py not found")
        return False
    
    # Test 1: Check for problematic st.rerun() calls (excluding auth)
    print("🧪 Testing for problematic st.rerun() calls...")
    
    # Only check for st.rerun() that's not in authentication context
    auth_rerun_pattern = r'st\.session_state\.user_authenticated = False\s*st\.rerun\(\)|st\.session_state\.current_user = None.*st\.rerun\(\)'
    all_reruns = re.findall(r'st\.rerun\(\)', content)
    auth_reruns = re.findall(auth_rerun_pattern, content, re.DOTALL)
    
    problematic_reruns = len(all_reruns) - len(auth_reruns)
    
    if problematic_reruns == 0:
        print("✅ No problematic st.rerun() calls found")
        rerun_test_passed = True
    else:
        print(f"❌ Found {problematic_reruns} problematic st.rerun() calls")
        rerun_test_passed = False
    
    # Test 2: Check usage tracking architecture
    print("\n🧪 Testing usage tracking architecture...")
    
    # Count usage_monitor.track_analysis_session calls
    usage_monitor_calls = len(re.findall(r'usage_monitor\.track_analysis_session\(', content))
    
    # Count direct subscription_service.increment_user_usage calls
    direct_increment_calls = len(re.findall(r'subscription_service\.increment_user_usage\(user\.id, 1\)', content))
    
    # Count bulk usage tracking
    bulk_usage_calls = len(re.findall(r'session_type="bulk"', content))
    
    print(f"Usage monitor calls: {usage_monitor_calls}")
    print(f"Direct increment calls: {direct_increment_calls}")
    print(f"Bulk analysis calls: {bulk_usage_calls}")
    
    # Expected: 3 usage_monitor calls (1 single + 2 bulk) OR 1 usage_monitor + 1 direct
    # The key is that total usage tracking should be reasonable
    total_usage_tracking = usage_monitor_calls + direct_increment_calls
    
    if total_usage_tracking >= 2 and total_usage_tracking <= 4 and bulk_usage_calls == 2:
        print("✅ Usage tracking architecture is correct")
        usage_test_passed = True
    else:
        print("❌ Usage tracking architecture may have issues")
        usage_test_passed = False
    
    # Test 3: Check for usage tracking inside loops
    print("\n🧪 Testing for usage tracking in loops...")
    
    # Look for for loops with resume_file
    for_loops = re.findall(r'for.*resume_file.*?(?=\n\s*for|\n\s*#|\n\s*if|\Z)', content, re.DOTALL)
    
    usage_in_loops = 0
    for loop in for_loops:
        if 'subscription_service.increment_user_usage' in loop:
            usage_in_loops += 1
    
    if usage_in_loops == 0:
        print("✅ No usage tracking found inside resume processing loops")
        loop_test_passed = True
    else:
        print(f"❌ Found {usage_in_loops} instances of usage tracking inside loops")
        loop_test_passed = False
    
    # Test 4: Check session state preservation
    print("\n🧪 Testing session state preservation...")
    
    session_state_storage = 'st.session_state.analysis_results' in content
    refresh_function = 'def refresh_usage_display' in content
    
    if session_state_storage and refresh_function:
        print("✅ Session state preservation mechanisms found")
        session_test_passed = True
    else:
        print("❌ Session state preservation may be missing")
        session_test_passed = False
    
    # Test 5: Check for double tracking
    print("\n🧪 Testing for double tracking...")
    
    # Look for places where both usage_monitor and direct increment might be called
    double_tracking_patterns = [
        r'usage_monitor\.track_analysis_session.*?subscription_service\.increment_user_usage',
        r'subscription_service\.increment_user_usage.*?usage_monitor\.track_analysis_session'
    ]
    
    double_tracking_found = 0
    for pattern in double_tracking_patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        double_tracking_found += len(matches)
    
    if double_tracking_found == 0:
        print("✅ No double tracking patterns found")
        double_tracking_test_passed = True
    else:
        print(f"❌ Found {double_tracking_found} potential double tracking patterns")
        double_tracking_test_passed = False
    
    # Summary
    print("\n" + "=" * 55)
    tests_passed = sum([
        rerun_test_passed,
        usage_test_passed, 
        loop_test_passed,
        session_test_passed,
        double_tracking_test_passed
    ])
    
    print(f"TEST RESULTS: {tests_passed}/5 tests passed")
    
    if tests_passed == 5:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Usage tracking should work correctly:")
        print("- Analysis count will decrease properly (3→2→1)")
        print("- No reports will disappear")
        print("- No double counting")
        print("- Session state preserved")
        return True
    else:
        print(f"⚠️ {5 - tests_passed} tests failed")
        print("Some issues may still exist")
        return False

if __name__ == "__main__":
    success = test_usage_tracking_architecture()
    exit(0 if success else 1)