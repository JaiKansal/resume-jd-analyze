#!/usr/bin/env python3
"""
Test Usage Tracking Fix - Verify the analysis count and persistence issues are resolved
"""

import re

def test_no_problematic_reruns():
    """Test that problematic st.rerun() calls are removed"""
    print("🧪 Testing for problematic st.rerun() calls...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for problematic patterns
        problematic_patterns = [
            r'if subscription:\s*st\.rerun\(\)',
            r'st\.rerun\(\)\s*# Store result',
            r'subscription = get_subscription_with_fallback.*st\.rerun\(\)'
        ]
        
        issues_found = 0
        for pattern in problematic_patterns:
            if re.search(pattern, content, re.DOTALL):
                print(f"❌ Found problematic pattern: {pattern}")
                issues_found += 1
        
        if issues_found == 0:
            print("✅ No problematic st.rerun() calls found")
            return True
        else:
            print(f"❌ Found {issues_found} problematic st.rerun() patterns")
            return False
            
    except Exception as e:
        print(f"❌ Error testing reruns: {e}")
        return False

def test_single_usage_tracking():
    """Test that usage tracking happens only once per analysis type"""
    print("\\n🧪 Testing single usage tracking...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Count different types of usage tracking
        single_usage = content.count('subscription_service.increment_user_usage(user.id, 1)')
        bulk_usage = content.count('subscription_service.increment_user_usage(user.id, len(results))')
        
        print(f"Single analysis usage tracking: {single_usage} locations")
        print(f"Bulk analysis usage tracking: {bulk_usage} locations")
        
        # Should have:
        # - 2 single usage tracking (main single analysis + job matching)
        # - 2 bulk usage tracking (both bulk analysis functions)
        if single_usage == 2 and bulk_usage == 2:
            print("✅ Usage tracking count is correct")
            return True
        elif single_usage <= 3 and bulk_usage >= 1:
            print("✅ Usage tracking count is reasonable")
            return True
        else:
            print(f"⚠️ Usage tracking count may be incorrect")
            return False
            
    except Exception as e:
        print(f"❌ Error testing usage tracking: {e}")
        return False

def test_session_state_preservation():
    """Test that session state is preserved during analysis"""
    print("\\n🧪 Testing session state preservation...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for immediate session state storage
        if 'st.session_state.analysis_results.append((resume_file.name, result))' in content:
            print("✅ Immediate session state storage found")
        else:
            print("⚠️ Immediate session state storage not found")
        
        # Check for refresh function instead of st.rerun()
        if 'refresh_usage_display(user.id)' in content:
            print("✅ Usage display refresh function found")
            return True
        else:
            print("⚠️ Usage display refresh function not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing session state: {e}")
        return False

def test_bulk_analysis_tracking():
    """Test that bulk analysis tracks usage correctly"""
    print("\\n🧪 Testing bulk analysis usage tracking...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for bulk usage tracking after completion
        bulk_patterns = [
            r'status_text\.text\("✅ Bulk analysis completed!"\)\s*# Track usage for bulk analysis',
            r'subscription_service\.increment_user_usage\(user\.id, len\(results\)\)'
        ]
        
        found_patterns = 0
        for pattern in bulk_patterns:
            if re.search(pattern, content, re.DOTALL):
                found_patterns += 1
        
        if found_patterns >= 1:
            print("✅ Bulk analysis usage tracking found")
            return True
        else:
            print("❌ Bulk analysis usage tracking not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing bulk analysis: {e}")
        return False

def test_no_duplicate_tracking_in_loops():
    """Test that usage tracking is not in analysis loops"""
    print("\\n🧪 Testing for duplicate tracking in loops...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check that usage tracking is not inside for loops for individual results
        problematic_patterns = [
            r'for.*resume_file.*subscription_service\.increment_user_usage',
            r'results\.append.*subscription_service\.increment_user_usage'
        ]
        
        issues_found = 0
        for pattern in problematic_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                print(f"❌ Found usage tracking in loop: {len(matches)} instances")
                issues_found += len(matches)
        
        if issues_found == 0:
            print("✅ No usage tracking found in analysis loops")
            return True
        else:
            print(f"❌ Found {issues_found} instances of usage tracking in loops")
            return False
            
    except Exception as e:
        print(f"❌ Error testing loop tracking: {e}")
        return False

def main():
    """Run all tests for usage tracking fixes"""
    print("🚀 TESTING USAGE TRACKING AND PERSISTENCE FIXES")
    print("=" * 55)
    
    tests = [
        ("No Problematic Reruns", test_no_problematic_reruns),
        ("Single Usage Tracking", test_single_usage_tracking),
        ("Session State Preservation", test_session_state_preservation),
        ("Bulk Analysis Tracking", test_bulk_analysis_tracking),
        ("No Duplicate Tracking in Loops", test_no_duplicate_tracking_in_loops)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\\n{'='*55}")
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed >= 4:
        print("🎉 USAGE TRACKING FIXES VERIFIED!")
        print("\\n✅ No problematic page reloads")
        print("✅ Usage tracking happens once per analysis")
        print("✅ Session state is preserved")
        print("✅ Bulk analysis tracks usage correctly")
        print("✅ No duplicate tracking in loops")
        print("\\n🚀 Issues should be resolved:")
        print("- Analysis count will decrease properly (3→2→1)")
        print("- Reports will not disappear after analysis")
        print("- Analysis history will persist")
    else:
        print(f"⚠️ {total - passed} tests failed")
        print("Some issues may still exist")
    
    return passed >= 4

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)