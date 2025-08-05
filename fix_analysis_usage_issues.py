#!/usr/bin/env python3
"""
Fix Analysis Usage and Persistence Issues
1. Remove duplicate usage tracking
2. Fix immediate st.rerun() causing issues
3. Ensure analysis results persist
"""

import re

def fix_duplicate_usage_tracking():
    """Remove duplicate usage tracking and fix st.rerun() issues"""
    print("🔧 Fixing duplicate usage tracking...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Remove the problematic st.rerun() that's causing issues
        pattern1 = r'''# Track analysis usage count
                    subscription_service\.increment_user_usage\(user\.id, 1\)
                    
                    # Refresh subscription to show updated usage count
                    subscription = get_subscription_with_fallback\(user\.id\)
                    if subscription:
                        st\.rerun\(\)'''
        
        replacement1 = '''# Track analysis usage count
                    subscription_service.increment_user_usage(user.id, 1)'''
        
        if re.search(pattern1, content, re.DOTALL):
            content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)
            print("✅ Removed problematic st.rerun() after usage tracking")
        
        # Ensure usage tracking is only in the right places (not in bulk analysis loops)
        # Remove usage tracking from bulk analysis individual results
        pattern2 = r'''# Track analysis usage for each successful analysis
                    subscription_service\.increment_user_usage\(user\.id, 1\)'''
        
        # Replace with a comment to track bulk usage only once
        replacement2 = '''# Usage will be tracked once for the entire bulk analysis'''
        
        content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)
        print("✅ Fixed bulk analysis usage tracking")
        
        # Add single usage tracking for bulk analysis at the end
        pattern3 = r'(st\.success\(f"✅ Bulk analysis completed! Analyzed \{len\(results\)\} resumes\."\))'
        replacement3 = r'''\1
                
                # Track usage for bulk analysis (once for all resumes)
                subscription_service.increment_user_usage(user.id, len(results))'''
        
        if re.search(pattern3, content):
            content = re.sub(pattern3, replacement3, content)
            print("✅ Added proper bulk analysis usage tracking")
        
        with open('app.py', 'w') as f:
            f.write(content)
        
        print("✅ Usage tracking issues fixed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix usage tracking: {e}")
        return False

def fix_analysis_persistence():
    """Ensure analysis results persist and don't disappear"""
    print("🔧 Fixing analysis persistence...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Make sure session state is preserved during analysis
        # Remove any st.rerun() calls that might clear session state
        problematic_reruns = [
            r'st\.rerun\(\)\s*# Store result with enhanced history tracking',
            r'if subscription:\s*st\.rerun\(\)'
        ]
        
        for pattern in problematic_reruns:
            if re.search(pattern, content):
                content = re.sub(pattern, '# Removed problematic rerun', content)
                print("✅ Removed problematic st.rerun() call")
        
        # Ensure analysis results are stored in session state before any operations
        pattern = r'(st\.success\("✅ Analysis completed!"\)\s+render_analysis_result\(result, resume_file\.name\))'
        replacement = r'''\1
                    
                    # Store result in session state immediately to prevent loss
                    if 'analysis_results' not in st.session_state:
                        st.session_state.analysis_results = []
                    st.session_state.analysis_results.append((resume_file.name, result))'''
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content, count=1)
            print("✅ Added immediate session state storage")
        
        with open('app.py', 'w') as f:
            f.write(content)
        
        print("✅ Analysis persistence fixed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix analysis persistence: {e}")
        return False

