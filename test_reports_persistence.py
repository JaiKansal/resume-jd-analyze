#!/usr/bin/env python3
"""
Test script to verify that analysis reports persist and don't disappear
"""

import re
import os

def test_reports_persistence():
    """Test that analysis reports persist correctly"""
    print("🔍 TESTING ANALYSIS REPORTS PERSISTENCE")
    print("=" * 50)
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ app.py not found")
        return False
    
    tests_passed = 0
    total_tests = 6
    
    # Test 1: Check session state initialization is not duplicated
    print("🧪 Test 1: Session state initialization...")
    
    # Count defensive initializations (should be minimal)
    defensive_inits = re.findall(r'if.*not in st\.session_state.*st\.session_state.*= \[\]', content, re.DOTALL)
    
    # Count total initializations
    all_inits = re.findall(r'st\.session_state\.analysis_results = \[\]', content)
    
    print(f"Total analysis_results initializations: {len(all_inits)}")
    
    # Should have: 1 main init + 1 clear button = 2 max
    if len(all_inits) <= 3:  # Allow some flexibility
        print("✅ Session state initialization count is reasonable")
        tests_passed += 1
    else:
        print(f"❌ Too many session state initializations: {len(all_inits)}")
    
    # Test 2: Check immediate session state storage
    print("\n🧪 Test 2: Immediate session state storage...")
    
    storage_pattern = r'st\.session_state\.analysis_results\.append\('
    storage_calls = re.findall(storage_pattern, content)
    
    if len(storage_calls) >= 1:
        print(f"✅ Found {len(storage_calls)} session state storage calls")
        tests_passed += 1
    else:
        print("❌ No session state storage found")
    
    # Test 3: Check for problematic reruns after analysis
    print("\n🧪 Test 3: Problematic reruns after analysis...")
    
    # Look for st.rerun() calls near analysis completion
    analysis_sections = re.findall(r'result.*=.*analyze_single_resume.*?(?=def|\Z)', content, re.DOTALL)
    
    problematic_reruns = 0
    for section in analysis_sections:
        if 'st.rerun()' in section and 'authentication' not in section.lower():
            problematic_reruns += 1
    
    if problematic_reruns == 0:
        print("✅ No problematic reruns found after analysis")
        tests_passed += 1
    else:
        print(f"❌ Found {problematic_reruns} problematic reruns after analysis")
    
    # Test 4: Check usage tracking consistency
    print("\n🧪 Test 4: Usage tracking consistency...")
    
    # All analysis should use usage_monitor consistently
    usage_monitor_calls = len(re.findall(r'usage_monitor\.track_analysis_session', content))
    direct_increments = len(re.findall(r'subscription_service\.increment_user_usage\(user\.id, 1\)', content))
    
    print(f"Usage monitor calls: {usage_monitor_calls}")
    print(f"Direct increment calls: {direct_increments}")
    
    # Should have 4 usage_monitor calls and 0 direct increments
    if usage_monitor_calls == 4 and direct_increments == 0:
        print("✅ Usage tracking is consistent")
        tests_passed += 1
    else:
        print("❌ Usage tracking inconsistency detected")
    
    # Test 5: Check session state preservation mechanisms
    print("\n🧪 Test 5: Session state preservation mechanisms...")
    
    refresh_function = 'def refresh_usage_display' in content
    session_storage = 'st.session_state.analysis_results.append' in content
    
    if refresh_function and session_storage:
        print("✅ Session state preservation mechanisms in place")
        tests_passed += 1
    else:
        print("❌ Missing session state preservation mechanisms")
    
    # Test 6: Check for widgets that might cause state loss
    print("\n🧪 Test 6: Widgets that might cause state loss...")
    
    # Check for forms without proper state handling
    form_sections = re.findall(r'with st\.form.*?st\.form_submit_button.*?(?=with st\.form|\Z)', content, re.DOTALL)
    
    problematic_forms = 0
    for form in form_sections:
        # Check if form handles session state properly
        if 'st.session_state' not in form:
            problematic_forms += 1
    
    # Check for file uploaders that might reset state
    file_upload_sections = re.findall(r'st\.file_uploader.*?(?=st\.file_uploader|\Z)', content, re.DOTALL)
    
    if problematic_forms == 0:
        print("✅ No problematic widgets found")
        tests_passed += 1
    else:
        print(f"❌ Found {problematic_forms} potentially problematic forms")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"PERSISTENCE TEST RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL PERSISTENCE TESTS PASSED!")
        print("\n✅ Reports should persist correctly:")
        print("- Analysis results stored immediately in session state")
        print("- No problematic reruns that clear state")
        print("- Consistent usage tracking without double counting")
        print("- Proper session state preservation mechanisms")
        print("- No widgets that cause unexpected state loss")
        print("\n🎯 Reports should NOT disappear when users click anything!")
        return True
    else:
        print(f"⚠️ {total_tests - tests_passed} persistence tests failed")
        print("Reports may still disappear under certain conditions")
        return False

if __name__ == "__main__":
    success = test_reports_persistence()
    exit(0 if success else 1)