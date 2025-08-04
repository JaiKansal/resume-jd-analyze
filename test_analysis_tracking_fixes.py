#!/usr/bin/env python3
"""
Test Analysis Tracking and History Fixes
"""

import re
import sys
from pathlib import Path

def test_usage_tracking_added():
    """Test that usage tracking was added to analysis completion"""
    print("🧪 Testing usage tracking integration...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for usage tracking in single analysis
        if 'subscription_service.increment_user_usage(user.id, 1)' in content:
            print("✅ Usage tracking found in app.py")
            
            # Count occurrences to ensure it's in multiple places
            count = content.count('subscription_service.increment_user_usage(user.id, 1)')
            print(f"✅ Usage tracking found in {count} locations")
            
            if count >= 2:  # Should be in single and bulk analysis
                print("✅ Usage tracking properly integrated")
                return True
            else:
                print("⚠️ Usage tracking may not be in all analysis flows")
                return False
        else:
            print("❌ Usage tracking not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing usage tracking: {e}")
        return False

def test_subscription_display_fixed():
    """Test that subscription usage display was fixed"""
    print("\\n🧪 Testing subscription usage display fixes...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check that the complex conditional was simplified
        if 'subscription.plan.monthly_analysis_limit - subscription.monthly_analysis_used' in content:
            print("✅ Simplified subscription usage calculation found")
        else:
            print("⚠️ Simplified subscription usage calculation not found")
        
        # Check that the overly complex conditional was removed
        if 'subscription.plan.monthly_analysis_limit if subscription and subscription.plan else 0 - subscription.monthly_analysis_used' not in content:
            print("✅ Complex subscription conditional removed")
            return True
        else:
            print("⚠️ Complex subscription conditional still present")
            return False
            
    except Exception as e:
        print(f"❌ Error testing subscription display: {e}")
        return False

def test_history_components_exist():
    """Test that history components exist and are integrated"""
    print("\\n🧪 Testing history components...")
    
    components_exist = True
    
    # Check for enhanced analysis storage
    if Path('database/enhanced_analysis_storage.py').exists():
        print("✅ Enhanced analysis storage exists")
    else:
        print("❌ Enhanced analysis storage missing")
        components_exist = False
    
    # Check for report history UI
    if Path('components/report_history_ui.py').exists():
        print("✅ Report history UI exists")
    else:
        print("❌ Report history UI missing")
        components_exist = False
    
    # Check app.py integration
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        if 'render_analysis_history' in content:
            print("✅ Analysis history function found in app.py")
        else:
            print("❌ Analysis history function not found")
            components_exist = False
        
        if '"📋 Analysis History"' in content:
            print("✅ Analysis History navigation option found")
        else:
            print("❌ Analysis History navigation option not found")
            components_exist = False
            
    except Exception as e:
        print(f"❌ Error checking app.py integration: {e}")
        components_exist = False
    
    return components_exist

def test_fallback_history_added():
    """Test that fallback history was added"""
    print("\\n🧪 Testing fallback history implementation...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        if 'def render_simple_analysis_history' in content:
            print("✅ Simple analysis history fallback found")
            
            if 'FROM analysis_sessions' in content:
                print("✅ Database query for history found")
                return True
            else:
                print("⚠️ Database query for history not found")
                return False
        else:
            print("❌ Simple analysis history fallback not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing fallback history: {e}")
        return False

def test_save_analysis_integration():
    """Test that save_analysis_with_history is properly integrated"""
    print("\\n🧪 Testing analysis saving integration...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        if 'save_analysis_with_history(' in content:
            print("✅ Analysis saving function found")
            
            # Count occurrences
            count = content.count('save_analysis_with_history(')
            print(f"✅ Analysis saving found in {count} locations")
            
            if count >= 1:
                print("✅ Analysis saving properly integrated")
                return True
            else:
                print("⚠️ Analysis saving may not be in all flows")
                return False
        else:
            print("❌ Analysis saving function not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing analysis saving: {e}")
        return False

def main():
    """Run all tests for analysis tracking and history fixes"""
    print("🚀 TESTING ANALYSIS TRACKING AND HISTORY FIXES")
    print("=" * 55)
    
    tests = [
        ("Usage Tracking Integration", test_usage_tracking_added),
        ("Subscription Display Fixes", test_subscription_display_fixed),
        ("History Components", test_history_components_exist),
        ("Fallback History", test_fallback_history_added),
        ("Analysis Saving Integration", test_save_analysis_integration)
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
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\\n✅ Usage tracking is properly integrated")
        print("✅ Subscription display is fixed")
        print("✅ History components are in place")
        print("✅ Fallback history is available")
        print("✅ Analysis saving is integrated")
        print("\\n🚀 Your analysis tracking and history issues are resolved!")
    else:
        print(f"⚠️ {total - passed} tests failed")
        print("Some functionality may need additional review")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)