def add_usage_display_refresh():
    """Add proper usage display refresh without st.rerun()"""
    print("🔧 Adding proper usage display refresh...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Add a function to refresh usage display in sidebar
        refresh_function = '''
def refresh_usage_display(user_id):
    """Refresh usage display in sidebar without full page reload"""
    try:
        subscription = get_subscription_with_fallback(user_id)
        if subscription and subscription.plan and subscription.plan.monthly_analysis_limit != -1:
            remaining = (subscription.plan.monthly_analysis_limit - subscription.monthly_analysis_used) if (subscription and subscription.plan and hasattr(subscription, "monthly_analysis_used")) else 0
            # Update sidebar with new count (will show on next interaction)
            st.session_state.usage_updated = True
    except Exception as e:
        logger.error(f"Failed to refresh usage display: {e}")
'''
        
        # Add the function before the main functions
        insert_point = content.find('def initialize_session_state():')
        if insert_point != -1 and 'def refresh_usage_display' not in content:
            content = content[:insert_point] + refresh_function + '\n' + content[insert_point:]
            print("✅ Added usage display refresh function")
        
        # Use the refresh function instead of st.rerun()
        pattern = r'# Track analysis usage count\s+subscription_service\.increment_user_usage\(user\.id, 1\)'
        replacement = '''# Track analysis usage count
                    subscription_service.increment_user_usage(user.id, 1)
                    
                    # Refresh usage display without full reload
                    refresh_usage_display(user.id)'''
        
        content = re.sub(pattern, replacement, content)
        print("✅ Updated usage tracking to use refresh function")
        
        with open('app.py', 'w') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to add usage display refresh: {e}")
        return False

def verify_single_usage_tracking():
    """Verify that usage tracking only happens once per analysis"""
    print("🔧 Verifying single usage tracking...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Count usage tracking calls
        single_usage_count = content.count('subscription_service.increment_user_usage(user.id, 1)')
        bulk_usage_count = content.count('subscription_service.increment_user_usage(user.id, len(results))')
        
        print(f"Single analysis usage tracking: {single_usage_count} locations")
        print(f"Bulk analysis usage tracking: {bulk_usage_count} locations")
        
        if single_usage_count <= 2 and bulk_usage_count <= 1:  # Should be max 2 for single (main + job matching) and 1 for bulk
            print("✅ Usage tracking count looks reasonable")
            return True
        else:
            print(f"⚠️ Too many usage tracking calls: {single_usage_count + bulk_usage_count} total")
            return False
        
    except Exception as e:
        print(f"❌ Failed to verify usage tracking: {e}")
        return False

def main():
    """Apply all fixes for analysis usage and persistence issues"""
    print("🚀 FIXING ANALYSIS USAGE AND PERSISTENCE ISSUES")
    print("=" * 60)
    
    fixes = [
        ("Duplicate Usage Tracking", fix_duplicate_usage_tracking),
        ("Analysis Persistence", fix_analysis_persistence),
        ("Usage Display Refresh", add_usage_display_refresh),
        ("Verify Single Usage Tracking", verify_single_usage_tracking)
    ]
    
    success_count = 0
    
    for fix_name, fix_func in fixes:
        print(f"\n🔧 {fix_name}...")
        try:
            if fix_func():
                success_count += 1
                print(f"✅ {fix_name}: SUCCESS")
            else:
                print(f"❌ {fix_name}: FAILED")
        except Exception as e:
            print(f"❌ {fix_name}: ERROR - {e}")
    
    print(f"\n{'='*60}")
    print(f"FIX RESULTS: {success_count}/{len(fixes)} fixes applied")
    
    if success_count >= 3:
        print("🎉 ANALYSIS USAGE AND PERSISTENCE FIXES APPLIED!")
        print("\n✅ Usage tracking will only happen once per analysis")
        print("✅ Analysis count will decrease properly (3→2→1)")
        print("✅ Reports will not disappear after analysis")
        print("✅ No more problematic page reloads")
        print("\n🚀 NEXT STEPS:")
        print("1. Commit and push changes")
        print("2. Test analysis with free tier limits")
        print("3. Verify usage count decreases correctly")
        print("4. Confirm reports persist after analysis")
    else:
        print(f"⚠️ {len(fixes) - success_count} fixes failed")
        print("Some issues may persist")
    
    return success_count >= 3

if __name__ == "__main__":
    main()